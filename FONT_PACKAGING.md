# PDF 字体打包说明

这个项目的 PDF 模板主要使用这些字体族：

- `SimSun`
- `FangSong`
- `KaiTi`

为了让项目在 `Alibaba Linux + Docker` 中稳定生成中文 PDF，当前仓库已经把下面这些字体文件一起收进来了：

- [simsun.ttc](d:/Users/32223/Desktop/resume/backend/server-fonts/simsun.ttc)
- [simfang.ttf](d:/Users/32223/Desktop/resume/backend/server-fonts/simfang.ttf)
- [simkai.ttf](d:/Users/32223/Desktop/resume/backend/server-fonts/simkai.ttf)
- [NotoSansSC-VF.ttf](d:/Users/32223/Desktop/resume/backend/server-fonts/NotoSansSC-VF.ttf)

`backend/Dockerfile` 构建时会自动把它们复制到：

- `/usr/local/share/fonts/resume`

然后执行：

```bash
fc-cache -f -v
```

这样容器里的 Chromium 在打印 PDF 时就能直接找到这些字体。

## 你现在怎么用

推送到 Git 后，在服务器上正常执行：

```bash
git clone <repo>
cd resume
cp .env.docker.example .env.docker
sh deploy.sh
```

字体会随着仓库一起拉下来，不需要你再额外手工装字体。

## 重要提醒

这里面的 `SimSun` / `FangSong` / `KaiTi` 来自你的 Windows 字体目录。

这在技术上可以用，但授权上未必适合公开分发。

如果仓库是：

- 私有仓库：通常更可控
- 公开仓库：建议改成可再分发的开源中文字体

如果你后面想把仓库公开，我建议下一步把模板字体切到开源字体方案，我可以继续帮你换掉。
