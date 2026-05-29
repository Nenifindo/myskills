---
name: parse-bilibili
description: 解析 B 站 Android/PC 客户端缓存的 .m4s 文件，并导出可播放的 MP4 视频或纯音频文件。Use when users ask for B站缓存转换、bilibili 缓存解析、m4s 转 mp4、m4s 提取音频、导出 B站缓存音频、合并 B站视频音频、B站缓存转视频/音频等任务。
---

# Parse Bilibili

## 背景

B站客户端缓存通常包含两个 `.m4s` 文件：

- 视频流：包含画面，无声音，通常体积较大
- 音频流：仅包含声音，通常体积较小

这些 `.m4s` 文件开头常带有 9 字节私有头，需要先剥离，再用 ffprobe/ffmpeg 识别与导出。

## 依赖

- Python 3.8+
- ffmpeg 和 ffprobe

Windows 可用以下方式安装 ffmpeg：

```bash
winget install Gyan.FFmpeg
```

或：

```bash
scoop install ffmpeg
```

脚本会自动探测 WinGet 的常见安装路径；如果 ffmpeg 已加入 PATH，也会直接使用 PATH 中的版本。

## 脚本

使用 `scripts/parse_bilibili.py`。脚本会：

1. 递归扫描目标目录下的 `.m4s` 文件
2. 按目录将视频流和音频流配对
3. 剥离 B站私有头
4. 用 ffprobe 自动识别视频流和音频流，缺少 ffprobe 时退回到“较大文件为视频”的启发式判断
5. 从同目录 `videoInfo.json` 的 `title` 字段生成安全文件名；没有标题时使用目录名
6. 按模式导出 MP4 视频、纯音频，或两者同时导出
7. 成功后清理中间文件，不删除原始 `.m4s`

## 用法

把 `scripts/parse_bilibili.py` 复制到缓存根目录，或直接用参数指定缓存目录。

导出视频（默认行为）：

```bash
python parse_bilibili.py C:\Users\Fourier\Videos\bilibili
```

仅导出纯音频，默认 `.m4a`，无损复制音频流：

```bash
python parse_bilibili.py C:\Users\Fourier\Videos\bilibili --mode audio
```

仅导出纯音频，并转码为 `.mp3`：

```bash
python parse_bilibili.py C:\Users\Fourier\Videos\bilibili --mode audio --audio-format mp3
```

同时导出视频和音频：

```bash
python parse_bilibili.py C:\Users\Fourier\Videos\bilibili --mode both
```

如果不传目录，脚本默认扫描脚本所在目录。

## 输出

示例缓存结构：

```text
bilibili/
├── 38422646362/
│   ├── 38422646362-1-30112.m4s
│   ├── 38422646362-1-30280.m4s
│   └── videoInfo.json
└── parse_bilibili.py
```

可能输出：

```text
bilibili/
└── 38422646362/
    ├── 第331集 谈谈大众学术.mp4
    └── 第331集 谈谈大众学术.m4a
```

## 验证

视频输出：

```bash
ffprobe -v quiet -show_format -show_streams output.mp4
```

纯音频输出：

```bash
ffprobe -v quiet -show_format -show_streams output.m4a
```

期望视频文件包含视频流和音频流；纯音频文件只包含音频流。

## 常见问题

| 问题 | 原因 | 解决方法 |
|------|------|----------|
| `未找到 ffmpeg` | 未安装或未加入 PATH | 安装 ffmpeg；Windows WinGet 路径会自动探测 |
| `只找到 1 个 .m4s` | 缓存不完整 | 重新在 B站客户端缓存该视频 |
| `无法区分视频/音频流` | 文件损坏、流异常或 ffprobe 不可用 | 检查文件大小，安装 ffmpeg/ffprobe，必要时重新缓存 |
| `ffmpeg ... 失败` | 文件损坏或编码/容器异常 | 查看脚本打印的 ffmpeg 错误，重新缓存或尝试 `--audio-format mp3` |
| 输出文件名为 cid 数字 | `videoInfo.json` 不存在或缺少 `title` | 正常，脚本会退回到目录名 |

## 注意事项

- 原始 `.m4s` 文件不会被删除
- `--mode video` 保持原来的导出 MP4 行为
- `--mode audio --audio-format m4a` 会复制原音频流，速度快且避免二次压缩
- `--mode audio --audio-format mp3` 会转码，适合需要 MP3 兼容性的场景
- 已知兼容：B站 Android 客户端、B站 PC 客户端缓存格式
