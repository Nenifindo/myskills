"""
AI4Scholar — DOI 论文下载示例

通过 DOI 从出版商直接下载 PDF。需要网络环境支持（校园网/IP 权限访问付费论文）。

开源（OA）论文可以直接下载。付费论文需要所在机构有订阅权限。
"""

import os
import sys
import io
import urllib.request
import urllib.error
import time

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/pdf,application/x-pdf,*/*",
}

TIMEOUT_MS = 120_000


def fetch_with_headers(url, accept="application/pdf"):
    """带浏览器头部的请求"""
    headers = dict(BROWSER_HEADERS)
    headers["Accept"] = accept
    req = urllib.request.Request(url, headers=headers)
    return urllib.request.urlopen(req, timeout=TIMEOUT_MS // 1000)


def is_pdf_content(data):
    """检查是否为 PDF 内容（检查魔术字节）"""
    return len(data) > 0 and data[0] == 0x25  # '%'


def build_pdf_candidates(landing_url):
    """
    根据出版商页面 URL 生成可能的 PDF 链接。
    覆盖主流学术出版商。
    """
    from urllib.parse import urlparse
    candidates = []
    u = urlparse(landing_url)
    hostname = u.hostname or ""

    # Elsevier / ScienceDirect
    if "sciencedirect.com" in hostname:
        candidates.append(f"{landing_url}/pdfft?isDTMRedir=true&download=true")

    # Springer / Nature
    if "springer.com" in hostname or "nature.com" in hostname:
        import re
        m = re.search(r"/articles?/(10\.\d+/\S+)", landing_url)
        if m:
            candidates.append(f"https://{hostname}/content/pdf/{m.group(1)}.pdf")

    # Wiley
    if "onlinelibrary.wiley.com" in hostname:
        candidates.append(landing_url.replace("/doi/", "/doi/pdfdirect/"))

    # Taylor & Francis
    if "tandfonline.com" in hostname:
        candidates.append(landing_url.replace("/doi/full/", "/doi/pdf/"))

    # MDPI
    if "mdpi.com" in hostname and landing_url.endswith("/htm"):
        candidates.append(landing_url.replace("/htm", "/pdf"))

    # IEEE
    if "ieeexplore.ieee.org" in hostname:
        import re
        arnumber = re.search(r"/document/(\d+)", u.path)
        if arnumber:
            candidates.append(
                f"https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&arnumber={arnumber.group(1)}"
            )

    # ACM
    if "dl.acm.org" in hostname:
        candidates.append(landing_url.replace("/doi/", "/doi/pdf/"))

    # ACS
    if "pubs.acs.org" in hostname:
        candidates.append(landing_url.replace("/doi/", "/doi/pdf/"))

    # RSC
    if "pubs.rsc.org" in hostname:
        candidates.append(landing_url.replace("/articlelanding/", "/articlepdf/"))

    # 通用: 追加 .pdf
    if not landing_url.endswith(".pdf"):
        candidates.append(landing_url + ".pdf")

    return candidates


def resolve_doi(doi):
    """
    通过 DOI 解析并下载 PDF。

    策略:
    1. 用 Accept: application/pdf 请求 doi.org 进行内容协商
    2. 如果返回 PDF，直接返回
    3. 如果返回 HTML（摘要页），尝试各出版商的 PDF 路径
    """
    doi_url = f"https://doi.org/{doi}"

    print(f"  解析 DOI: {doi_url}")

    # 第一步：内容协商
    try:
        resp = fetch_with_headers(doi_url)
    except urllib.error.HTTPError as e:
        return {"success": False, "error": f"HTTP {e.code}", "doi": doi}

    final_url = resp.url
    content_type = resp.headers.get("Content-Type", "")
    data = resp.read()

    if content_type and ("pdf" in content_type or "octet-stream" in content_type):
        if is_pdf_content(data):
            return {"success": True, "pdf_data": data, "final_url": final_url, "doi": doi}

    print(f"  内容协商返回 HTML，尝试出版商 PDF 路径...")
    print(f"  落地页: {final_url}")

    # 第二步：尝试各出版商 PDF 路径
    candidates = build_pdf_candidates(final_url)
    for candidate in candidates:
        try:
            print(f"  尝试: {candidate}")
            pdf_resp = fetch_with_headers(candidate)
            ct = pdf_resp.headers.get("Content-Type", "")
            if "pdf" not in ct and "octet-stream" not in ct:
                continue
            pdf_data = pdf_resp.read()
            if is_pdf_content(pdf_data):
                return {"success": True, "pdf_data": pdf_data, "final_url": candidate, "doi": doi}
        except Exception:
            continue

    return {
        "success": False,
        "error": "无法获取 PDF。论文可能需要机构订阅权限。",
        "final_url": final_url,
        "doi": doi,
    }


def download_by_doi(doi, output_dir="."):
    """通过 DOI 下载论文 PDF"""
    result = resolve_doi(doi)

    if not result["success"]:
        print(f"  ✗ 下载失败: {result.get('error', '未知错误')}")
        return None

    pdf_data = result["pdf_data"]
    safe_doi = doi.replace("/", "_").replace(":", "_")
    output_path = os.path.join(output_dir, f"{safe_doi}.pdf")

    with open(output_path, "wb") as f:
        f.write(pdf_data)

    print(f"  ✓ 已保存: {output_path} ({len(pdf_data)} bytes)")
    print(f"    来源: {result['final_url']}")
    return output_path


def extract_text_from_pdf(pdf_path):
    """从 PDF 提取文本（需要安装 pdfminer.six）"""
    try:
        from pdfminer.high_level import extract_text
        text = extract_text(pdf_path)
        return text
    except ImportError:
        return None


def main():
    print("=" * 60)
    print("AI4Scholar — DOI 论文下载示例")
    print("=" * 60)
    print("\n注意: 付费论文需要所在机构有订阅权限或校园网环境。")
    print("      以下仅演示 OA 论文。\n")

    # 示例：开放获取论文
    test_dois = [
        "10.1038/s41586-021-03819-2",  # 可能需要 Nature 订阅
        "10.48550/arXiv.1706.03762",   # arXiv 论文，开放获取
    ]

    for doi in test_dois:
        print(f"\n--- DOI: {doi} ---")
        result = download_by_doi(doi)
        if result:
            # 尝试提取文本
            text = extract_text_from_pdf(result)
            if text:
                print(f"  文本长度: {len(text)} 字符")
                print(f"  文本预览: {text[:200]}...")
            else:
                print("  提示: 安装 pdfminer.six 进行文本提取: pip install pdfminer.six")
        print()

    print("✅ 示例执行完毕")


if __name__ == "__main__":
    main()
