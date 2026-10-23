# 临时文件传送：服务器端部署

> 目标机：62.234.28.97（Ubuntu 24.04）
> 最近更新：2026-10-24

## 架构

```
                    ┌─────────────── Cloudflare 边缘 ───────────────┐
   浏览器 (https)  ──┤  jet-kde-beer-petersburg.trycloudflare.com   │
                    └────────────────────┬──────────────────────────┘
                                         │ 隧道（服务器主动外连）
                                         ▼
                              本机 nginx :25446
                              ├─ /            → 页面静态文件
                              ├─ /peerjs      → 25443（信令，TLS）
                              ├─ /config.json → 25445（实时配置）
                              └─ /signal.json → 静态快照
```

## 服务清单

| systemd 单元 | 端口 | 作用 |
| --- | --- | --- |
| `wptransfer-signal` | 25443 | PeerJS 信令（TLS，自签证书） |
| `wptransfer-signal-ws` | 25444 | PeerJS 信令（明文，http 页面用） |
| `wptransfer-tunnel` | 出站 | cloudflared 隧道 → 25446 |
| `wptransfer-config` | 25445 | 动态配置接口（实时读隧道域名） |
| `wptransfer-watch` | — | 监测域名变化并更新 config.json |
| `coturn` | 25347 udp/tcp | TURN 中继，中继端口 25500-25899 |
| `nginx` | 80 / 25446 | ACME（已失效）/ 统一入口 |

TURN 凭据（明文在前端，见 `transfer/index.html` 的 `TURN` 常量）：

- 用户名 `wp47b9d28d`
- 密码 `cyi7ozAPIkacFrzK7MK73nVcYxC6`

## 为什么绕这么大一圈

这台机器有两个死结，我都验证过：

### 死结 1：443 端口被云安全组封死

无论本机是否监听，外部始终连不上。**所有标准 HTTPS/WSS 方案、TLS-ALPN-01 验证全部不可用。**

### 死结 2：80 端口有 ICP 备案拦截

`Host` 头是**任何域名**的请求都会被 302 到 `dnspod.qcloud.com/static/webblock.html`。
`Host` 是 IP 时不拦，所以本机自测都正常、看起来没问题。

**但 Let's Encrypt 从境外验证时仍然失败**（`reader size limit exceeded`）：

- 服务器访问日志证明 CA 拿到了正确的 200 + 正确字节数
- 换 nginx、换最小 Python 服务、加 `Connection: close` —— 结果完全相同
- 结论：腾讯云在北上链路对境外请求做了注入，服务器侧无法规避

**所以：这台机器签不出受信任证书，除非有已备案域名。**

### 解法：Cloudflare 隧道

隧道是服务器**主动出站**连到 Cloudflare，不经过本机 443/80：

- 证书由 Google Trust Services 签发，浏览器直接信任
- 不受备案拦截影响
- 不需要域名、不需要账号（quick tunnel）

```
$ curl -sS https://<tunnel>.trycloudflare.com/peerjs/id -w '\ncode=%{http_code}\n'
a1b2c3d4-...
code=200
```

## 已知限制

### quick tunnel 域名会变

重启 `wptransfer-tunnel` 后域名必然改变。应对措施：

1. `wptransfer-watch` 每 30 秒检查，域名变了就更新 `/var/www/transfer/config.json`
2. 页面端按 `?signal=` → 同源 `config.json` → `signal.json` → `/config.json` → localStorage 依次回退
3. GitHub Pages 上的 `transfer/config.json` 需要重新生成并提交（见下）

**要彻底固定**，需要 Cloudflare 账号 + 一个域名做 named tunnel。免费额度足够。

### TURN 凭据暴露

TURN 用户名密码明文写在前端，任何人拿到页面都能免费用中继带宽。
已设 `total-quota=100`（并发），但**没设带宽上限**。

建议改成 TURN REST API（`--use-auth-secret`）用时效凭据，或加云侧流量告警。

## 运维

```bash
# 一键自检
sudo /opt/wptransfer/status.sh

# 服务状态
sudo systemctl status wptransfer-signal wptransfer-signal-ws \
  wptransfer-tunnel wptransfer-config wptransfer-watch coturn

# 看当前隧道域名
sudo grep -oE '[a-z0-9-]+\.trycloudflare\.com' /var/log/wptransfer-tunnel.log | tail -1

# 更新 GitHub Pages 上的静态快照（域名变了以后）
sudo cat /var/www/transfer/config.json   # 拷到 transfer/config.json 再提交
```

## 换真证书（拿到域名后）

```bash
sudo certbot certonly --manual --preferred-challenges dns -d your.domain
sudo cp /etc/letsencrypt/live/your.domain/fullchain.pem /etc/ssl/wptransfer/fullchain.pem
sudo cp /etc/letsencrypt/live/your.domain/privkey.pem   /etc/ssl/wptransfer/key.pem
sudo systemctl restart wptransfer-signal
```

然后在 `transfer/config.json` 里把 host 改成该域名即可，隧道可以停掉。
