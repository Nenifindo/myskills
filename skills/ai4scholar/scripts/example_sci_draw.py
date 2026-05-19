"""
AI4Scholar — Sci-Draw 科研绘图示例（通过 ai4scholar.net API）

功能：AI 驱动的科研图片生成和编辑。
支持：文生图、图片编辑、风格迁移、SVG 生成、矢量化、专家评审等。

需要 API Key，生成时间 30-60 秒。

基础 URL: https://ai4scholar.net/api/proxy/nano/generate
"""

import os
import sys
import json
import urllib.request
import urllib.error

# ── 配置 ──────────────────────────────────────────────────────────────────


def load_api_key():
    try:
        import yaml
        cfg_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
        if os.path.exists(cfg_path):
            with open(cfg_path) as f:
                cfg = yaml.safe_load(f)
                if cfg.get("apiKey"):
                    return cfg["apiKey"]
    except ImportError:
        pass
    return os.environ.get("AI4SCHOLAR_API_KEY", "")


API_KEY = load_api_key()
BASE_URL = "https://ai4scholar.net"
TIMEOUT_S = 300


def sci_draw(
    action,
    prompt="",
    model="flash31",
    image_size="2K",
    aspect_ratio="1:1",
    images=None,
    style_preset=None,
    lang="en",
    vectorize_mode=None,
):
    """
    科研绘图

    参数:
        action: "smart"/"generate"/"edit"/"style"/"compose"/"iterate"/"critic"/"svg"/"vectorize"
        prompt: 图片描述（smart 模式下支持中文）
        model: "flash"/"flash31"/"pro"/"gptimage"
        image_size: "1K"/"2K"/"4K"
        aspect_ratio: "1:1"/"16:9"/"4:3"/"3:4"/"9:16"
        images: 输入图片列表（base64 data URI 或 URL）
        style_preset: 风格预设
        lang: "en"/"zh"
        vectorize_mode: "fast"/"standard"/"premium"（仅 vectorize 动作）
    """
    if not API_KEY:
        raise ValueError("需要配置 API Key")

    if action in ("edit", "style", "compose", "iterate", "critic", "vectorize"):
        if not images:
            raise ValueError(f"Action '{action}' 需要提供 images 参数")
        if action == "compose" and len(images) < 2:
            raise ValueError("Action 'compose' 需要至少 2 张图片")

    body = {"action": action, "prompt": prompt, "model": model}
    if image_size:
        body["imageSize"] = image_size
    if aspect_ratio:
        body["aspectRatio"] = aspect_ratio
    if images:
        body["images"] = images
    if style_preset:
        body["stylePreset"] = style_preset
    if lang:
        body["lang"] = lang
    if vectorize_mode and action == "vectorize":
        body["vectorizeMode"] = vectorize_mode

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "ai4scholar-python-example/1.0",
    }

    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{BASE_URL}/api/proxy/nano/generate",
        data=data,
        headers=headers,
        method="POST",
    )

    print(f"  ⏳ 正在生成（通常需要 30-60 秒，{action} 模式）...")
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
        result = json.loads(resp.read())

    if not result.get("success"):
        raise RuntimeError("生成失败，积分已自动退还")

    return result


def main():
    print("=" * 60)
    print("AI4Scholar — Sci-Draw 科研绘图示例")
    print("=" * 60)

    if not API_KEY:
        print("\n⚠  未配置 API Key。请编辑 ../config.yaml 后重试。")
        return

    # 1. SVG 生成（最快，无需图片输入）
    print("\n--- 1. 生成 SVG 科研示意图 ---")
    try:
        result = sci_draw(
            action="svg",
            prompt="A simple flowchart showing the steps of a deep learning pipeline: "
                   "Data Collection -> Preprocessing -> Model Training -> Evaluation -> Deployment. "
                   "Use blue and green colors, professional academic style.",
            lang="en",
        )
        if result.get("svgUrl"):
            print(f"  SVG URL: {result['svgUrl']}")
        if result.get("svgCode"):
            print(f"  SVG 代码: {len(result['svgCode'])} 字符")
        if result.get("imageUrl"):
            print(f"  预览图: {result['imageUrl']}")
        if result.get("creditCost") is not None:
            print(f"  消耗积分: {result['creditCost']}")
    except Exception as e:
        print(f"  (跳过: {e})")

    # 2. 文生图 (smart 模式)
    print("\n--- 2. 文生图（smart 模式，支持中文）---")
    try:
        result = sci_draw(
            action="smart",
            prompt="神经网络架构图，展示 Transformer 的 encoder-decoder 结构，"
                   "包含 self-attention 和 feed-forward 层，专业学术风格",
            model="flash31",
            aspect_ratio="16:9",
            lang="zh",
        )
        if result.get("imageUrl"):
            print(f"  图片 URL: {result['imageUrl']}")
        if result.get("optimizedPrompt"):
            print(f"  优化后提示词: {result['optimizedPrompt']}")
        if result.get("creditCost") is not None:
            print(f"  消耗积分: {result['creditCost']}")
    except Exception as e:
        print(f"  (跳过: {e})")

    # 3. 列出所有可用 action
    print("\n--- 3. Sci-Draw 可用操作一览 ---")
    actions = [
        ("smart", "智能模式：自动优化提示词，支持中文"),
        ("generate", "文生图"),
        ("edit", "编辑修改已有图片（需提供图片）"),
        ("style", "风格迁移（需提供图片）"),
        ("compose", "合并多张图片（需提供 ≥2 张图片）"),
        ("iterate", "自动审核并优化（需提供图片）"),
        ("critic", "专家评审，返回文字评审（需提供图片）"),
        ("svg", "生成 SVG 矢量科研图"),
        ("vectorize", "PNG/JPG → PDF+PPTX 矢量化（需提供图片）"),
    ]
    for act, desc in actions:
        print(f"  • {act:12s} - {desc}")

    # 4. 模型选择指南
    print("\n--- 4. 模型选择 ---")
    models = [
        ("flash", "快速生成"),
        ("flash31", "均衡（默认）"),
        ("pro", "高质量"),
        ("gptimage", "GPT Image 2，细节最佳"),
    ]
    for name, desc in models:
        print(f"  • {name:12s} - {desc}")

    print("\n✅ 示例执行完毕")


if __name__ == "__main__":
    main()
