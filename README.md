# 网页作品集

一些自己做的交互式网页，全部是纯静态文件，没有后端依赖。

## 目录结构

| 路径 | 内容 |
| --- | --- |
| `ics/` | 《计算机系统基础》交互式课件：Data Lab 实验台、位与整数、浮点数 |
| `ics/variants-lab/` | Data Lab 页面的四种备选视觉风格 |
| `laiyipan/` | Phaser 小游戏「来一盘吗？」，含音效与地图素材 |
| `qinshihuang/` | 「始皇北巡」单页作品 |
| `gitlearn/` | Git 学习模拟器：纯前端 git 模拟器 + 9 章零基础闯关课程（单文件） |
| `index.html` | 落地页，汇总以上入口 |

## 本地预览

```bash
python3 -m http.server 8000
# 然后打开 http://localhost:8000
```

不要直接双击 HTML 文件打开——部分页面的相对路径依赖 HTTP 服务。

## 部署

站点通过 GitHub Pages 发布，源为 `main` 分支根目录。推送后大约一分钟自动生效：

```bash
git add -A && git commit -m "update" && git push
```
