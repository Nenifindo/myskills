"""
AI4Scholar — Semantic Scholar API 调用示例（通过 ai4scholar.net 代理）

基础 URL: https://ai4scholar.net/graph/v1

需要配置 API Key：
  1. 前往 https://ai4scholar.net 注册
  2. 编辑 ../config.yaml，填入 apiKey
"""

import os
import sys
import json
import time
from urllib.parse import quote, urlencode

# ---------------------------------------------------------------------------
# 配置（优先读取上级 config.yaml，也支持环境变量）
# ---------------------------------------------------------------------------

def load_api_key():
    """从 config.yaml 或环境变量读取 API Key"""
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


def api_get(path, params=None):
    """GET 请求（自动重试 429）"""
    import urllib.request

    url = f"{BASE_URL}{path}"
    if params:
        url += "?" + urlencode({k: v for k, v in params.items() if v is not None})

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


def api_post(path, body, params=None):
    """POST 请求（自动重试 429）"""
    import urllib.request

    url = f"{BASE_URL}{path}"
    if params:
        url += "?" + urlencode({k: v for k, v in params.items() if v is not None})

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


# ================================ 示例 ====================================

FIELDS = "title,abstract,year,citationCount,authors,url,publicationDate,externalIds,fieldsOfStudy,openAccessPdf"


def search_papers(query, limit=10, year=None):
    """搜索论文"""
    params = {"query": query, "limit": limit, "fields": FIELDS}
    if year:
        params["year"] = year
    return api_get("/graph/v1/paper/search", params)


def get_paper_detail(paper_id):
    """论文详情（支持 SHA/DOI:xxx/ARXIV:xxx/PMID:xxx）"""
    return api_get(f"/graph/v1/paper/{quote(paper_id)}", {"fields": FIELDS})


def get_citations(paper_id, limit=100, offset=0):
    """施引文献"""
    return api_get(
        f"/graph/v1/paper/{quote(paper_id)}/citations",
        {"limit": limit, "offset": offset, "fields": "contexts,intents,isInfluential,title,abstract,authors,year,citationCount,externalIds"},
    )


def get_references(paper_id, limit=100, offset=0):
    """参考文献"""
    return api_get(
        f"/graph/v1/paper/{quote(paper_id)}/references",
        {"limit": limit, "offset": offset, "fields": "contexts,intents,isInfluential,title,abstract,authors,year,citationCount,externalIds"},
    )


def search_authors(query, limit=10):
    """搜索作者"""
    return api_get(
        "/graph/v1/author/search",
        {"query": query, "limit": limit, "fields": "name,affiliations,paperCount,citationCount,hIndex"},
    )


def get_author_detail(author_id):
    """作者详情"""
    return api_get(
        f"/graph/v1/author/{quote(author_id)}",
        {"fields": "name,affiliations,homepage,paperCount,citationCount,hIndex,externalIds,url"},
    )


def get_author_papers(author_id, limit=100, offset=0):
    """作者的所有论文"""
    return api_get(
        f"/graph/v1/author/{quote(author_id)}/papers",
        {"limit": limit, "offset": offset, "fields": "title,year,citationCount,authors,externalIds"},
    )


def get_recommendations(positive_ids, negative_ids=None, limit=100):
    """基于示例论文推荐"""
    body = {"positivePaperIds": positive_ids}
    if negative_ids:
        body["negativePaperIds"] = negative_ids
    return api_post("/recommendations/v1/papers/", body, {"limit": limit, "fields": "title,abstract,authors,year,citationCount,externalIds"})


def get_recommendations_for_paper(paper_id, limit=100):
    """单篇论文的相似推荐"""
    return api_get(
        f"/recommendations/v1/papers/forpaper/{quote(paper_id)}",
        {"limit": limit, "fields": "title,abstract,authors,year,citationCount,externalIds"},
    )


def batch_papers(paper_ids):
    """批量查询论文详情（最多 500 篇）"""
    return api_post("/graph/v1/paper/batch", {"ids": paper_ids}, {"fields": FIELDS})


def batch_authors(author_ids):
    """批量查询作者详情（最多 1000 个）"""
    return api_post("/graph/v1/author/batch", {"ids": author_ids}, {"fields": "name,affiliations,paperCount,citationCount,hIndex"})


def get_paper_authors(paper_id, limit=100, offset=0):
    """论文的作者列表"""
    return api_get(
        f"/graph/v1/paper/{quote(paper_id)}/authors",
        {"limit": limit, "offset": offset, "fields": "name,affiliations,paperCount,citationCount,hIndex"},
    )


def search_snippets(query, limit=10):
    """全文片段搜索（需要 API Key）"""
    return api_get("/graph/v1/snippet/search", {"query": query, "limit": limit})


def bulk_search(query, token=None, year=None):
    """批量搜索（返回最多 1000 条，含翻页 token）"""
    params = {"query": query, "fields": FIELDS}
    if token:
        params["token"] = token
    if year:
        params["year"] = year
    return api_get("/graph/v1/paper/search/bulk", params)


def exact_title_match(title):
    """精确标题匹配"""
    return api_get("/graph/v1/paper/search/match", {"query": title, "fields": FIELDS})


def download_pdf(paper_id):
    """获取论文开放获取 PDF 链接"""
    data = api_get(f"/graph/v1/paper/{quote(paper_id)}", {"fields": "title,openAccessPdf,externalIds,url"})
    paper = data
    oa_pdf = paper.get("openAccessPdf") or {}
    return {
        "title": paper.get("title"),
        "pdf_url": oa_pdf.get("url"),
        "paper_url": paper.get("url"),
    }


def read_paper(paper_id):
    """下载 PDF 并提取全文（需要 API Key 支持 PDF 下载）"""
    info = download_pdf(paper_id)
    if not info.get("pdf_url"):
        print("⚠  No open access PDF available")
        return info

    import urllib.request
    req = urllib.request.Request(info["pdf_url"], headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        pdf_bytes = resp.read()

    try:
        import pdfminer.high_level
        text = pdfminer.high_level.extract_text(io.BytesIO(pdf_bytes))
    except ImportError:
        text = f"[PDF downloaded: {len(pdf_bytes)} bytes. Install pdfminer.six for text extraction]"

    info["text"] = text
    return info


# ================================ main ====================================

def main():
    """运行所有示例"""
    print("=" * 60)
    print("AI4Scholar — Semantic Scholar API 示例")
    print("=" * 60)

    if not API_KEY:
        print("\n⚠  未配置 API Key。部分功能将受限。")
        print("   配置方式：")
        print("   1. 编辑 ../config.yaml 填入 apiKey")
        print("   2. 或设置环境变量 AI4SCHOLAR_API_KEY")
        print("   获取 Key: https://ai4scholar.net\n")

    # 1. 搜索论文
    print("\n--- 1. 搜索论文 ---")
    result = search_papers("transformer time series", limit=3)
    print(f"搜索到 {result.get('total', 0)} 篇论文")
    for paper in result.get("data", [])[:3]:
        print(f"  [{paper.get('paperId', '?')[:8]}] {paper.get('title')} "
              f"({paper.get('year')}, 引用: {paper.get('citationCount', 0)})")

    # 2. 精确标题匹配
    print("\n--- 2. 精确标题匹配 ---")
    match = exact_title_match("Attention Is All You Need")
    paper = match.get("paper") or match.get("data", [None])[0]
    if paper:
        print(f"  匹配: {paper.get('title')} ({paper.get('year')})")

    # 3. 引文查询
    print("\n--- 3. 引文查询（需要有效 paper_id）---")
    if paper and paper.get("paperId"):
        paper_id = paper["paperId"]
        cites = get_citations(paper_id, limit=5)
        cites_data = cites.get("data", [])
        print(f"  施引文献: {len(cites_data)} 条（显示前 5）")
        for c in cites_data[:3]:
            citing = c.get("citingPaper", {})
            print(f"  - {citing.get('title', '?')} ({citing.get('year', '?')})")

    # 4. 作者搜索
    print("\n--- 4. 搜索作者 ---")
    authors = search_authors("Yann LeCun", limit=3)
    for author in authors.get("data", [])[:3]:
        print(f"  [{author.get('authorId', '?')}] {author.get('name')} — "
              f"h-index: {author.get('hIndex', '?')}, "
              f"论文: {author.get('paperCount', '?')}")

    # 5. 推荐
    print("\n--- 5. 论文推荐（需提供有效 paper_id）---")
    if paper and paper.get("paperId"):
        recs = get_recommendations_for_paper(paper["paperId"], limit=3)
        for r in recs.get("recommendedPapers", [])[:3]:
            print(f"  - {r.get('title', '?')} ({r.get('year', '?')})")

    # 6. 全文片段搜索（需要 API Key）
    if API_KEY:
        print("\n--- 6. 全文片段搜索 ---")
        snippets = search_snippets("dropout rate 0.1", limit=3)
        for item in snippets.get("data", [])[:3]:
            snip = item.get("snippet", {})
            p = item.get("paper", {})
            print(f"  [{snip.get('section', '?')}] {p.get('title', '?')}")
            print(f"    \"{snip.get('text', '')[:120]}...\"")
    else:
        print("\n--- 6. 全文片段搜索（跳过，需要 API Key）---")

    print("\n✅ 示例执行完毕")


if __name__ == "__main__":
    main()
