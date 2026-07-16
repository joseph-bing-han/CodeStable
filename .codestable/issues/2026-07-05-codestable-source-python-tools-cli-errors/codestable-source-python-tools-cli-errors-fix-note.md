---
doc_type: issue-fix
issue: 2026-07-05-codestable-source-python-tools-cli-errors
status: draft
path: fastforward
root_cause_type: cli-contract
tags: [codestable, source-template, python-tools, cli]
related: []
---

# CodeStable 源模板 Python 工具命令行报错修复记录

## 1. 根因

当前 CodeStable 仓库里，`cs-onboard` 所携带的 Python 工具源模板存在两类 CLI 可执行性问题：

1. `plugins/codestable/skills/cs-onboard/tools/validate-yaml.py`
   - usage 示例仍保留旧的 `codestable/...` 路径，容易误导下游项目调用。
   - 路径解析依赖当前工作目录；若调用者不在目标仓库根目录执行，即使传入仓库相对路径，也可能报 `File not found`。

2. `plugins/codestable/skills/cs-onboard/tools/codestable-main-publish.py`
   - `--root`、`--json` 仅挂在主 parser。
   - 当调用者按常见直觉执行 `status --json` 或 `status --root .` 时，会触发 argparse `unrecognized arguments`。

## 2. 修复范围

本次只修改：

- `plugins/codestable/skills/cs-onboard/tools/validate-yaml.py`
- `plugins/codestable/skills/cs-onboard/tools/codestable-main-publish.py`

## 3. 修复内容

### 3.1 validate-yaml.py

- 将 usage 示例统一改为真实的 `.codestable/...` 路径。
- 在帮助文本中明确强调 `--dir`、`--file`、positional path 三者只能提供一个来源。
- 新增基于脚本位置推导仓库根目录的路径解析逻辑。
- 对 `--file`、`--dir`、positional path 做归一化判定，保证：
  - 同一目标路径的等价输入不再误判；
  - 调用方不在仓库根目录时，仍可解析仓库相对路径。

### 3.2 codestable-main-publish.py

- 抽出公共参数注册函数 `add_common_arguments()`。
- 将 `--root`、`--json` 同时挂到主 parser 和各子命令 parser。
- 允许以下直觉式调用正常工作：
  - `status --json`
  - `status --root .`
  - `status --root <repo> --json`

## 4. 验证命令和结果

### 4.1 源模板 CLI help smoke-test

```bash
python3 "/Users/joseph/code/CodeStable/plugins/codestable/skills/cs-onboard/tools/validate-yaml.py" --help >/dev/null && python3 "/Users/joseph/code/CodeStable/plugins/codestable/skills/cs-onboard/tools/codestable-main-publish.py" --help >/dev/null
```

结果：退出码 `0`。

### 4.2 codestable-main-publish 子命令后置参数

```bash
python3 "/Users/joseph/code/CodeStable/plugins/codestable/skills/cs-onboard/tools/codestable-main-publish.py" status --root "/Users/joseph/code/CodeStable" --json
```

结果：退出码 `0`，成功输出 JSON 状态。

## 5. 风险评估

- 数据结构：无变更。
- 业务逻辑：无变更。
- 影响范围：仅影响 CodeStable `cs-onboard` 分发给下游项目的 Python 工具模板。
- 剩余风险：`codestable-main-publish.py` 默认 `--root` 仍取当前工作目录；若调用方只写绝对脚本路径但不显式给出 `--root`，仍会以当前 cwd 对应仓库作为目标。这是 CLI 约定，不是本次缺陷。
