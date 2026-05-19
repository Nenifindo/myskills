"""
AI4Scholar — bioRxiv / medRxiv API 调用示例

完全开放，无需 API Key。

API 文档: https://api.biorxiv.org/details
搜索接口: GET https://api.biorxiv.org/details/{server}/{start_date}/{end_date}/{cursor}
PDF 下载: https://www.{server}.org/content/{doi}v{version}.full.pdf
"""

import os
import sys
import json
import urllib.request
import urllib.error
import time
from datetime import datetime, timedelta


def search_rxiv(server, category, max_results=10, days=30):
    """
    搜索 bioRxiv 或 medRxiv 预印本

    参数:
        server: "biorxiv" 或 "medrxiv"
        category: 分类名（如 "cell_biology", "neuroscience", "bioinformatics"）
        max_results: 最大结果数
        days: 向前搜索的天数
    """
    now = datetime.now()
    start = now - timedelta(days=days)
    fmt = lambda d: d.strftime("%Y-%m-%d")
    category_fmt = category.lower().replace(" ", "_")

    papers = []
    cursor = 0

    while len(papers) < max_results:
        url = f"https://api.biorxiv.org/details/{server}/{fmt(start)}/{fmt(now)}/{cursor}?category={category_fmt}"

        req = urllib.request.Request(url, headers={"User-Agent": "ai4scholar-python-example/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if papers:
                break
            raise

        items = data.get("collection", [])
        if not items:
            break

        for item in items:
            if len(papers) >= max_results:
                break
            papers.append({
                "paper_id": item.get("doi"),
                "title": item.get("title"),
                "authors": item.get("authors", "").split("; ") if item.get("authors") else [],
                "abstract": item.get("abstract"),
                "url": f"https://www.{server}.org/content/{item.get('doi')}v{item.get('version', '1')}",
                "pdf_url": f"https://www.{server}.org/content/{item.get('doi')}v{item.get('version', '1')}.full.pdf",
                "published": item.get("date"),
                "category": item.get("category"),
                "doi": item.get("doi"),
                "source": server,
            })

        if len(items) < 100:
            break
        cursor += 100

    return papers


def search_biorxiv(category, max_results=10, days=30):
    """搜索 bioRxiv"""
    return search_rxiv("biorxiv", category, max_results, days)


def search_medrxiv(category, max_results=10, days=30):
    """搜索 medRxiv"""
    return search_rxiv("medrxiv", category, max_results, days)


def get_pdf_info(server, doi, version="1"):
    """获取 PDF 下载信息"""
    return {
        "pdf_url": f"https://www.{server}.org/content/{doi}v{version}.full.pdf",
        "abs_url": f"https://www.{server}.org/content/{doi}v{version}",
        "doi": doi,
    }


CATEGORIES = {
    "biorxiv": [
        "cell_biology", "neuroscience", "bioinformatics", "genetics",
        "evolutionary_biology", "microbiology", "immunology",
        "cancer_biology", "biochemistry", "molecular_biology",
        "biophysics", "systems_biology", "ecology",
        "developmental_biology", "plant_biology", "zoology",
        "paleontology", "genomics", "synthetic_biology",
        "pathology", "pharmacology", "epidemiology",
    ],
    "medrxiv": [
        "infectious_diseases", "epidemiology", "cardiovascular_medicine",
        "neurology", "public_health", "health_policy",
        "health_informatics", "immunology", "nutrition",
        "mental_health", "oncology", "surgery",
        "pediatrics", "emergency_medicine", "genetics",
        "pharmacology", "environmental_health",
    ],
}


def list_categories(server="biorxiv"):
    """列出可用的分类"""
    print(f"\n  {server} 可用分类（共 {len(CATEGORIES.get(server, []))} 个）:")
    for c in CATEGORIES.get(server, []):
        print(f"    - {c}")


def main():
    print("=" * 60)
    print("AI4Scholar — bioRxiv / medRxiv API 示例（无需 API Key）")
    print("=" * 60)

    # 1. 搜索 bioRxiv
    print("\n--- 1. bioRxiv 搜索 ---")
    papers = search_biorxiv("cell_biology", max_results=3, days=30)
    print(f"搜索到 {len(papers)} 篇细胞生物学预印本（近 30 天）\n")
    for i, p in enumerate(papers, 1):
        authors = p["authors"][:4]
        author_str = ", ".join(authors) + (" ..." if len(p["authors"]) > 4 else "")
        print(f"  #{i} {p['title']}")
        print(f"     作者: {author_str}")
        print(f"     日期: {p['published']}")
        print(f"     分类: {p['category']}")
        print(f"     DOI: {p['doi']}")
        print(f"     PDF: {p['pdf_url']}")
        print(f"     摘要: {p['abstract'][:150]}...\n")

    # 2. 搜索 medRxiv
    print("--- 2. medRxiv 搜索 ---")
    papers = search_medrxiv("epidemiology", max_results=3, days=30)
    print(f"搜索到 {len(papers)} 篇流行病学预印本（近 30 天）\n")
    for i, p in enumerate(papers, 1):
        print(f"  #{i} {p['title']}")
        print(f"     作者: {', '.join(p['authors'][:4])}")
        print(f"     DOI: {p['doi']}\n")

    # 3. 列出可用分类
    print("--- 3. 可用分类 ---")
    list_categories("biorxiv")

    print("\n✅ 示例执行完毕")


if __name__ == "__main__":
    main()
