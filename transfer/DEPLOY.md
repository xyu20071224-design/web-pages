# 临时文件传送：服务器端部署

> 目标机：62.234.28.97（Ubuntu 24.04，2C/3.6G）
> 部署日期：2026-10-24

## 已部署的服务

| 服务 | 端口 | 说明 |
| --- | --- | --- |
| PeerJS 信令（TLS） | 25443 | 自签证书，systemd: `wptransfer-signal` |
| PeerJS 信令（明文） | 25444 | http 页面用，systemd: `wptransfer-signal-ws` |
| coturn TURN | 25347 udp/tcp | 中继端口 25500-25899，systemd: `coturn` |
| nginx | 80 | 仅用于 ACME 验证（当前失效，见下） |

TURN 凭据（写死在 transfer/index.html 的 TURN 常量里）：

- 用户名：`wp47b9d28d`
- 密码：`cyi7ozAPIkacFrzK7MK73nVcYxC6`

## 关键约束（踩过的坑）

### 1. 443 端口被云安全组封死

外层探测 443 始终不通，即使本机有监听。**所有依赖 443 的方案（HTTPS/WSS 标准端口、TLS-ALPN-01 验证）都不可用。**

### 2. 80 端口有备案拦截

凡是 `Host` 头是**域名**的请求，一律 302 到 `dnspod.qcloud.com/static/webblock.html`。
`Host` 是 IP 时不拦（所以 `curl http://62.234.28.97/` 正常）。

**但 Let's Encrypt 从境外验证时仍然失败**，报 `reader size limit exceeded`：

- 服务器侧访问日志显示 CA 拿到了正确的 200 + 131 字节
- 换 nginx / 最小 Python 服务都一样
- 说明是腾讯云在**北上链路**对境外请求做了注入，服务器侧无法规避

结论：**这台机器上签不出受信任证书**，除非有已备案域名。

### 3. 非标端口不受备案拦截

25443 上跑 TLS，`Host` 是域名也正常返回。所以只要证书可信，WSS 就能用。

## 当前状态与页面行为

- **http 页面** → `ws://62.234.28.97:25444`：✅ 已验证可用
- **https 页面**（GitHub Pages）→ `wss://62.234.28.97:25443`：❌ 自签证书被浏览器拒绝

页面里 `pickSignal()` 按 `location.protocol` 自动选择，无需手工改。

## 怎么修好 https 场景

拿到**任意一个能加 TXT 记录的域名**后：

```bash
# 1. DNS-01 签发（不需要 80/443，绕开备案）
sudo apt install -y certbot
sudo certbot certonly --manual --preferred-challenges dns -d your.domain

# 2. 换掉自签证书
sudo cp /etc/letsencrypt/live/your.domain/fullchain.pem /etc/ssl/wptransfer/fullchain.pem
sudo cp /etc/letsencrypt/live/your.domain/privkey.pem   /etc/ssl/wptransfer/key.pem
sudo systemctl restart wptransfer-signal
```

然后改 `transfer/index.html` 的 `pickSignal()`，把 host 换成该域名即可。

## 常用运维命令

```bash
sudo systemctl status wptransfer-signal wptransfer-signal-ws coturn
sudo journalctl -u wptransfer-signal -f
sudo tail -f /var/log/turnserver.log
sudo turnutils_uclient -u wp47b9d28d -w cyi7ozAPIkacFrzK7MK73nVcYxC6 -p 25347 62.234.28.97
```

## 安全提醒

- TURN 凭据是**明文写在前端**的，任何人拿到页面都能免费用你的中继带宽。
- 已设 `total-quota=100` 限制并发，但带宽没有上限（`bps-capacity` 未设）。
- 建议后续改成 TURN REST API（`--use-auth-secret`）用时效性凭据，或在云侧加流量告警。
