"""
AI4Scholar — Google Scholar 搜索示例（通过 ai4scholar.net 代理）

Google Scholar 没有开放 API，需要通过 ai4scholar.net 代理访问。

基础 URL: https://ai4scholar.net/google-scholar/v1

需要 API Key，配置方式：
  1. 前往 https://ai4scholar.net 注册
  2. 编辑 ../config.yaml，填入 apiKey
"""

import os
import sys
import json
import urllib.request
import urllib.error
import time

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

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "ai4scholar-python-example/1.0",
}
if API_KEY:
    HEADERS["Authorization"] = f"Bearer {API_KEY}"


def search_google_scholar(query, max_results=10, year_from=None, year_to=None):
    """
    搜索 Google Scholar

    参数:
        query: 搜索关键词
        max_results: 最大结果数（默认 10，最大 50）
        year_from: 起始年份（如 2020）
        year_to: 结束年份（如 2025）
    """
    all_results = []
    page = 1
    per_page = 10

    while len(all_results) < max_results:
        body = {"query": query, "page": page}
        if year_from is not None:
            body["yearFrom"] = year_from
        if year_to is not None:
            body["yearTo"] = year_to

        data = json.dumps(body).encode()
        req = urllib.request.Request(
            f"{BASE_URL}/google-scholar/v1/search",
            data=data,
            headers=HEADERS,
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())

        results = result.get("results", [])
        if not results:
            break

        all_results.extend(results)
        if result.get("resultsCount", 0) < per_page:
            break
        page += 1

    return all_results[:max_results]


def main():
    print("=" * 60)
    print("AI4Scholar — Google Scholar 搜索示例")
    print("=" * 60)

    if not API_KEY:
        print("\n⚠  未配置 API Key。请编辑 ../config.yaml 后重试。")
        return

    # 1. 基础搜索
    print("\n--- 1. 搜索论文 ---")
    results = search_google_scholar("deep learning", max_results=5)
    print(f"搜索到 {len(results)} 条结果\n")
    for i, r in enumerate(results, 1):
        print(f"  #{i} {r.get('title', '?')}")
        authors = r.get("authors", "")
        print(f"     作者: {authors if authors else 'N/A'}")
        cited = r.get("citedBy", r.get("citationCount", 0))
        print(f"     引用: {cited}")
        snippet = r.get("snippet", r.get("abstract", ""))
        if snippet:
            print(f"     摘要: {snippet[:150]}...")
        print()

    # 2. 年份过滤
    print("--- 2. 年份过滤（2024-2025）---")
    results = search_google_scholar("graph neural network", max_results=3, year_from=2024, year_to=2025)
    print(f"搜索到 {len(results)} 条结果\n")
    for r in results:
        print(f"  • {r.get('title', '?')} ({r.get('year', '?')})")

    # 3. 不同领域示例
    print("\n--- 3. 搜索示例 ---")
    examples = [
        "transformer time series",
        "CRISPR gene editing",
        "reinforcement learning robotics",
    ]
    for q in examples:
        results = search_google_scholar(q, max_results=1)
        if results:
            print(f"  「{q}」: {results[0].get('title', '?')}")

    print("\n✅ 示例执行完毕")


if __name__ == "__main__":
    main()
