# 自用 Skills 仓库

该仓库包含了我个人使用的一组 Codex / Claude Code / OpenClaw / Hermes Agent 技能，覆盖学术检索、论文研读、每日 AI 资讯、读书拆解、代码库入门文档、笔记管理、技术栈入门和 B 站缓存转换等场景。

## 技能列表

| 技能 | 说明 | 是否需要手动配置 |
|------|------|------------------|
| [ai4scholar](./skills/ai4scholar/) | 综合学术文献检索、分析、管理。覆盖 Semantic Scholar、PubMed、Google Scholar、arXiv、bioRxiv、medRxiv，支持论文搜索、引文追踪、作者画像、PDF 全文、DOI 解析、自动引用标注 (Auto-Cite)、科研绘图 (Sci-Draw) | 部分功能需要配置 API Key |
| [bilibili-cache-to-mp4](./skills/bilibili-cache-to-mp4/) | 将 B 站 Android/PC 客户端缓存的 .m4s 文件转换为可播放的 MP4 视频 | 否 |
| [book-deconstruction](./skills/book-deconstruction/) | 书籍章节级要点提炼与深度解读，生成结构化笔记和思维导图 | 否 |
| [codebase-onboarding](./skills/codebase-onboarding/) | 分析代码库并生成面向不同受众的入门文档，包括架构概览、关键文件地图、本地启动指南、常见任务手册、调试指南和贡献规范 | 否 |
| [daily-ai-news](./skills/daily-ai-news/) | 聚合和总结最新 AI 新闻，按重大公告、研究论文、产业商业、工具应用、政策伦理等类别生成每日简报，并附原文链接 | 否 |
| [paper-parse](./skills/paper-parse/) | 对学术论文 PDF 或 URL 进行双模式深度研读，生成面向研究者的专业解析和面向快速理解的核心逻辑提炼 | 否 |
| [siyuan-note](./skills/siyuan-note/) | SiYuan Note (思源笔记) API 客户端 — 完整的笔记本、文档和块管理 | 需要配置 API Token |
| [tech-stack-quickstart](./skills/tech-stack-quickstart/) | 为指定技术栈生成新手友好的快速入门和用法参考文档 | 否 |

## 安装

首先，克隆该仓库到本地：

```bash
git clone https://gitee.com/bowenEI/myskills.git
cd myskills
```

然后，根据你使用的智能体应用，执行相应的安装命令。以下命令会用符号链接把本仓库的 `skills` 目录挂载到目标应用的技能目录中。

### Codex

```bash
rm -rf ~/.codex/skills
ln -s $(pwd)/skills ~/.codex/skills
```

```powershell
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $env:USERPROFILE\.codex\skills
New-Item -ItemType SymbolicLink -Path $env:USERPROFILE\.codex\skills -Target (Join-Path (Get-Location) "skills")
```

### Claude Code

```bash
rm -rf ~/.claude/skills
ln -s $(pwd)/skills ~/.claude/skills
```

```powershell
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $env:USERPROFILE\.claude\skills
New-Item -ItemType SymbolicLink -Path $env:USERPROFILE\.claude\skills -Target (Join-Path (Get-Location) "skills")
```

### 通用 Agent 目录

```bash
rm -rf ~/.agent/skills
ln -s $(pwd)/skills ~/.agent/skills
```

```powershell
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $env:USERPROFILE\.agent\skills
New-Item -ItemType SymbolicLink -Path $env:USERPROFILE\.agent\skills -Target (Join-Path (Get-Location) "skills")
```
