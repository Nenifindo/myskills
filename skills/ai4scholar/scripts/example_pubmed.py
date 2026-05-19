"""
AI4Scholar — PubMed API 调用示例（通过 ai4scholar.net 代理）

基础 URL: https://ai4scholar.net/pubmed/v1

需要 API Key，配置方式：
  1. 前往 https://ai4scholar.net 注册
  2. 编辑 ../config.yaml，填入 apiKey
"""

import os
import json
import sys

# ── 配置读取 ──────────────────────────────────────────────────────────────

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


def api_post(path, body):
    """POST 请求"""
    import urllib.request
    import time

    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=HEADERS, method="POST")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                time.sleep(2 * 2 ** attempt)
                continue
            raise


def api_get(path, params=None):
    """GET 请求"""
    import urllib.request
    import time
    from urllib.parse import urlencode

    url = f"{BASE_URL}{path}"
    if params:
        url += "?" + urlencode({k: str(v) for k, v in params.items() if v is not None})

    req = urllib.request.Request(url, headers=HEADERS)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                time.sleep(2 * 2 ** attempt)
                continue
            raise


# ================================ API 函数 =================================


def search_pubmed(query, limit=10, sort="relevance", min_date=None, max_date=None):
    """搜索 PubMed 论文"""
    body = {"query": query, "limit": limit, "offset": 0, "sort": sort}
    if min_date:
        body["minDate"] = min_date
    if max_date:
        body["maxDate"] = max_date
    return api_post("/pubmed/v1/paper/search", body)


def get_pubmed_detail(pmid):
    """论文详情"""
    return api_get(f"/pubmed/v1/paper/{pmid}")


def get_pubmed_citations(pmid, limit=20):
    """施引文献"""
    return api_get(f"/pubmed/v1/paper/{pmid}/citations", {"limit": limit})


def get_pubmed_related(pmid, limit=20):
    """相关论文"""
    return api_get(f"/pubmed/v1/paper/{pmid}/related", {"limit": limit})


def batch_pubmed(pmids):
    """批量查询"""
    return api_post("/pubmed/v1/paper/batch", {"pmids": pmids})


# ================================ main ====================================


def main():
    print("=" * 60)
    print("AI4Scholar — PubMed API 示例")
    print("=" * 60)

    if not API_KEY:
        print("\n⚠  未配置 API Key。请配置后重试。")
        return

    # 1. 搜索
    print("\n--- 1. 搜索论文 ---")
    result = search_pubmed("CRISPR cancer immunotherapy", limit=3)
    papers = result.get("papers", [])
    print(f"搜索到 {result.get('total', 0)} 篇论文")
    for p in papers[:3]:
        print(f"  [PMID:{p.get('pmid', '?')}] {p.get('title', '?')} ({p.get('year', '?')})")

    # 2. 论文详情
    print("\n--- 2. 论文详情 ---")
    if papers:
        pmid = papers[0].get("pmid", "")
        if pmid:
            detail = get_pubmed_detail(pmid)
            p = detail.get("paper", detail)
            print(f"  标题: {p.get('title', '?')}")
            print(f"  期刊: {p.get('journal', '?')}")
            print(f"  作者: {', '.join(p.get('authors', [])[:5])}")

    # 3. 引文查询
    print("\n--- 3. 引文查询 ---")
    example_pmids = ["39575807", "30102808"]
    for pmid in example_pmids:
        try:
            cites = get_pubmed_citations(pmid, limit=3)
            items = cites if isinstance(cites, list) else cites.get("citations", cites.get("papers", []))
            print(f"  PMID:{pmid} → {len(items)} 条施引文献")
            break
        except Exception as e:
            pass

    # 4. 批量查询
    if example_pmids:
        print("\n--- 4. 批量查询 ---")
        batch = batch_pubmed(example_pmids)
        items = batch if isinstance(batch, list) else batch.get("papers", [])
        print(f"  批量查询 {len(example_pmids)} 篇，返回 {len(items)} 条")

    print("\n✅ 示例执行完毕")


if __name__ == "__main__":
    main()
