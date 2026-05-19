---
name: bilibili-cache-to-mp4
description: 将 B 站 Android/PC 客户端缓存的 .m4s 文件转换为可播放的 MP4 视频。当用户提到"B站缓存转 mp4"、"bilibili 缓存视频转换"、"m4s 转 mp4"、"合并 B站视频音频"或类似意图时触发。
agent_created: true
---

# B站缓存视频转 MP4 技能

## 背景知识

B站客户端（Android / PC）缓存的视频由两个 `.m4s` 文件组成：
- **视频流**（较大，通常几百 MB）：包含画面，无声音
- **音频流**（较小，通常几十 MB）：仅包含声音

这两个文件的开头被插入了 **9 个字节的私有头**（`0x30 * 9`，即 ASCII `000000000`），需要先剥离才能被 ffmpeg 正确识别。

## 依赖项

| 工具 | 说明 |
|------|------|
| Python 3.8+ | 运行转换脚本 |
| ffmpeg | 合并视频/音频流（包含 ffprobe） |

### ffmpeg 安装方式（Windows）

```bash
# 推荐：winget（安装后在 WinGet Packages 目录，未必自动加入 PATH）
winget install Gyan.FFmpeg

# 或 Scoop（会自动加入 PATH）
scoop install ffmpeg
```

> 脚本已内置 WinGet 安装路径的自动探测，未加入 PATH 也可正常运行。

## 转换脚本

完整脚本见 `scripts/bilibili_convert.py`。

### 脚本功能

1. **递归扫描**工作目录，找出所有 `.m4s` 文件对
2. **剥离**每个文件开头的 9 字节私有头
3. 用 **ffprobe** 自动识别哪个是视频流、哪个是音频流
4. 将两者分别命名为 `xxx_video.mp4` / `xxx_audio.mp3`
5. 调用 **ffmpeg** 合并（视频 `-c:v copy` 直接复制，音频转为 AAC）
6. 从同目录 `videoInfo.json` 读取标题作为输出文件名
7. 自动清理中间临时文件

### 运行方式

```bash
# 在缓存目录下直接运行（自动扫描当前目录）
python bilibili_convert.py

# 或指定目录
python bilibili_convert.py C:\Users\Fourier\Videos\bilibili
```

### 目录结构约定

```
bilibili/
├── 38422646362/              ← 每个视频一个子目录（以 cid 命名）
│   ├── 38422646362-1-30112.m4s   ← 视频流（大文件）
│   ├── 38422646362-1-30280.m4s   ← 音频流（小文件）
│   ├── videoInfo.json            ← 含 title 字段，用于命名输出文件
│   └── ...
└── bilibili_convert.py
```

转换后输出：
```
bilibili/
└── 38422646362/
    └── 第331集 谈谈大众学术.mp4   ← 合并完成的最终文件
```

## 步骤详解

### 步骤 1：确认环境

```bash
# 检查 ffmpeg 是否可用（PATH 中）
ffmpeg -version

# 若未在 PATH 中，Windows WinGet 安装路径为：
# %LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg_*\ffmpeg-*\bin\ffmpeg.exe
```

### 步骤 2：部署脚本

将 `scripts/bilibili_convert.py` 复制到缓存视频的**根目录**（即包含各 cid 子目录的上层目录）。

### 步骤 3：运行转换

```bash
python bilibili_convert.py
```

预期输出示例：
```
扫描目录: C:\Users\Fourier\Videos\bilibili

处理: C:\Users\Fourier\Videos\bilibili\38422646362
  [strip] 38422646362-1-30112.m4s -> 38422646362-1-30112_stripped.mp4  (381,153,051 bytes)
  [strip] 38422646362-1-30280.m4s -> 38422646362-1-30280_stripped.mp4  (41,322,044 bytes)
  [rename] video -> 38422646362_video.mp4
  [rename] audio -> 38422646362_audio.mp3
  [ffmpeg] 合并中 -> 第331集 谈谈大众学术.mp4 ...
  [done]  输出: C:\...\38422646362\第331集 谈谈大众学术.mp4

全部完成！
```

### 步骤 4：验证输出

```bash
ffprobe -v quiet -show_format -show_streams output.mp4
```

期望：包含一条 H.264/HEVC 视频流 + 一条 AAC 音频流。

## 常见问题

| 问题 | 原因 | 解决方法 |
|------|------|----------|
| `未找到 ffmpeg` | 未安装或未加入 PATH | 安装 ffmpeg；脚本会自动探测 WinGet 路径 |
| `只找到 1 个 .m4s` | 缓存不完整 | 重新在 B站客户端缓存该视频 |
| `ffmpeg 失败` | 文件损坏或格式异常 | 检查 m4s 文件大小是否为 0，重新下载 |
| 输出文件名为 cid 数字 | `videoInfo.json` 不存在或无 `title` 字段 | 正常，以目录名（cid）命名输出文件 |

## 注意事项

- 原始 `.m4s` 文件**不会被删除**，转换后可手动清理
- 脚本支持批量处理：一次可转换工作目录下**所有**缓存视频
- 视频流直接 `-c:v copy` 复制，**无画质损失**
- 已知兼容：B站 Android 客户端、B站 PC 客户端缓存格式
