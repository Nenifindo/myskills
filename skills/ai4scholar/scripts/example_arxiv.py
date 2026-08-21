"""
AI4Scholar — arXiv API 调用示例

arXiv 提供完全开放的 API，无需 API Key。

搜索接口: GET https://export.arxiv.org/api/query
PDF 下载: https://arxiv.org/pdf/{paper_id}.pdf
摘要页面: https://arxiv.org/abs/{paper_id}
"""

import os
import sys
import json
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlencode, quote


ARXIV_API = "https://export.arxiv.org/api/query"
NS = {"atom": "http://www.w3.org/2005/Atom"}


def parse_atom_xml(xml_text):
    """解析 arXiv Atom XML 为结构化数据"""
    papers = []
    root = ET.fromstring(xml_text)

    for entry in root.findall("atom:entry", NS):
        title = entry.findtext("atom:title", "", NS).replace("\n", " ").strip()
        summary = entry.findtext("atom:summary", "", NS).replace("\n", " ").strip()
        published = entry.findtext("atom:published", "", NS)
        updated = entry.findtext("atom:updated", "", NS)

        id_url = entry.findtext("atom:id", "", NS)
        arxiv_id = re.sub(r"http://arxiv.org/abs/|v\d+$", "", id_url)

        authors = []
        for author in entry.findall("atom:author", NS):
            name = author.findtext("atom:name", "", NS).strip()
            if name:
                authors.append(name)

        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        for link in entry.findall("atom:link", NS):
            if link.get("title") == "pdf":
                pdf_url = link.get("href", pdf_url)
                break

        categories = []
        for cat in entry.findall("atom:category", NS):
            term = cat.get("term", "")
            if term:
                categories.append(term)

        papers.append({
            "title": title,
            "authors": authors,
            "abstract": summary,
            "arxiv_id": arxiv_id,
            "pdf_url": pdf_url,
            "published": published,
            "updated": updated,
            "categories": categories,
        })

    return papers


def search_arxiv(query, max_results=10, sort_by="relevance", date_from=None):
    """
    搜索 arXiv 论文

    参数:
        query: 搜索关键词（支持 au:作者名、ti:标题、abs:摘要、cat:分类）
        max_results: 最大结果数（1-50）
        sort_by: "relevance" / "lastUpdatedDate" / "submittedDate"
        date_from: 起始日期 YYYY-MM-DD
    """
    search_query = query
    if date_from:
        d = date_from.replace("-", "")
        search_query = f"{query} AND submittedDate:[{d}0000 TO 99991231]"

    params = {
        "search_query": search_query,
        "start": "0",
        "max_results": str(min(max_results, 50)),
        "sortBy": sort_by,
        "sortOrder": "descending",
    }

    import urllib.request
    url = f"{ARXIV_API}?{urlencode(params)}"
    print(f"  GET {url}")

    req = urllib.request.Request(url, headers={"User-Agent": "ai4scholar-python-example/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        xml_text = resp.read().decode()

    papers = parse_atom_xml(xml_text)
    return papers


def get_pdf_url(arxiv_id):
    """获取 arXiv 论文 PDF 下载链接"""
    return {
        "paper_id": arxiv_id,
        "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf",
        "abs_url": f"https://arxiv.org/abs/{arxiv_id}",
    }


def download_pdf(arxiv_id, output_dir="."):
    """下载 arXiv 论文 PDF 到本地"""
    import urllib.request

    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    output_path = os.path.join(output_dir, f"{arxiv_id}.pdf")

    print(f"  下载中: {pdf_url}")
    req = urllib.request.Request(pdf_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = resp.read()

    with open(output_path, "wb") as f:
        f.write(data)

    print(f"  已保存: {output_path} ({len(data)} bytes)")
    return output_path


def advanced_search_examples():
    """复杂查询示例"""
    examples = [
        ("作者+标题", 'au:del_maestro AND ti:checkerboard'),
        ("分类+关键词", 'cat:cs.AI AND (ti:transformer OR ti:attention)'),
        ("多作者", 'au:hinton AND au:lecun'),
        ("作者+摘要关键词", 'au:goodfellow AND abs:generative AND abs:adversarial'),
        ("排除", 'cat:stat.ML ANDNOT cat:cs.AI'),
    ]
    print("\n  复杂查询示例：")
    for label, q in examples:
        print(f"    {label}: {q}")


def main():
    print("=" * 60)
    print("AI4Scholar — arXiv API 示例（无需 API Key）")
    print("=" * 60)

    # 1. 基础搜索
    print("\n--- 1. 搜索论文 ---")
    papers = search_arxiv("graph neural network", max_results=3)
    print(f"搜索到 {len(papers)} 篇论文\n")
    for i, p in enumerate(papers, 1):
        print(f"  #{i} {p['title']}")
        print(f"     作者: {', '.join(p['authors'][:4])}{' ...' if len(p['authors']) > 4 else ''}")
        print(f"     分类: {', '.join(p['categories'][:3])}")
        print(f"     PDF: {p['pdf_url']}")
        print(f"     摘要: {p['abstract'][:150]}...\n")

    # 2. 按日期排序
    print("--- 2. 按提交日期排序 ---")
    papers = search_arxiv("machine learning", max_results=3, sort_by="submittedDate")
    for p in papers:
        print(f"  [{p['published'][:10]}] {p['title'][:80]}")

    # 3. 日期过滤
    print("\n--- 3. 日期过滤（2025 年后）---")
    papers = search_arxiv("quantum computing", max_results=3, date_from="2025-01-01")
    for p in papers:
        print(f"  [{p['published'][:10]}] {p['title'][:80]}")

    # 4. PDF 下载链接
    print("\n--- 4. PDF 下载链接 ---")
    info = get_pdf_url("1706.03762")
    print(f"  论文 ID: {info['paper_id']}")
    print(f"  摘要页: {info['abs_url']}")
    print(f"  PDF: {info['pdf_url']}")

    # 5. 复杂查询
    print("\n--- 5. 复杂查询语法 ---")
    advanced_search_examples()

    print("\n✅ 示例执行完毕")


if __name__ == "__main__":
    main()
