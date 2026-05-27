"""
AI4Scholar — Auto-Cite 自动引用标注示例（通过 ai4scholar.net API）

功能：为学术文本自动添加真实引用，返回标注后的文本 + 参考文献列表 + BibTeX。

需要 API Key，处理时间 20-60 秒（SSE 流式响应）。

基础 URL: https://ai4scholar.net/api/proxy/auto-cite
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
TIMEOUT_S = 300  # 5 minutes for SSE streaming


def auto_cite(
    text,
    mode="auto",
    min_citations=10,
    field=None,
    year_preference=None,
    exclude_preprints=False,
    exclude_conferences=False,
    citation_style="ieee",
):
    """
    自动引用标注

    参数:
        text: 待标注的学术文本（100-10000 字符）
        mode: "auto"（自动检测引用位置）或 "manual"（用 [CITE] 标记位置）
        min_citations: 最少引用数
        field: 学术领域（如 "computer science"）
        year_preference: 偏好引用年份
        exclude_preprints: 排除预印本
        exclude_conferences: 排除会议论文
        citation_style: "ieee"/"apa"/"vancouver"/"nature"/"numbered"
    """
    if not API_KEY:
        raise ValueError("需要配置 API Key")

    body = {
        "text": text,
        "mode": mode,
        "minCitations": min_citations,
        "citationStyle": citation_style,
    }
    if field:
        body["field"] = field
    if year_preference:
        body["yearPreference"] = year_preference
    if exclude_preprints:
        body["excludePreprints"] = True
    if exclude_conferences:
        body["excludeConferences"] = True

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "ai4scholar-python-example/1.0",
    }

    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{BASE_URL}/api/proxy/auto-cite",
        data=data,
        headers=headers,
        method="POST",
    )

    print("  正在处理（通常需要 20-60 秒）...")
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
        # 解析 SSE 流
        result = None
        last_error = None
        buffer = ""

        while True:
            chunk = resp.read(4096)
            if not chunk:
                break
            buffer += chunk.decode()

            lines = buffer.split("\n")
            buffer = lines.pop() or ""

            current_event = ""
            for line in lines:
                line = line.strip()
                if line.startswith("event: "):
                    current_event = line[7:].strip()
                elif line.startswith("data: "):
                    try:
                        payload = json.loads(line[6:])
                        if current_event == "result":
                            result = payload
                        elif current_event == "error":
                            last_error = payload.get("message", "处理出错")
                    except json.JSONDecodeError:
                        pass

        if result:
            return result
        raise RuntimeError(last_error or "未收到结果")


def main():
    print("=" * 60)
    print("AI4Scholar — Auto-Cite 自动引用标注示例")
    print("=" * 60)

    if not API_KEY:
        print("\n⚠  未配置 API Key。请编辑 ../config.yaml 后重试。")
        return

    sample_text = (
        "Deep learning has revolutionized the field of natural language processing in recent years. "
        "Transformer-based architectures have become the dominant approach for sequence modeling tasks, "
        "achieving state-of-the-art results across a wide range of benchmarks. "
        "The self-attention mechanism allows these models to capture long-range dependencies effectively, "
        "which was a significant limitation of previous recurrent neural network approaches. "
        "Pre-trained language models have further advanced the field by enabling transfer learning "
        "across diverse NLP tasks. However, the large computational requirements of these models "
        "pose significant challenges for deployment in resource-constrained environments. "
        "Recent work has explored various approaches to model compression, including quantization, "
        "pruning, and knowledge distillation, to address these challenges. "
        "Additionally, the environmental impact of training large language models has raised concerns "
        "about the sustainability of current research directions. "
        "Several studies have proposed more efficient architectures and training methods to reduce "
        "the carbon footprint of NLP research while maintaining performance."
    )

    print(f"\n📝 输入文本 ({len(sample_text)} 字符):")
    print(f"  \"{sample_text[:200]}...\"")

    try:
        result = auto_cite(
            text=sample_text,
            mode="auto",
            min_citations=8,
            citation_style="ieee",
            field="computer science",
        )

        print("\n📄 标注后文本:")
        print(f"  {result.get('annotatedText', '(空)')[:500]}...")

        print(f"\n📚 参考文献 ({result.get('referenceCount', 0)} 条):")
        for ref in result.get("references", [])[:5]:
            print(f"  [{ref.get('number')}] {ref.get('formatted', '')[:120]}")

        if result.get("bibtex"):
            print(f"\n📋 BibTeX ({len(result['bibtex'])} 字符):")
            print(f"  {result['bibtex'][:300]}...")

        stats = result.get("stats", {})
        print(f"\n📊 统计:")
        print(f"  引用数: {stats.get('citationCount', '?')}")
        print(f"  搜索次数: {stats.get('searchCount', '?')}")
        print(f"  处理时间: {stats.get('processingTime', '?')}ms")

    except Exception as e:
        print(f"\n✗ 出错: {e}")

    print("\n✅ 示例执行完毕")


if __name__ == "__main__":
    main()
