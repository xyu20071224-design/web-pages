# agent.md

给接手这个仓库的 AI（或人）看的施工说明。这个项目**没有构建系统、没有测试、没有 CI**：改完 push 到 `main` 就等于发布。下面这些是本仓库特有的约定，不是通用最佳实践。

---

## 1. 基本盘

| 项 | 值 |
| --- | --- |
| 仓库（公开） | https://github.com/xyu20071224-design/web-pages |
| 线上站点 | https://xyu20071224-design.github.io/web-pages/ |
| 默认分支 / 发布源 | `main` 分支**根目录**（GitHub Pages legacy 构建，HTTPS 已强制） |
| 发布方式 | `git push` 后约 1 分钟自动生效，**没有任何构建 / 编译 / 部署命令** |
| 技术栈 | 纯静态 HTML + 内联 CSS/JS；唯一的第三方运行时是 `laiyipan/` 里打包好的 Phaser |
| 规模 | 43 个 HTML；仓库约 21 MB（大头是 `laiyipan/` 的图片与音频） |

## 2. 目录职责

| 路径 | 是什么 | 备注 |
| --- | --- | --- |
| `index.html` | 落地页，5 张卡片入口 | 纯手写 HTML |
| `ics/index.html` | ICS 二级入口页（课件 / 实验 / 视觉风格三个网格） | 新增讲次要改这里 |
| `ics/*.html` | 《计算机系统导论》5 讲主页面 + Data Lab 实验台 | 见 §4 |
| `ics/variants*/` | 每讲的 4 种视觉风格副本 + 预览页 | 见 §4，整页副本 |
| `gitlearn/` | Git 学习模拟器（单文件，9 章） | 见 §5 |
| `shelllearn/` | 命令行学习模拟器（单文件，18 章） | 见 §5 |
| `laiyipan/` | Phaser 小游戏「来一盘吗？」 | **只有构建产物，源码不在仓库**，见 §6 |
| `qinshihuang/` | 「始皇北巡」单页作品（2 个 HTML） | 见 §7 |
| `README.md` | 面向人的说明 | 目录结构 / 预览 / 发布方式变了要同步更新 |
| `agent.md` | 本文件 | 约定变了就更新 |

## 3. 本地预览与发布

```bash
# 预览（在仓库根目录执行；不要直接双击 HTML 打开，相对路径和 iframe 依赖 HTTP 服务）
python3 -m http.server 8000        # 然后打开 http://localhost:8000/

# 发布（只推 main，没有 PR 流程）
git add -A && git commit -m "…" && git push origin main
```

发布后核对线上：

```bash
curl -sS -o /dev/null -w "%{http_code}\n" -L https://xyu20071224-design.github.io/web-pages/
# 期望 200；再抽查刚改的那个页面路径
```

## 4. ICS 课件：整页复制 × 4 种风格（最容易踩的坑）

### 结构

每讲 = 1 个主页面 + 1 个风格画廊目录：

| 讲次 | 主页面（原版「清爽蓝」） | 风格画廊目录 |
| --- | --- | --- |
| 第 1 讲 · 课程概述 | `ics/ics01-zh.html` | `ics/variants-ics01/` |
| 第 2 讲 · 位、字节与整数 | `ics/bits-bytes-ints-zh.html` | `ics/variants-bits/` |
| 第 3 讲 · 浮点数 | `ics/floating-point-zh.html` | `ics/variants/` |
| 第 4 讲 · 机器级编程 I：基础 | `ics/ics04-zh.html` | `ics/variants-ics04/` |
| 第 5 讲 · 机器级编程 II：控制 | `ics/ics05-zh.html` | `ics/variants-ics05/` |
| Data Lab 实验台 | `ics/datalab-zh.html` | `ics/variants-lab/` |

每个画廊目录固定 5 个文件：`index.html`（预览页，用缩放 iframe 截主页面，含指向其他画廊的交叉链接）+ `01-academic.html` / `02-terminal.html` / `03-brutalist.html` / `04-glass.html`。四种风格的显示名：学术讲义、深色终端、新粗野、柔和玻璃。

### 关键事实：变体是整页副本，不是运行时换肤

- 主页面与 4 个变体之间，**正文 `<main>` 里的 `<section>` 内容和那条约 40 KB 的内联 `<script>` 是逐字相同的**；差异只在 `<head>` 的主题 CSS 块、`<title>`、`data-style` / `data-deck`、风格条和 footer 文案。
- 因此：**改一讲的内容或交互，必须同时改 5 个文件（1 主 + 4 变体）**，否则画廊里的副本会静默过期，页面上不会有任何报错。
- 变体目录命名不统一（历史原因）：第 3 讲是 `ics/variants/`，其余带讲次后缀。**不要"顺手"统一改名**——页面内相对链接和已分享的线上 URL 都会断。

### 新增 / 修改一讲的做法

1. 复制一份现有主页面作为模板，改 `<title>`、`<html data-deck="…">`、正文 `<section>`。主页面用共用基础样式 + 默认主题变量。
2. 在 `ics/variants-<新 key>/` 放 4 份主页面副本：把主题 CSS 块替换成目标风格的 block（从现有同风格变体里整段抄），再改 `<title>` 后缀、`data-style` 和风格条的"当前项"。
3. 改动会扩散到这些地方，逐一更新：
   - 6 张主页面的 `.stylebar`（每张都列出全部讲次 + Data Lab + 本讲的"全部预览"入口）；
   - 新画廊的 `index.html`（4 个 iframe + 说明），以及已有 5 个画廊 `index.html` 里的"其他课件"交叉链接；
   - `ics/index.html` 的「课件」「视觉风格」两个网格；
   - 视情况更新根 `index.html` 与 `README.md`。
4. 讲次名称 / 副标题在风格条、`ics/index.html`、落地页、README 里重复出现；改名时先找全：
   `grep -rn "第 5 讲" --include=*.html .`

## 5. gitlearn 与 shelllearn：共享终端内核 termkit

两个模拟器都是**单文件**，但各自内联了同一套通用终端内核（CSS + JS）：

- 内核 CSS 块（文件开头第一段 `<style>`）与内核 JS 块（`termkit.js`）在两个文件里**逐字相同**，只有 `<title>` 不同；各自项目的专有代码跟在后面（git 提交图 / shell 解释器与命令 / 课程数据 / 界面装配）。
- **改内核要两边同改并保持一致**；只改一个模拟器会出现两份分叉的内核。
- 源码里 `web-kit/term.css`、`web-kit/termkit.js`、`web-kit/sync.js` 这些路径**在本仓库不存在**（注释里写的是外部工具链的出处）。不要照这些路径去找文件。
- 两个模拟器共用内核但进度存储 key 不同：`git-learn-progress-v1` / `shell-learn-progress-v1`。新增存储 key 时要保持区分，避免互相覆盖。
- 文件很大（`gitlearn/index.html` 约 3400 行、`shelllearn/index.html` 约 5000 行），用精确编辑，不要整文件重写。

## 6. laiyipan：只有构建产物

- `laiyipan/index.html` 只加载 `assets/index-DbaNX_bg.js`（Vite 打包的 Phaser 应用）。**游戏源码不在仓库里**，改逻辑需要原始工程，不要手改这个被打包/压缩过的 bundle。
- 素材（`textures/`、`audio/`）是独立文件，可以直接替换或新增，但注意体积（单个最大约 3.8 MB）。
- 这是全站**唯一**使用外部网络依赖的地方：`index.html` 里引了 Google Fonts。其余页面离线可用。

## 7. 现状里容易误判的几点

- `qinshihuang/qinshihuang-bear.html` 没有被任何页面链接（孤儿页），落地页入口是 `qinshihuang-polarbear.html`。不是坏链，别删、也别当成问题修。
- `ics/floating-point-zh.html` 缺少其余 5 张主页面都有的 `data-deck` 属性（历史遗留，不影响使用）。
- 内联 JS 里存在形如 `let movSrc = 'imm'` 的代码，用 grep 粗查 `src=` 会误报成坏链。要查链接请用 §10 的脚本（它会先剥掉 `<script>`）。
- `.nojekyll` 存在于根目录；没有 `CNAME`，站点域名就是默认的 GitHub Pages 域名。

## 8. 守则

### 必须

- 动手前先 `git pull`，确认本地是 `main` 最新——线上内容由 `main` 直接生成，没有中间环境。
- 本地起 `python3 -m http.server 8000`，实际点开改动涉及的页面（尤其风格条、画廊 iframe、相对链接），再提交。
- 改 ICS 正文/交互 → 同步该讲的 4 个变体；改模拟器内核 → 同步两个模拟器。提交前跑 §10 自检。
- 新增目录入口时，同时补落地页卡片和 `ics/index.html` 的网格项。
- 提交信息用中文并说清改了什么，跟现有历史风格一致（`新增…` / `修复…` / `…更新：…`）。
- 大文件（图片 / 音频 / 字体）进仓库前先确认必要性——已有的 `laiyipan/` 素材已经占了大头。

### 禁止

- **不要把明文 token / 密码写进任何仓库文件**（仓库公开，commit 后无法撤回）。凭据用法见 §9。
- 不要引入构建工具、包管理器、框架或 `package.json`。"单文件 HTML，点开即用"是这个项目的前提；这类改造会破坏发布流程（Pages 直接从 `main` 根目录发布，没有构建步骤）。
- 不要重命名 / 移动已发布的文件或目录：会同时断掉页面内相对链接和外部已分享的 URL。
- 不要手改 `laiyipan/assets/index-DbaNX_bg.js`（打包产物）。
- 不要整文件重写大型页面（`shelllearn/index.html` 近 5000 行，`ics` 单页 100–175 KB）。用精确编辑，避免丢内容，也让 diff 可读。
- 不要在没有本地预览的情况下直接 push 到 `main`——push 即对公众生效。

## 9. 凭据

- 仓库是**公开**的：任何提交都会进入公开历史，无法撤回。
- 不要把 GitHub token 写进 `agent.md`、README 或任何仓库文件。需要推送时临时用环境变量提供，例如：

  ```bash
  export GITHUB_TOKEN=…              # 只在当前 shell 里
  git push "https://x-access-token:${GITHUB_TOKEN}@github.com/xyu20071224-design/web-pages.git" main
  ```

- 不要把带 token 的地址写进 `.git/config`（上面的做法是一次性的）。若已写入，用
  `git remote set-url origin https://github.com/xyu20071224-design/web-pages.git` 清掉。

## 10. 改动后自检

把下面的脚本存成 `/tmp/selfcheck.js`，在仓库根目录跑 `node /tmp/selfcheck.js .`。它检查本项目最容易坏的两件事：全站相对链接、以及 6 讲课件「主页面 vs 4 个变体」是否同步。

```js
const fs=require('fs'),path=require('path');
const ROOT=process.argv[2]||'.';
let files=[];
(function walk(d){for(const e of fs.readdirSync(d,{withFileTypes:true})){if(e.name==='.git')continue;const p=path.join(d,e.name);e.isDirectory()?walk(p):/\.html$/.test(e.name)&&files.push(p);}})(ROOT);
let bad=0;
for(const f of files){
  const html=fs.readFileSync(f,'utf8').replace(/<script[\s\S]*?<\/script>/gi,'');
  for(const m of html.matchAll(/(?:href|src)\s*=\s*["']([^"']+)["']/gi)){
    let u=m[1].trim();
    if(!u||u.startsWith('#')||/^(https?:|mailto:|data:|javascript:|\/\/)/i.test(u))continue;
    u=u.split('#')[0].split('?')[0]; if(!u)continue;
    const t=path.resolve(path.dirname(f),u);
    if(!fs.existsSync(t)){bad++;console.log('BROKEN LINK',path.relative(ROOT,f),'->',u);}
    else if(fs.statSync(t).isDirectory()&&!fs.existsSync(path.join(t,'index.html'))){bad++;console.log('NO INDEX',path.relative(ROOT,f),'->',u);}
  }
}
console.log('link check:',files.length,'files,',bad,'broken');
const pairs=[['ics/ics01-zh.html','ics/variants-ics01'],['ics/bits-bytes-ints-zh.html','ics/variants-bits'],['ics/floating-point-zh.html','ics/variants'],['ics/ics04-zh.html','ics/variants-ics04'],['ics/ics05-zh.html','ics/variants-ics05'],['ics/datalab-zh.html','ics/variants-lab']];
const norm=s=>s.replace(/\s+/g,'');
let drift=0;
for(const [main,dir] of pairs){
  const mainTxt=fs.readFileSync(path.join(ROOT,main),'utf8');
  const bodyOf=t=>{const a=t.indexOf('<main'),b=t.lastIndexOf('</main>');return a<0||b<0?'':norm(t.slice(a,b));};
  const scriptsOf=t=>(t.match(/<script[\s\S]*?<\/script>/gi)||[]).map(norm).join('|');
  const expectBody=bodyOf(mainTxt), expectScripts=scriptsOf(mainTxt);
  for(const n of ['01-academic','02-terminal','03-brutalist','04-glass']){
    const p=dir+'/'+n+'.html';
    if(!fs.existsSync(path.join(ROOT,p))){console.log('MISSING VARIANT',p);drift++;continue;}
    const t=fs.readFileSync(path.join(ROOT,p),'utf8');
    if(bodyOf(t)!==expectBody){console.log('DRIFT body',p,'vs',main);drift++;}
    if(scriptsOf(t)!==expectScripts){console.log('DRIFT script',p,'vs',main);drift++;}
  }
}
console.log('ics variant sync:',pairs.length,'lectures,',drift,'drift');
```

当前状态（写这份文档时跑过一次）：43 个 HTML、0 条坏链、6 讲 0 处漂移。
