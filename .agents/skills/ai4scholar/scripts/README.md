# AI4Scholar Python 示例脚本

本目录包含 AI4Scholar 各平台 API 的 Python 调用示例。

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置 API Key（使用需要 Key 的功能时才需要）
# 编辑 ../config.yaml，填入 apiKey
```

## 脚本列表

| 脚本 | 平台 | 是否需要 API Key | 说明 |
|------|------|------------------|------|
| `example_semantic_scholar.py` | Semantic Scholar | 部分需要 | 搜索、详情、引文、作者、推荐、批量、全文片段、PDF |
| `example_pubmed.py` | PubMed | 是 | 搜索、详情、施引、相关、批量 |
| `example_google_scholar.py` | Google Scholar | 是 | 搜索（含年份过滤、自动翻页） |
| `example_arxiv.py` | arXiv | 否 | 搜索（Atom XML）、PDF 下载、日期过滤 |
| `example_biorxiv.py` | bioRxiv/medRxiv | 否 | 按分类+日期搜索、PDF 下载 |
| `example_doi.py` | DOI | 否 | DOI 解析、PDF 下载（含出版商路径策略） |
| `example_auto_cite.py` | Auto-Cite | 是 | 自动引用标注（SSE 流式） |
| `example_sci_draw.py` | Sci-Draw | 是 | 科研图片生成、SVG、矢量化 |

## 运行示例

```bash
# 直接运行对应的脚本
python example_arxiv.py
python example_semantic_scholar.py

# 需要 API Key 的脚本会自动读取 ../config.yaml
python example_auto_cite.py
```

## 免 API Key 的功能

arXiv、bioRxiv、medRxiv、DOI 下载、Semantic Scholar 基础搜索/详情/引文/作者 等使用开放 API，无需配置即可使用。

## 注意事项

- DOI 下载脚本中的付费论文需要机构订阅权限或校园网环境
- Auto-Cite 处理需要 20-60 秒（SSE 流式响应）
- Sci-Draw 生成需要 30-60 秒
- 各 API 有频率限制，脚本已内置 429 重试逻辑
