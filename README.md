# 自用 Skills 仓库

该仓库包含了我个人使用的一组 Codex / Claude Code 技能，覆盖学术检索与论文速读、科研配图、每日 AI 资讯、读书拆解、代码库入门与源码讲解、技能发现与安装、Markdown 中英混排校对、Beamer / Slidev 演示文稿、东南大学学术汇报、思源笔记与 Hugo 内容同步、思源笔记与 VitePress 内容同步、技术栈入门与系统教程，以及 B 站缓存转换等场景。

当前共包含 19 个技能，统一放在 `skills/` 目录下。每个技能都是一个独立目录，包含必需的 `SKILL.md`，以及可选的 `agents/openai.yaml`、参考资料、脚本或素材。该布局符合 Agent Skills 规范，可直接通过 `npx skills add` 安装。

## 技能列表

| 技能 | 说明 | 是否需要手动配置 |
| --- | --- | --- |
| [ai4scholar](./skills/ai4scholar/) | 综合学术文献检索、分析与管理。覆盖 Semantic Scholar、PubMed、Google Scholar、arXiv、bioRxiv、medRxiv，支持论文搜索、引文追踪、作者画像、PDF 全文、DOI 解析、自动引用标注（Auto-Cite）和科研绘图（Sci-Draw） | 部分功能需要配置 API Key |
| [beamer](./skills/beamer/) | Beamer LaTeX 幻灯片工作流，支持学术报告的创建、编译、审阅、视觉检查、教学性优化、TikZ 图示和论文转幻灯片 | 否 |
| [book-deconstruction](./skills/book-deconstruction/) | 书籍章节级要点提炼与深度解读，生成结构化笔记和思维导图 | 否 |
| [ccf-figure](./skills/ccf-figure/) | 根据 AI/CS 论文内容设计符合顶会与期刊视觉标准的科研配图 | 否 |
| [codebase-onboarding](./skills/codebase-onboarding/) | 分析代码库并生成面向不同受众的入门文档，包括架构概览、关键文件地图、本地启动指南、常见任务手册、调试指南和贡献规范 | 否 |
| [daily-ai-news](./skills/daily-ai-news/) | 聚合和总结最新 AI 新闻，按重大公告、研究论文、产业商业、工具应用、政策伦理等类别生成每日简报，并附原文链接 | 否 |
| [drawio-diagram-builder](./skills/drawio-diagram-builder/) | 创建、复刻和迭代优化可编辑的 draw.io 科研与技术图示 | 否 |
| [find-skills](./skills/find-skills/) | 帮助发现和安装开放技能生态中的 Agent Skills，适合在需要扩展能力、查找已有工作流或推荐可安装技能时使用 | 否 |
| [markdown-cjk-spacing](./skills/markdown-cjk-spacing/) | 检查并修正 Markdown 或纯文本中的中文与英文、ASCII 术语混排间距，以及中英文标点和加粗文本邻近标点的排版细节 | 否 |
| [paper-quickread](./skills/paper-quickread/) | 对本地 PDF 或论文 URL 进行中文速读，重建研究动机、核心思路和验证证据链，并可为 arXiv 论文提取关键原图 | 否 |
| [parse-bilibili](./skills/parse-bilibili/) | 解析 B 站 Android/PC 客户端缓存的 `.m4s` 文件，导出 MP4 视频或纯音频 | 否 |
| [repo-source-explainer](./skills/repo-source-explainer/) | 基于源码证据生成架构导览、模块深度讲解、代码阅读指南或书籍式文档 | 否 |
| [seu-academic-beamer](./skills/seu-academic-beamer/) | 使用内置 SimplePlus Beamer 主题和东南大学 Logo 创建、编译、审阅和润色东南大学学术汇报幻灯片 | 否 |
| [sync-siyuan-hugo](./skills/sync-siyuan-hugo/) | 在思源笔记与 Hugo Markdown 之间双向转换和同步，保留 front matter、提示块和行内数学公式 | 取决于思源笔记接入方式 |
| [sync-siyuan-vitepress](./skills/sync-siyuan-vitepress/) | 在思源笔记与 VitePress 文档之间双向同步，支持路径映射、冲突检测、本地资源复制、自动生成侧边栏和增量状态保存 | 取决于思源笔记接入方式 |
| [siyuan-note](./skills/siyuan-note/) | 按运行平台管理思源笔记：原生 Windows 优先使用内置 `siyuan` CLI，Linux 和 WSL 优先使用 Python HTTP API | Linux/WSL 默认需要 API 配置 |
| [slidev](./skills/slidev/) | 创建和维护面向开发者的 Slidev 网页演示文稿，支持 Markdown、Vue 组件、代码高亮、动画、交互演示和导出 | 否 |
| [tech-stack-quickstart](./skills/tech-stack-quickstart/) | 为指定技术栈生成新手友好的快速入门和用法参考文档 | 否 |
| [tech-stack-tutorial](./skills/tech-stack-tutorial/) | 为指定编程语言、框架、库、数据库、开发工具或平台生成章节化、示例驱动的系统教程 | 否 |

## 使用 `npx skills`

从 Git 仓库安装整个技能仓库（CLI 会发现 `skills/` 下的所有技能）：

```bash
npx skills add https://gitee.com/bowenEI/myskills.git
```

只安装指定技能：

```bash
npx skills add https://gitee.com/bowenEI/myskills.git --skill ai4scholar
```

如果仓库托管在 GitHub，也可以使用 `<owner>/<repo>` 简写。

也可以在本地验证仓库中的技能：

```bash
npx skills add . --list
```

## 手动安装

如需手动使用 Codex / Claude Code 目录，可参考下表：

| Agent | Skill 路径 |
| :---: | --- |
| Codex | `~/.codex/skills` |
| Claude Code | `~/.claude/skills` |

先克隆仓库：

```bash
git clone https://gitee.com/bowenEI/myskills.git
cd myskills
```

再将需要的技能目录复制到对应 Agent 的 Skill 路径。例如：

```bash
cp -R skills/ai4scholar ~/.codex/skills/
# 或
cp -R skills/ai4scholar ~/.claude/skills/
```

## 配置

大多数技能可以直接使用。以下技能在部分功能中需要额外配置：

- `ai4scholar`：如需使用受限接口或更稳定的检索能力，请参考 [ai4scholar/config.example.yaml](./skills/ai4scholar/config.example.yaml) 创建本地 `config.yaml` 并配置 API Key。
- `siyuan-note`：原生 Windows 优先使用内置 `siyuan` CLI，通常无需 API 配置；Linux 和 WSL 优先使用 Python HTTP API，需要参考 [siyuan-note/config.example.yaml](./skills/siyuan-note/config.example.yaml) 创建本地 `config.yaml`，并配置思源笔记 API Token 和当前环境可访问的服务地址。
- `sync-siyuan-hugo`：通过 `siyuan-note` 访问思源笔记，并遵循相同的平台选择规则；如需验证 Hugo 输出，还应准备可用的 Hugo 项目环境。
- `sync-siyuan-vitepress`：通过 `siyuan-note` 访问思源笔记，并遵循相同的平台选择规则；支持 VitePress 和 Teek 主题，如需验证输出，还应准备可用的 VitePress 项目环境。

真实的 `config.yaml` 会被 `.gitignore` 忽略。请不要把 Token、Key 或本地私有服务地址提交到公开仓库。

## 维护

新增技能时，建议同时更新：

1. `skills/<skill-name>/SKILL.md`
2. 本 README 的技能列表
3. 相关 `agents/openai.yaml`、配置示例、脚本、参考资料或素材说明
