#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站缓存视频转换脚本
- 删除 .m4s 文件开头的 9 个字节（B站私有头）
- 根据文件内容自动识别视频/音频流，分别保存为 .mp4 / .mp3
- 调用 ffmpeg 将两者合并为最终 mp4 文件
"""

import os
import sys
import glob
import json
import struct
import shutil
import subprocess
from pathlib import Path

# ──────────────────────────────────────────────
# ffmpeg / ffprobe 路径探测
# ──────────────────────────────────────────────
_WINGET_FFMPEG_GLOB = os.path.expandvars(
    r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg_*\ffmpeg-*\bin"
)

def _find_tool(name: str) -> str | None:
    """先用 shutil.which，找不到再去 WinGet 安装目录探测。"""
    found = shutil.which(name)
    if found:
        return found
    for bin_dir in glob.glob(_WINGET_FFMPEG_GLOB):
        exe = Path(bin_dir) / f"{name}.exe"
        if exe.exists():
            return str(exe)
    return None

FFMPEG  = _find_tool("ffmpeg")
FFPROBE = _find_tool("ffprobe")


# ──────────────────────────────────────────────
# 工具函数
# ──────────────────────────────────────────────

BILIBILI_HEADER_SIZE = 9  # B站在 m4s 文件开头插入的私有字节数


def strip_bilibili_header(src: Path, dst: Path) -> None:
    """跳过前 9 个字节，将剩余内容写入目标文件。"""
    with open(src, "rb") as f:
        f.read(BILIBILI_HEADER_SIZE)          # 丢弃前 9 字节
        data = f.read()
    with open(dst, "wb") as f:
        f.write(data)
    print(f"  [strip] {src.name} -> {dst.name}  ({len(data):,} bytes)")


def find_m4s_pairs(base_dir: Path):
    """
    在 base_dir 下递归查找所有 .m4s 文件，按目录分组后返回
    每组 (m4s_files, folder) 的列表。
    """
    groups: dict[Path, list[Path]] = {}
    for m4s in sorted(base_dir.rglob("*.m4s")):
        folder = m4s.parent
        groups.setdefault(folder, []).append(m4s)

    pairs = []
    for folder, files in groups.items():
        if len(files) < 2:
            print(f"[warn] {folder} 只找到 {len(files)} 个 .m4s，跳过")
            continue
        if len(files) > 2:
            print(f"[warn] {folder} 找到 {len(files)} 个 .m4s，取前两个")
            files = files[:2]
        pairs.append((files, folder))
    return pairs


# ──────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────

def process_folder(m4s_files: list[Path], folder: Path) -> None:
    tmp_files: list[Path] = []

    # 1. 去掉 B站私有头，写到临时文件
    stripped: list[Path] = []
    for m4s in m4s_files:
        tmp = folder / (m4s.stem + "_stripped.mp4")
        strip_bilibili_header(m4s, tmp)
        stripped.append(tmp)
        tmp_files.append(tmp)

    # 2. 识别哪个是视频、哪个是音频
    video_tmp: Path | None = None
    audio_tmp: Path | None = None

    for tmp in stripped:
        if FFPROBE:
            # 用 ffprobe 检测是否含视频流
            cmd = [
                FFPROBE, "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=codec_type",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(tmp),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            has_video = result.stdout.strip() == "video"
        else:
            # 回退：文件更大的当视频
            has_video = (tmp.stat().st_size == max(s.stat().st_size for s in stripped))

        if has_video and video_tmp is None:
            video_tmp = tmp
        else:
            audio_tmp = tmp

    if video_tmp is None or audio_tmp is None:
        print(f"  [error] 无法区分视频/音频流，跳过 {folder}")
        for f in tmp_files:
            f.unlink(missing_ok=True)
        return

    # 3. 重命名为正式扩展名
    video_mp4 = folder / (folder.name + "_video.mp4")
    audio_mp3 = folder / (folder.name + "_audio.mp3")   # 实际是 AAC/m4a，ffmpeg 可处理

    shutil.move(str(video_tmp), str(video_mp4))
    shutil.move(str(audio_tmp), str(audio_mp3))
    tmp_files = [f for f in tmp_files if f != video_tmp and f != audio_tmp]

    print(f"  [rename] video -> {video_mp4.name}")
    print(f"  [rename] audio -> {audio_mp3.name}")

    # 4. 读取视频标题（若有 videoInfo.json）
    info_json = folder / "videoInfo.json"
    output_name = folder.name  # 默认用目录名
    if info_json.exists():
        try:
            with open(info_json, encoding="utf-8") as f:
                info = json.load(f)
            title = info.get("title", "").strip()
            if title:
                # 去掉文件名中的非法字符
                safe = "".join(c if c not in r'\/:*?"<>|' else "_" for c in title)
                output_name = safe
        except Exception:
            pass

    output_mp4 = folder / f"{output_name}.mp4"

    # 5. 调用 ffmpeg 合并
    if not FFMPEG:
        print("  [error] 未找到 ffmpeg，请安装后重试")
        return

    cmd = [
        FFMPEG,
        "-y",                       # 覆盖已有文件
        "-i", str(video_mp4),
        "-i", str(audio_mp3),
        "-c:v", "copy",             # 视频流直接复制，无需重新编码
        "-c:a", "aac",              # 音频转 AAC（兼容 mp4 容器）
        "-strict", "experimental",
        str(output_mp4),
    ]
    print(f"  [ffmpeg] 合并中 -> {output_mp4.name} ...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"  [done]  输出: {output_mp4}")
        # 清理中间文件
        video_mp4.unlink(missing_ok=True)
        audio_mp3.unlink(missing_ok=True)
        for f in tmp_files:
            f.unlink(missing_ok=True)
    else:
        print(f"  [error] ffmpeg 失败:\n{result.stderr[-2000:]}")


def main():
    base_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent
    base_dir = base_dir.resolve()
    print(f"扫描目录: {base_dir}\n")

    pairs = find_m4s_pairs(base_dir)
    if not pairs:
        print("未找到任何 .m4s 文件对，退出。")
        return

    for m4s_files, folder in pairs:
        print(f"\n处理: {folder}")
        process_folder(m4s_files, folder)

    print("\n全部完成！")


if __name__ == "__main__":
    main()
