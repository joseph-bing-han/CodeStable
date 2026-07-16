---
doc_type: task-list
task: codestable-source-python-tools-cli-errors
goal: 修复 CodeStable 源模板 Python 工具的 CLI 可执行性问题，并把错误放置在 docs 的总结迁移回 .codestable 体系
status: completed
workflow: issue-fastforward
owner_skill: cs-issue
created: 2026-07-05
updated: 2026-07-05
archived: 2026-07-05
related_docs:
  - .codestable/issues/2026-07-05-codestable-source-python-tools-cli-errors/codestable-source-python-tools-cli-errors-fix-note.md
---

# CodeStable 源模板 Python 工具 CLI 问题任务归档

## 1. 任务目标

修复 `cs-onboard` 源模板中的 Python CLI 问题，确保下游项目不再重复命中同类错误；同时把错误放在 `docs/` 的总结迁移回 `.codestable/` 体系。

## 2. 当前状态

completed

## 3. Agent 原生 Tasks 同步区

- [x] 修复 `validate-yaml.py` 的路径示例与路径解析
- [x] 修复 `codestable-main-publish.py` 的子命令后置公共参数问题
- [x] 补 issue fix-note
- [x] 将错误放置在 `docs/` 的总结改为 `.codestable` 体系内产物并清理 `docs` 文件

## 4. CodeStable 文档索引

| 类型 | 路径 | 说明 |
|---|---|---|
| issue-fix | `.codestable/issues/2026-07-05-codestable-source-python-tools-cli-errors/codestable-source-python-tools-cli-errors-fix-note.md` | 本次源模板 CLI 修复记录 |
| archived-task | `.codestable/tasks/archived/2026-07-05-codestable-source-python-tools-cli-errors.md` | 本次任务归档 |

## 5. 执行步骤

### 1. 修复源模板脚本

- 状态：done
- 来源：cs-issue
- 完成信号：两个 Python 源模板脚本的 CLI 行为已按预期修正。

### 2. 执行最小验证

- 状态：done
- 来源：cs-issue
- 完成信号：help smoke-test、`codestable-main-publish` 子命令参数验证、`validate-yaml` frontmatter 校验均已通过。

### 3. 清理错误文档归宿

- 状态：done
- 来源：cs-issue
- 完成信号：总结信息已回收到 `.codestable` 体系，`docs/` 中不再保留本次 CS 总结文档。

## 6. 完成与归档记录

完成日期：2026-07-05

验证结果：

- `validate-yaml.py` 已支持 `.codestable/...` 实际路径示例与仓库相对路径解析。
- `codestable-main-publish.py` 已支持 `status --json` 与 `status --root ... --json` 等后置公共参数写法。
- 源模板脚本 `--help` smoke-test 已通过。
- fix-note 与任务归档文档均已落在 `.codestable/` 下。
