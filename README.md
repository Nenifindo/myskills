# 自用 Skills 仓库

该仓库包含了我个人使用的一组 Codex / Claude Code / WorkBuddy 技能，覆盖学术检索、论文研读、每日 AI 资讯、读书拆解、代码库入门文档、技能发现与安装、Beamer / Slidev 演示文稿、东南大学学术汇报模板、笔记管理、技术栈入门和 B 站缓存转换等场景。

当前技能统一存放在 [.agents/skills](./.agents/skills/) 目录中。

## 技能列表

| 技能 | 说明 | 是否需要手动配置 |
|------|------|------------------|
| [ai4scholar](./.agents/skills/ai4scholar/) | 综合学术文献检索、分析、管理。覆盖 Semantic Scholar、PubMed、Google Scholar、arXiv、bioRxiv、medRxiv，支持论文搜索、引文追踪、作者画像、PDF 全文、DOI 解析、自动引用标注 (Auto-Cite)、科研绘图 (Sci-Draw) | 部分功能需要配置 API Key |
| [beamer](./.agents/skills/beamer/) | Beamer LaTeX 幻灯片工作流，支持学术报告的创建、编译、审阅、视觉检查、教学性优化、TikZ 图示和论文转 slides | 否 |
| [parse-bilibili](./.agents/skills/parse-bilibili/) | 解析 B 站 Android/PC 客户端缓存的 .m4s 文件，导出 MP4 视频或纯音频 | 否 |
| [book-deconstruction](./.agents/skills/book-deconstruction/) | 书籍章节级要点提炼与深度解读，生成结构化笔记和思维导图 | 否 |
| [codebase-onboarding](./.agents/skills/codebase-onboarding/) | 分析代码库并生成面向不同受众的入门文档，包括架构概览、关键文件地图、本地启动指南、常见任务手册、调试指南和贡献规范 | 否 |
| [daily-ai-news](./.agents/skills/daily-ai-news/) | 聚合和总结最新 AI 新闻，按重大公告、研究论文、产业商业、工具应用、政策伦理等类别生成每日简报，并附原文链接 | 否 |
| [find-skills](./.agents/skills/find-skills/) | 帮助发现和安装开放技能生态中的 Agent Skills，适合在需要扩展能力、查找已有工作流或推荐可安装技能时使用 | 否 |
| [paper-parse](./.agents/skills/paper-parse/) | 对学术论文 PDF 或 URL 进行双模式深度研读，生成面向研究者的专业解析和面向快速理解的核心逻辑提炼 | 否 |
| [seu-academic-beamer](./.agents/skills/seu-academic-beamer/) | 使用内置 SimplePlus Beamer 主题和东南大学 Logo 创建、编译、审阅和润色东南大学学术汇报幻灯片 | 否 |
| [siyuan-note](./.agents/skills/siyuan-note/) | SiYuan Note (思源笔记) API 客户端 — 完整的笔记本、文档和块管理 | 需要配置 API Token |
| [slidev](./.agents/skills/slidev/) | 创建和维护面向开发者的 Slidev 网页演示文稿，支持 Markdown、Vue 组件、代码高亮、动画、交互演示和导出 | 否 |
| [tech-stack-quickstart](./.agents/skills/tech-stack-quickstart/) | 为指定技术栈生成新手友好的快速入门和用法参考文档 | 否 |

## 安装

首先，克隆该仓库到本地：

```bash
git clone https://gitee.com/bowenEI/myskills.git
cd myskills
```

然后，根据你使用的智能体应用，执行相应的安装命令。以下命令会用符号链接把本仓库的 `.agents/skills` 目录挂载到目标应用的技能目录中。

> 注意：下面的命令会替换目标位置已有的 `skills` 目录。如果你已有自定义技能，建议先备份或手动合并。

### Codex

Linux/WSL:

```bash
rm -rf ~/.codex/skills
mkdir -p ~/.codex
ln -s $(pwd)/.agents/skills ~/.codex/skills
```

Windows:

```powershell
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $env:USERPROFILE\.codex\skills
New-Item -ItemType SymbolicLink -Path $env:USERPROFILE\.codex\skills -Target (Join-Path (Get-Location) ".agents/skills")
```

### Claude Code

Linux/WSL:

```bash
rm -rf ~/.claude/skills
mkdir -p ~/.claude
ln -s $(pwd)/.agents/skills ~/.claude/skills
```

Windows:

```powershell
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $env:USERPROFILE\.claude\skills
New-Item -ItemType SymbolicLink -Path $env:USERPROFILE\.claude\skills -Target (Join-Path (Get-Location) ".agents/skills")
```

### WorkBuddy

Windows:

```powershell
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $env:USERPROFILE\.workbuddy\skills
New-Item -ItemType SymbolicLink -Path $env:USERPROFILE\.workbuddy\skills -Target (Join-Path (Get-Location) ".agents/skills")
```

### 通用 Agent 目录

Linux/WSL:

```bash
rm -rf ~/.agent/skills
mkdir -p ~/.agent
ln -s $(pwd)/.agents/skills ~/.agent/skills
```

Windows:

```powershell
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $env:USERPROFILE\.agent\skills
New-Item -ItemType SymbolicLink -Path $env:USERPROFILE\.agent\skills -Target (Join-Path (Get-Location) ".agents/skills")
```

## 配置

大多数技能可以直接使用。以下技能在部分功能中需要额外配置：

- `ai4scholar`：如需使用受限接口或更稳定的检索能力，请参考 [.agents/skills/ai4scholar/config.yaml.example](./.agents/skills/ai4scholar/config.yaml.example) 创建本地 `config.yaml` 并配置 API Key。
- `siyuan-note`：使用前请参考 [.agents/skills/siyuan-note/config.example.yaml](./.agents/skills/siyuan-note/config.example.yaml) 创建本地 `config.yaml`，并配置思源笔记 API Token 和服务地址。

真实的 `config.yaml` 会被 `.gitignore` 忽略。请不要把 Token、Key 或本地私有服务地址提交到公开仓库。

## 维护

新增技能时，建议同时更新：

1. `.agents/skills/<skill-name>/SKILL.md`
2. 本 README 的技能列表
3. 相关 `AGENTS.md`、配置示例、脚本或素材说明
