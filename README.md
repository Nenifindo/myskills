# 自用技能仓库

该仓库包含了我个人使用的一些技能，主要用于 OpenClaw、Claude Code、Hermes Agent 等智能体应用。

## Installation

首先，克隆该仓库到本地：

```bash
git clone https://gitee.com/bowenEI/myskills.git
cd myskills
```

然后，根据你使用的智能体应用，执行相应的安装命令（采用符号链接方式）：

OpenClaw Installation:

```bash
ln -s $(pwd)/skills/* ~/.openclaw/skills/
```

Claude Code Installation:

```bash
ln -s $(pwd)/skills/* ~/.claude/skills/
```

Hermes Agent Installation:

```bash
ln -s $(pwd)/skills/* ~/.hermes/skills/
```

Other Agents (e.g., Codex, etc.) Installation:

```bash
ln -s $(pwd)/skills/* ~/.agent/skills/
```

以上安装命令都是用户级别全局安装，当然也可以选择局部安装到某个项目中：

```bash
cd /path/to/your/project
ln -s $(pwd)/skills/* ./skills/
```