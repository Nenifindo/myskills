#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站缓存解析导出脚本
- 删除 .m4s 文件开头的 9 个字节（B站私有头）
- 根据文件内容自动识别视频/音频流
- 支持导出合并后的 MP4 视频、纯音频文件，或两者同时导出
"""

import argparse
import os
import glob
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ──────────────────────────────────────────────
# ffmpeg / ffprobe 路径探测
# ──────────────────────────────────────────────
_WINGET_FFMPEG_GLOB = os.path.expandvars(
    r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg_*\ffmpeg-*\bin"
)

def _find_tool(name: str) -> Optional[str]:
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


def safe_output_stem(folder: Path) -> str:
    """读取 videoInfo.json 的 title 字段；读取失败时退回目录名。"""
    info_json = folder / "videoInfo.json"
    output_name = folder.name
    if not info_json.exists():
        return output_name

    try:
        with open(info_json, encoding="utf-8") as f:
            info = json.load(f)
        title = info.get("title", "").strip()
        if title:
            output_name = "".join(c if c not in r'\/:*?"<>|' else "_" for c in title)
    except Exception:
        pass
    return output_name


def find_m4s_pairs(base_dir: Path):
    """
    在 base_dir 下递归查找所有 .m4s 文件，按目录分组后返回
    每组 (m4s_files, folder) 的列表。
    """
    groups: Dict[Path, List[Path]] = {}
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

def detect_streams(stripped: List[Path]) -> Tuple[Optional[Path], Optional[Path]]:
    video_tmp: Optional[Path] = None
    audio_tmp: Optional[Path] = None

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

    return video_tmp, audio_tmp


def export_audio(audio_src: Path, output_stem: str, folder: Path, audio_format: str) -> bool:
    if not FFMPEG:
        print("  [error] 未找到 ffmpeg，请安装后重试")
        return False

    output_audio = folder / f"{output_stem}.{audio_format}"
    if audio_format == "m4a":
        codec_args = ["-c:a", "copy"]
    else:
        codec_args = ["-c:a", "libmp3lame", "-q:a", "2"]

    cmd = [
        FFMPEG,
        "-y",
        "-i", str(audio_src),
        "-vn",
        *codec_args,
        str(output_audio),
    ]
    print(f"  [ffmpeg] 导出音频 -> {output_audio.name} ...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"  [done]  音频: {output_audio}")
        return True

    print(f"  [error] ffmpeg 音频导出失败:\n{result.stderr[-2000:]}")
    return False


def export_video(video_src: Path, audio_src: Path, output_stem: str, folder: Path) -> bool:
    if not FFMPEG:
        print("  [error] 未找到 ffmpeg，请安装后重试")
        return False

    output_mp4 = folder / f"{output_stem}.mp4"
    cmd = [
        FFMPEG,
        "-y",                       # 覆盖已有文件
        "-i", str(video_src),
        "-i", str(audio_src),
        "-c:v", "copy",             # 视频流直接复制，无需重新编码
        "-c:a", "aac",              # 音频转 AAC（兼容 mp4 容器）
        "-strict", "experimental",
        str(output_mp4),
    ]
    print(f"  [ffmpeg] 合并视频 -> {output_mp4.name} ...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"  [done]  视频: {output_mp4}")
        return True

    print(f"  [error] ffmpeg 视频合并失败:\n{result.stderr[-2000:]}")
    return False


def process_folder(m4s_files: List[Path], folder: Path, mode: str, audio_format: str) -> None:
    tmp_files: List[Path] = []

    # 1. 去掉 B站私有头，写到临时文件
    stripped: List[Path] = []
    for m4s in m4s_files:
        tmp = folder / (m4s.stem + "_stripped.m4s")
        strip_bilibili_header(m4s, tmp)
        stripped.append(tmp)
        tmp_files.append(tmp)

    # 2. 识别哪个是视频、哪个是音频
    video_tmp, audio_tmp = detect_streams(stripped)

    if video_tmp is None or audio_tmp is None:
        print(f"  [error] 无法区分视频/音频流，跳过 {folder}")
        for f in tmp_files:
            f.unlink(missing_ok=True)
        return

    # 3. 重命名为中间文件
    video_mp4 = folder / (folder.name + "_video.mp4")
    audio_m4a = folder / (folder.name + "_audio.m4a")

    video_mp4.unlink(missing_ok=True)
    audio_m4a.unlink(missing_ok=True)
    shutil.move(str(video_tmp), str(video_mp4))
    shutil.move(str(audio_tmp), str(audio_m4a))
    tmp_files = [f for f in tmp_files if f != video_tmp and f != audio_tmp]

    print(f"  [rename] video -> {video_mp4.name}")
    print(f"  [rename] audio -> {audio_m4a.name}")

    output_stem = safe_output_stem(folder)
    ok = True
    if mode in ("video", "both"):
        ok = export_video(video_mp4, audio_m4a, output_stem, folder) and ok
    if mode in ("audio", "both"):
        ok = export_audio(audio_m4a, output_stem, folder, audio_format) and ok

    if ok:
        video_mp4.unlink(missing_ok=True)
        audio_m4a.unlink(missing_ok=True)
        for f in tmp_files:
            f.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(
        description="解析 B 站客户端 .m4s 缓存，导出 MP4 视频或纯音频。"
    )
    parser.add_argument(
        "base_dir",
        nargs="?",
        default=Path(__file__).parent,
        type=Path,
        help="缓存根目录；默认使用脚本所在目录。",
    )
    parser.add_argument(
        "--mode",
        choices=("video", "audio", "both"),
        default="video",
        help="导出模式：video 合并 MP4；audio 仅导出音频；both 同时导出。默认 video。",
    )
    parser.add_argument(
        "--audio-format",
        choices=("m4a", "mp3"),
        default="m4a",
        help="纯音频导出格式。m4a 默认无损复制音频流；mp3 会转码。默认 m4a。",
    )
    args = parser.parse_args()

    base_dir = args.base_dir
    base_dir = base_dir.resolve()
    print(f"扫描目录: {base_dir}\n")

    pairs = find_m4s_pairs(base_dir)
    if not pairs:
        print("未找到任何 .m4s 文件对，退出。")
        return

    for m4s_files, folder in pairs:
        print(f"\n处理: {folder}")
        process_folder(m4s_files, folder, args.mode, args.audio_format)

    print("\n全部完成！")


if __name__ == "__main__":
    main()
