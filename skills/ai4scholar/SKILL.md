---
name: ai4scholar
description: "全面的学术文献检索、管理、分析技能。覆盖 Semantic Scholar（2 亿+ 论文）、PubMed（生物医学）、Google Scholar、arXiv、bioRxiv、medRxiv 六大平台。支持论文搜索、引文追踪、作者画像、PDF 下载与全文阅读、DOI 解析、自动引用标注（auto-cite）、科研绘图（sci-draw）。适合做文献综述、查引文、找方法、读全文、写引用。当用户提出学术搜索、论文查找、文献调研、引文分析、科研绘图、DOI 下载、自动引用等需求时，必须使用此技能，即使只是问'帮我搜一些关于 XX 的论文'。"
metadata:
  version: "1.0"
  tags: [academic, literature, search, paper, citation, research, scholar, pubmed, arxiv, biorxiv, medrxiv, DOI, sci-draw]
---

# AI4Scholar 综合学术文献技能

本技能指导你如何使用 6 大学术平台提供的开放 API，完成论文搜索、信息检索、全文获取、引文分析、自动引用标注和科研绘图等任务。

## 配置说明

本技能的部分功能（Semantic Scholar 全文片段搜索、PubMed、Google Scholar、Auto-Cite、Sci-Draw）需要通过 ai4scholar.net 代理 API，需要配置 API Key。

**首次使用配置步骤**：

1. 前往 [ai4scholar.net](https://ai4scholar.net) 注册账号
2. 在个人中心获取 API Key
3. 编辑本技能目录下的 `config.yaml` 文件，填入你的 API Key

**config.yaml 文件路径**：本技能所在目录下的 `config.yaml`
**格式**：
```yaml
apiKey: "你的API-Key"
```

**如何使用配置**：启动 skill 后读取 `config.yaml` 中的 `apiKey` 字段。如果 `apiKey` 为空则提示用户配置。

**免 API Key 的功能**：arXiv 搜索/下载、bioRxiv 搜索/下载、medRxiv 搜索/下载、Semantic Scholar 基础搜索（非 snippet 搜索）、DOI 下载（需网络环境支持）等可直接使用，无需配置。

## 整体原则

- **优先使用开放/免费 API**：arXiv API、Semantic Scholar API（非 snippet 搜索）、PubMed E-utilities、bioRxiv API 都是免费的，优先直接调用
- **ai4scholar.net 代理**：Semantic Scholar 全文片段搜索、PubMed、Google Scholar、Auto-Cite、Sci-Draw 需要通过 ai4scholar.net 的代理 API，需要 API Key
- **读取配置**：当需要使用需要 API Key 的功能时，先读取 `config.yaml` 获取 `apiKey`。如果 `apiKey` 为空，提示用户前往 ai4scholar.net 注册并配置
- **不编造数据**：所有论文信息、作者、引用数等必须来自 API 返回的真实数据
- **区分平台**：每个平台的查询标识符不同（arXiv ID、DOI、PMID、Semantic Scholar ID），不要混用

## 平台 API 速查

### 1. Semantic Scholar API（全学科，2 亿+ 论文）

Semantic Scholar 提供开放 API，**无需 API Key**（但有频率限制）。

**基础 URL**: `https://api.semanticscholar.org/graph/v1`

#### 搜索论文
```
GET /paper/search?query={关键词}&limit={数量}&year={年份范围}&fields={字段列表}
```
- `query`: 搜索关键词（英文）
- `limit`: 1-100，默认 10
- `year`: 格式如 `2020`、`2020-2024`、`2020-`、`-2020`
- `fields`: 控制返回字段，常用字段组合见下方

常用 fields 值：
- `title,abstract,year,citationCount,authors,url,publicationDate,externalIds,fieldsOfStudy,openAccessPdf`
- `title,abstract,authors,year,citationCount,externalIds`

**返回示例**：
```json
{
  "data": [{
    "paperId": "abc123",
    "title": "Attention Is All You Need",
    "year": 2017,
    "citationCount": 50000,
    "authors": [{ "authorId": "1741101", "name": "Ashish Vaswani" }],
    "externalIds": { "ArXiv": "1706.03762", "DOI": "10.xxxx/xxxxx" },
    "openAccessPdf": { "url": "https://..." },
    "abstract": "..."
  }],
  "total": 1234
}
```

#### 论文详情
```
GET /paper/{paper_id}?fields={字段列表}
```
支持多种 ID 格式：
- Semantic Scholar ID: `abc123`
- DOI: `DOI:10.1038/s41586-021-03819-2`
- arXiv: `ARXIV:1706.03762`
- PMID: `PMID:39575807`
- Corpus ID: `CorpusId:12345`

#### 引用查询
- **施引文献**（谁引用了它）：`GET /paper/{paper_id}/citations?limit={}&offset={}`
- **参考文献**（它引用了谁）：`GET /paper/{paper_id}/references?limit={}&offset={}`
- `limit`: 最大 1000，默认 100
- 返回数据包含 `contexts`（引用上下文）、`isInfluential`（是否有影响力）

#### 作者查询
- **搜索作者**: `GET /author/search?query={作者名}&limit={}`
- **作者详情**: `GET /author/{author_id}?fields=name,affiliations,paperCount,citationCount,hIndex`
- **作者论文**: `GET /author/{author_id}/papers?limit={}&offset={}`
- **论文作者**: `GET /paper/{paper_id}/authors?limit={}&offset={}`

#### 批量查询
- **批量论文**: `POST /paper/batch`，body: `{"ids": ["id1", "id2"]}`，最大 500 个
- **批量作者**: `POST /author/batch`，body: `{"ids": ["id1", "id2"]}`，最大 1000 个

#### 全文片段搜索
通过 ai4scholar.net 代理：
```
GET https://ai4scholar.net/graph/v1/snippet/search
Headers: Authorization: Bearer {API_KEY}
Params: query, limit(10-1000), year, minCitationCount, fieldsOfStudy, venue
```
返回匹配的原文段落（~500 字片段），支持按字段、引用数、期刊筛选。

#### 论文推荐
- **基于示例论文推荐**: `POST /recommendations/v1/papers/` body: `{"positivePaperIds": [...], "negativePaperIds": [...]}`
- **单篇相似论文**: `GET /recommendations/v1/papers/forpaper/{paper_id}?limit={}`
- `limit` 最大 500

#### 批量搜索（大量数据爬取）
```
GET /paper/search/bulk?query={}&token={}&year={}
```
返回最多 1000 条结果 + `token` 用于翻页获取更多。

---

### 2. PubMed API（生物医学）

通过 ai4scholar.net 代理访问。

**基础 URL**: `https://ai4scholar.net/pubmed/v1`

需要 API Key（从 ai4scholar.net 获取）。

#### 搜索论文
```
POST /pubmed/v1/paper/search
Body: { "query": "关键词", "limit": 10, "sort": "relevance", "minDate": "2020/01/01", "maxDate": "2024/12/31" }
```
- `sort`: `"relevance"` 或 `"date"`
- `limit`: 最大 100

#### 论文详情
```
GET /pubmed/v1/paper/{pmid}
```

#### 引文查询
- **施引文献**: `GET /pubmed/v1/paper/{pmid}/citations?limit={}`
- **相关文献**: `GET /pubmed/v1/paper/{pmid}/related?limit={}`

#### 批量查询
```
POST /pubmed/v1/paper/batch
Body: { "pmids": ["39575807", "30102808"] }
```

---

### 3. Google Scholar（全学科通用）

通过 ai4scholar.net 代理，需要 API Key。

**基础 URL**: `https://ai4scholar.net/google-scholar/v1`

#### 搜索
```
POST /google-scholar/v1/search
Body: { "query": "关键词", "page": 1, "yearFrom": 2020, "yearTo": 2025 }
```
- 每页 10 条结果，自动翻页
- `max_results` 最大 50
- 返回标题、作者、引用数、摘要、PDF 链接

---

### 4. arXiv API（预印本）

**完全开放**，无需 API Key。

**基础 URL**: `https://export.arxiv.org/api/query`

#### 搜索论文
```
GET /api/query?search_query={关键词}&start={}&max_results={}&sortBy={}&sortOrder=descending
```

参数：
- `search_query`: 支持复杂查询，如 `au:del_maestro AND ti:checkerboard`
  - 字段前缀：`au:` 作者, `ti:` 标题, `abs:` 摘要, `cat:` 分类
  - `AND`、`OR`、`ANDNOT` 逻辑
- `max_results`: 最大 50
- `sortBy`: `relevance`（默认）、`lastUpdatedDate`、`submittedDate`
- 日期过滤: `query AND submittedDate:[YYYYMMDD0000 TO 99991231]`

**返回格式**: Atom XML，需解析 `entry` 标签：
- `<title>`: 标题
- `<summary>`: 摘要
- `<id>`: 含 arXiv ID（如 `http://arxiv.org/abs/1706.03762`）
- `<author><name>`: 作者
- `<published>`: 发布日期
- `<link title="pdf">`: PDF 链接
- `<category term="">`: 分类

#### PDF 下载
- 下载 URL: `https://arxiv.org/pdf/{paper_id}.pdf`
- 摘要页 URL: `https://arxiv.org/abs/{paper_id}`

---

### 5. bioRxiv / medRxiv API（生物学/医学预印本）

**完全开放**，无需 API Key。

**基础 URL**: `https://api.biorxiv.org/details/{server}/{start_date}/{end_date}/{cursor}`

#### 搜索论文（按分类 + 日期范围）
```
GET /details/{server}/{start_date}/{end_date}/0?category={category}
```
- `server`: `biorxiv` 或 `medrxiv`
- `start_date`/`end_date`: YYYY-MM-DD 格式
- `category`: 分类名（如 `cell_biology`、`neuroscience`），见官网分类列表
- 每页最多 100 条，通过 `cursor`（0, 100, 200...）翻页

**返回格式**:
```json
{
  "collection": [{
    "doi": "10.1101/2024.01.01.123456",
    "title": "Paper Title",
    "authors": "Author1; Author2",
    "abstract": "...",
    "date": "2024-01-01",
    "category": "cell_biology",
    "version": "1"
  }]
}
```

#### PDF 下载
- bioRxiv URL: `https://www.biorxiv.org/content/{doi}v{version}.full.pdf`
- medRxiv URL: `https://www.medrxiv.org/content/{doi}v{version}.full.pdf`
- 摘要页: `https://www.biorxiv.org/content/{doi}v{version}`

---

### 6. DOI 直接下载

通过 DOI 直接从出版商下载 PDF。**需要校园网/IP 权限才能访问付费论文**。

#### 下载流程
1. 通过 `https://doi.org/{doi}` 重定向到出版商页面
2. 使用 `Accept: application/pdf` 请求头尝试内容协商
3. 如果返回 HTML（登录页/摘要页），尝试各出版商特有 PDF 路径：
   - **Elsevier/ScienceDirect**: `/pdfft?isDTMRedir=true&download=true`
   - **Springer/Nature**: `/content/pdf/{doi}.pdf`
   - **Wiley**: `/doi/pdfdirect/{doi}`
   - **IEEE**: `/stampPDF/getPDF.jsp?tp=&arnumber={number}`
   - **Taylor & Francis**: `/doi/pdf/{doi}`
   - **MDPI**: `/pdf` 替换 `/htm`
   - **ACM**: `/doi/pdf/{doi}`
   - **ACS**: `/doi/pdf/{doi}`
   - **RSC**: `/articlepdf/` 替换 `/articlelanding/`

---

## PDF 全文读取

支持从 PDF 提取文本。当用户需要阅读论文全文时：

1. **先获取 PDF URL**（通过对应平台的下载工具）
2. **下载并提取文本**：使用代码下载 PDF 并解析文本（pdf-parse 库）
3. **返回文本内容**给用户，或进行摘要、翻译、分析

> **注意**：带有插图、公式的 PDF 文本提取质量有限。对于 arXiv 论文，可以直接提取到 LaTeX 源码级的文本。

---

## 自动引用标注 (Auto-Cite)

通过 ai4scholar.net API 自动为学术文本添加真实引用。

**接口**: `POST https://ai4scholar.net/api/proxy/auto-cite`
**Headers**: `Authorization: Bearer {API_KEY}`

**请求参数**:
| 参数 | 必填 | 说明 |
|------|------|------|
| text | 是 | 待标注的学术文本（100-10000 字符） |
| mode | 否 | `"auto"`（自动检测引用位置）或 `"manual"`（用 `[CITE]` 标记位置） |
| minCitations | 否 | 最少引用数（默认 10） |
| field | 否 | 学术领域（如 `"computer science"`） |
| yearPreference | 否 | 偏好引用年份 |
| excludePreprints | 否 | 排除预印本 |
| excludeConferences | 否 | 排除会议论文 |
| citationStyle | 否 | 格式: `ieee`, `apa`, `vancouver`, `nature`, `numbered` |

**处理时间**: 20-60 秒（SSE 流式响应）

**使用场景**：
- 用户写了 Introduction/Related Work 段落，需要添加真实引用
- 需要生成参考文献列表和 BibTeX
- 已有草稿需要补全引用标注

**用法**：
1. 用户粘贴学术文本
2. 调用 auto-cite API
3. 返回标注后的文本（带 `[1]`, `[2]` 标记）
4. 同时返回参考文献列表（含 DOI、标题、年份、期刊等）
5. 返回 BibTeX 格式的完整引用数据

**重要**：auto-cite 属于耗时操作（20-60 秒），调用前告知用户需要等待。

---

## 科研绘图 (Sci-Draw)

通过 ai4scholar.net API 生成或处理科研图片。

**接口**: `POST https://ai4scholar.net/api/proxy/nano/generate`
**Headers**: `Authorization: Bearer {API_KEY}`

**action 类型**:
| action | 说明 | 需图片 |
|--------|------|--------|
| `smart` | 智能模式：自动优化提示词，支持中文（推荐） | 否 |
| `generate` | 文生图 | 否 |
| `edit` | 编辑修改已有图片 | 是 |
| `style` | 风格迁移 | 是 |
| `compose` | 合并多张图片 | 是（≥2） |
| `iterate` | 自动审核并优化 | 是 |
| `critic` | 专家评审（返回文字评审） | 是 |
| `svg` | 生成 SVG 矢量图 | 否 |
| `vectorize` | 将 PNG/JPG 转为 PDF+PPTX | 是 |

**模型选择**:
- `flash`: 快速
- `flash31`: 均衡（默认）
- `pro`: 高质量
- `gptimage`: GPT Image 2，细节最佳

**参数**:
- `prompt`: 图片描述（smart 模式下支持中文）
- `imageSize`: `"1K"`, `"2K"`（默认）, `"4K"`
- `aspectRatio`: `"1:1"`, `"16:9"`, `"4:3"`, `"3:4"`, `"9:16"`
- `stylePreset`: 风格预设
- `lang`: `"en"` 或 `"zh"`

**返回**:
- `imageUrl`: 生成图片 URL
- `svgCode` / `svgUrl`: SVG 相关
- `pdfUrl` / `pptxUrl`: 矢量化输出

**重要规则**：
- 调用 `sci_draw` 前，**必须先告知用户**"正在生成科研图片，大约需要 30-60 秒，请稍候..."
- 生成后将 `imageUrl` 以图片形式展示给用户
- `critic` 模式只返回评审文字，无图片
- 需要 API Key

---

## 工作流指南

### 文献调研

```
用户需求 → 确定搜索平台 → 调用搜索 API → 获取论文详情 → 整理结果
```

1. 根据用户需求选择平台：
   - 全学科通用 → Semantic Scholar
   - 生物医学 → PubMed
   - 最新预印本 → arXiv / bioRxiv / medRxiv
   - 需要引文分析 → Semantic Scholar（支持施引/参考文献）
2. 搜索后提供摘要：论文标题、作者、年份、引用数、摘要要点
3. 如需深入阅读：获取 PDF 并提取全文

### 引文追踪

```
已知某篇关键论文 → 查施引文献 → 评估影响力 → 查参考文献 → 追溯研究脉络
```

- 使用 Semantic Scholar 的 citations/references API
- 关注 `isInfluential` 标记，可以快速找到重要引文
- 引用上下文 `contexts` 告诉你"别人怎么引用这篇论文"

### 作者画像

```
作者名 → 搜索 Semantic Scholar 作者 → 获取 h-index/论文数/引用数 → 列出代表作 → 分析研究方向
```

- 使用 Semantic Scholar 作者 API
- h-index、论文总数、总引用数可快速评估作者影响力
- 查看作者的合作者网络（通过论文作者列表）

### 全文阅读

```
论文 ID/DIO → 获取 PDF URL → 下载 PDF → 提取文本 → 分析/翻译/摘要
```

如果用户多次请求不同论文内容，注意保持回答简洁，不要在每个回答中都重复列出所有搜索结果。

### 自动引用

```
用户粘贴学术段落 → 调用 auto-cite API → 返回带标注文本 + 参考文献列表 + BibTeX
```

始终优先使用 API 返回的真实数据，不要自己编造引用。

---

## 输出规范

### 搜索结果展示格式

```
**搜索概况**
在 {total} 篇论文中找到「{query}」相关结果。来源：{platform}。

**核心论文**
#️⃣ {序号} **{标题}**
- 作者：{authors} | 年份：{year} | 引用：{citationCount} | 来源：{platform}
- 摘要：{abstract（200 字以内摘要）}
- 链接：[Semantic Scholar](链接) | [arXiv](链接) | [PDF](链接)

（更多论文以列表形式展示）
```

### 引文分析格式

```
**{论文标题}**
- 施引文献数：{citationCount}
- 有影响力的引用：{count}

**关键引文**
1️⃣ {标题}（{年份}）- {作者} - {引用数}
   引用上下文："{contexts}"
```

### 通用约束
- 所有数据必须来自 API 真实返回
- 禁止编造论文标题、作者、引用数
- 每篇提到的论文附上可访问的链接
- API 出错时只提示错误，不要用训练数据补全
- 搜索结果为空时，建议调整关键词或筛选条件
- 中文用户优先用中文回复，但 API 查询参数保持英文
