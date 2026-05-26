# 自用技能仓库

该仓库包含了我个人使用的一些技能，主要用于 OpenClaw、Claude Code、Hermes Agent 等智能体应用。

## 技能列表

| 技能 | 说明 |
|------|------|
| [ai4scholar](./skills/ai4scholar/) | 综合学术文献检索、分析、管理。覆盖 Semantic Scholar、PubMed、Google Scholar、arXiv、bioRxiv、medRxiv，支持论文搜索、引文追踪、作者画像、PDF 全文、DOI 解析、自动引用标注 (Auto-Cite)、科研绘图 (Sci-Draw) |
| [bilibili-cache-to-mp4](./skills/bilibili-cache-to-mp4/) | 将 B 站 Android/PC 客户端缓存的 .m4s 文件转换为可播放的 MP4 视频 |
| [book-deconstruction](./skills/book-deconstruction/) | 书籍章节级要点提炼与深度解读，生成结构化笔记和思维导图 |
| [siyuan-note](./skills/siyuan-note/) | SiYuan Note (思源笔记) API 客户端 — 完整的笔记本、文档和块管理 |
| [tech-stack-quickstart](./skills/tech-stack-quickstart/) | 为指定技术栈生成新手友好的快速入门和用法参考文档 |

## 安装

首先，克隆该仓库到本地：

```bash
git clone https://gitee.com/bowenEI/myskills.git
cd myskills
```

然后，根据你使用的智能体应用，执行相应的安装命令（采用符号链接方式）。

Claude Code Installation:

```bash
rm -rf ~/.claude/skills
ln -s $(pwd)/skills ~/.claude/skills
```

```powershell
rm -rf $env:USERPROFILE\.claude\skills
New-Item -ItemType SymbolicLink -Path $env:USERPROFILE\.claude\skills -Target (Join-Path (Get-Location) "skills")
```

Codex Installation:

```bash
rm -rf ~/.codex/skills
ln -s $(pwd)/skills ~/.codex/skills
```

```powershell
rm -rf $env:USERPROFILE\.codex\skills
New-Item -ItemType SymbolicLink -Path $env:USERPROFILE\.codex\skills -Target (Join-Path (Get-Location) "skills")
```

Or:

```bash
rm -rf ~/.agent/skills
ln -s $(pwd)/skills ~/.agent/skills
```

```powershell
rm -rf $env:USERPROFILE\.agent\skills
New-Item -ItemType SymbolicLink -Path $env:USERPROFILE\.agent\skills -Target (Join-Path (Get-Location) "skills")
```