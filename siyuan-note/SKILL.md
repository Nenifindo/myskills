---
name: siyuan-note
description: Access and manage local SiYuan Note (思源笔记) workspaces with the built-in siyuan CLI as the preferred path, while preserving the local HTTP API and Python client fallback. Use for notebooks, documents, blocks, search, SQL, import/export, assets, databases, daily notes, templates, history, repo snapshots, and scripted/batch note management.
---

# SiYuan Note (思源笔记)

Prefer the built-in `siyuan` CLI for direct local workspace access. It can read and write workspace data without starting the SiYuan kernel service, which makes it the default choice for scripting, batch operations, and agent workflows. Keep using the bundled HTTP API client when the CLI is unavailable, the user explicitly asks for API access, or an existing Python helper is the best fit.

## Access Strategy

1. Probe the CLI first: `Get-Command siyuan`, `siyuan --help`, then `siyuan --format json workspace info`.
2. Use `--format json` for parseable output whenever the command supports it.
3. Pass `--workspace <path>` when the user gives a workspace, when multiple workspaces are registered, or when `SIYUAN_WORKSPACE_PATH` is unset/ambiguous.
4. Use `--dry-run` before destructive or bulk write operations, then rerun without it only after the target and parameters are confirmed.
5. Use temporary files plus `--file` for long Markdown or structured content instead of stuffing large payloads into shell arguments.
6. Fall back to the API/Python client section when `siyuan` is missing from `PATH`, CLI output is insufficient, or the operation is already implemented by the bundled tools.

## CLI Access (Preferred)

For any CLI-based note access or management task, read `CLI.md` in this skill directory before running `siyuan` commands. It contains installation notes, global flags, safety rules, command references, and examples for notebooks, documents, blocks, search, SQL, import/export, history, repo snapshots, metadata, assets, databases, daily notes, templates, and workspace files.

Minimal probe:

```powershell
Get-Command siyuan
siyuan --help
siyuan --format json workspace info
```

Default command shape:

```bash
siyuan [--workspace /path/to/workspace] [--format json] [--dry-run] <command> [args]
```

Before destructive or bulk writes, use `--dry-run` and consider `siyuan repo create --memo "before batch edit"` or `siyuan export data --output ./full-backup.zip`.

## API/Python Fallback

Use this path when the CLI cannot be used, when the user explicitly asks for HTTP API access, or when a local Python helper already covers the requested task. The API path requires SiYuan running with API enabled and a token from **Settings -> About -> API**.

### Configuration

Create or edit `config.yaml`:

```yaml
siyuan:
  base_url: "http://127.0.0.1:6806"  # Check SiYuan settings for actual port
  token: "your-api-token-here"       # Paste your token here
  timeout: 30
  retry: 3
```

SiYuan may use different ports on restart, commonly `6806` but sometimes another port. Check the current port in SiYuan settings.

### Initialize Client

```python
from siyuan_client import SiYuanClient

# Use config.yaml settings
client = SiYuanClient()

# Or explicit configuration
client = SiYuanClient(
    base_url="http://127.0.0.1:6806",
    token="your-token"
)
```

### System Operations

```python
# Get system version
version = client.system_version()
print(f"SiYuan v{version}")

# Get current time in milliseconds
timestamp = client.current_time()

# Get boot progress
progress = client.boot_progress()
print(f"Boot: {progress['progress']}% - {progress['details']}")
```

### Notebook Operations

```python
# List all notebooks
notebooks = client.list_notebooks()
for nb in notebooks:
    print(f"{nb['name']}: {nb['id']}")

# Create new notebook
new_nb = client.create_notebook("我的新项目")

# Open/close notebook (load/unload from memory)
client.open_notebook("notebook-id")
client.close_notebook("notebook-id")

# Rename notebook
client.rename_notebook("notebook-id", "新名称")

# Get/set notebook configuration
conf = client.get_notebook_conf("notebook-id")
client.set_notebook_conf("notebook-id", {"dailyNoteSavePath": "/daily"})

# Remove notebook
client.remove_notebook("notebook-id")
```

### Document Operations

IMPORTANT: When importing Markdown format text, convert inline math in the form of `\(...\)` to `$...$` first, then proceed with the import.

```python
# Export document as Markdown
result = client.export_md_content("doc-id")
print(result["hPath"])      # Human-readable path
print(result["content"])    # Markdown content

# Create new document
new_doc = client.create_doc_with_md(
    notebook_id="notebook-id",
    path="folder/document-name",  # Supports nested paths
    markdown="# Title\n\nContent here"
)

# Rename document
client.rename_doc("notebook-id", "/old-path", "新标题")
client.rename_doc_by_id("doc-id", "新标题")

# Get document paths
hpath = client.get_hpath_by_id("doc-id")
path_info = client.get_path_by_id("doc-id")
ids = client.get_ids_by_hpath("notebook-id", "/人类可读路径")

# Move documents by ID
client.move_docs_by_id(
    doc_ids=["doc-id-1", "doc-id-2"],
    to_id="target-notebook-or-doc-id"
)

# Move documents by path
client.move_docs(
    from_paths=["/path/to/doc1.sy", "/path/to/doc2.sy"],
    to_notebook="target-notebook-id",
    to_path="/subfolder"
)

# Remove document by notebook and path
client.remove_doc("notebook-id", "/path/to/doc.sy")

# Remove document by ID
client.remove_doc_by_id("doc-id")
```

### Block Operations

```python
# Insert blocks at a specific position
blocks = client.insert_block(
    data_type="markdown",
    data="## New Section\n\nSome content",
    parent_id="doc-id",      # Optional: parent block/document
    previous_id="block-id",  # Optional: insert after this block
    next_id="block-id"       # Optional: insert before this block
)

# Prepend to beginning of document
blocks = client.prepend_block(
    data_type="markdown",
    data="# Title\n",
    parent_id="doc-id"
)

# Append to end of document
blocks = client.append_block(
    data_type="markdown",
    data="\n---\nFooter here",
    parent_id="doc-id"
)

# Update block content
client.update_block(
    data_type="markdown",
    data="Updated content",
    block_id="block-id"
)

# Delete block
client.delete_block("block-id")

# Move block
client.move_block(
    block_id="block-id",
    previous_id="target-block-id",  # Optional: insert after this block
    parent_id="parent-block-id"     # Optional: set parent; at least one target is required
)

# Fold/unfold blocks
client.fold_block("block-id")
client.unfold_block("block-id")

# Transfer block references
client.transfer_block_ref(
    from_id="source-block-id",
    to_id="target-block-id",
    ref_ids=["ref-1", "ref-2"]  # Optional: specific refs to transfer
)

# Get block in Kramdown format
kramdown = client.get_block_kramdown("block-id")

# Get child blocks
children = client.get_child_blocks("container-block-id")
for child in children:
    print(f"{child['type']}: {child['content'][:50]}")
```

### Block Attributes

```python
# Set custom attributes on a block
client.set_block_attrs("block-id", {
    "custom-key": "value",
    "custom-priority": "high",
    "custom-status": "done"
})

# Get all attributes of a block
attrs = client.get_block_attrs("block-id")
print(attrs.get("custom-key"))
```

### Assets

```python
# Upload asset files
result = client.upload_asset(
    file_paths=["/path/to/image.png", "/path/to/doc.pdf"],
    assets_dir_path="/assets/"
)
print(result["succMap"])
print(result["errFiles"])
```

### SQL Operations

```python
# Execute SQL query (read-only recommended)
results = client.query_sql("""
    SELECT * FROM blocks
    WHERE content LIKE '%关键词%'
    ORDER BY updated DESC
    LIMIT 10
""")
for block in results:
    print(f"{block['content'][:100]}...")

# Flush SQLite transaction to disk
client.flush_transaction()
```

### Templates

```python
# Render a template file
result = client.render_template(
    doc_id="doc-id",
    template_path="/data/templates/daily.md"
)
print(result["content"])

# Render Sprig template string
output = client.render_sprig('/daily note/{{now | date "2006/01"}}/{{now | date "2006-01-02"}}')
```

### File Operations

```python
# Read file content
content = client.get_file("/data/20210808180117-6v0mkxr/20200923234011-ieuun1p.sy")

# Create directory
client.put_file("/data/new-folder", is_dir=True)

# Upload file
with open("local-file.txt", "rb") as f:
    client.put_file("/data/new-folder/file.txt", file_content=f.read())

# List directory
files = client.read_dir("/data/20210808180117-6v0mkxr")
for f in files:
    print(f"{'[DIR]' if f['isDir'] else '[FILE]'} {f['name']}")

# Rename/move file
client.rename_file("/data/old-name.sy", "/data/new-name.sy")

# Remove file
client.remove_file("/data/unwanted-file.sy")
```

### Export

```python
# Export document as Markdown
result = client.export_md_content("doc-id")
print(result["hPath"])
print(result["content"])

# Export multiple files/folders as zip
zip_path = client.export_resources(
    paths=["/conf/appearance/boot", "/conf/appearance/langs"],
    name="my-export"
)
print(f"Exported to: {zip_path}")
```

### Conversion

```python
# Run Pandoc conversion
client.put_file("/temp/convert/pandoc/mydir/input.epub", file_content=epub_bytes)
work_dir = client.pandoc("mydir", ["--to", "markdown_strict", "input.epub", "-o", "output.md"])
output = client.get_file("/temp/convert/pandoc/mydir/output.md")
```

### Notifications

```python
# Push message to SiYuan UI
msg_id = client.push_msg("Hello from API!")

# Push error message
err_id = client.push_err_msg("Something went wrong!", timeout=10000)
```

### Network

```python
# Forward HTTP request through SiYuan proxy
response = client.forward_proxy(
    url="https://api.example.com/data",
    method="GET",
    headers=[{"Authorization": "Bearer token"}]
)
print(response["body"])
print(response["status"])
```

### Bundled API Tools

All tools are located in `tools/` and depend on `siyuan_client.py`.

```bash
# List
python3 tools/list.py --notebooks
python3 tools/list.py --docs "notebook-id"
python3 tools/list.py -n -j

# Read
python3 tools/read.py 20240602141622-l7ou7t7
python3 tools/read.py 20240602141622-l7ou7t7 -o ~/doc.md
python3 tools/read.py 20240602141622-l7ou7t7 --info

# Search
python3 tools/search.py "keyword"
python3 tools/search.py "keyword" -l 50
python3 tools/search.py "SELECT * FROM blocks WHERE type='d' LIMIT 10" --sql

# Export
python3 tools/export.py -o ~/backup/
python3 tools/export.py -n "工作" -o ~/backup/
python3 tools/export.py -d 20240602141622-l7ou7t7 -o ~/doc.md

# Create
python3 tools/create.py --notebook "New Project"
python3 tools/create.py --doc notebook-id /readme "# Hello\n\nWorld"
python3 tools/create.py --doc notebook-id /folder/doc "## Title\nContent"

# Delete
python3 tools/delete.py --notebook notebook-id
python3 tools/delete.py --doc doc-id
python3 tools/delete.py --block block-id
python3 tools/delete.py --doc doc-id --yes

# Move
python3 tools/move.py --doc doc-id --to-notebook target-nb-id
python3 tools/move.py --docs id1 id2 id3 --to-notebook target-nb-id
python3 tools/move.py --from-paths /doc1.sy /doc2.sy --to-nb target-nb --to-path /folder/

# Update
python3 tools/update.py --block block-id --markdown "New content"
python3 tools/update.py --append doc-id --markdown "\n\nFooter"
python3 tools/update.py --prepend doc-id --markdown "# Header\n"
python3 tools/update.py --insert "New paragraph" --parent doc-id
```

### API Reference

- Local API documentation: `API.md` in this directory.
- Implementation details: inspect `siyuan_client.py`.
- Command wrappers: inspect `tools/`.

## Troubleshooting

- CLI missing: locate `<SiYuan install>/resources/kernel/SiYuan-Kernel` or the platform-specific `siyuan` executable, add it to `PATH`, or invoke the full path.
- Wrong workspace: set `SIYUAN_WORKSPACE_PATH` or pass `--workspace`.
- CLI output hard to parse: add `--format json`.
- API connection refused: start SiYuan, enable API, and verify the port in `config.yaml`.
- API authentication failed: copy a fresh token from SiYuan settings.
- API port changed: check the current SiYuan API port and update `config.yaml`.
