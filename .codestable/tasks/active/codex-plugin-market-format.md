---
doc_type: task
task: codex-plugin-market-format
goal: 修正 CodeStable 的 Codex plugin manifest 与 marketplace 格式，使其可被 Codex 正确识别
status: completed
workflow: issue
owner_skill: cs-issue-fix
created: 2026-07-06
updated: 2026-07-06
archived: null
related_docs: []
---

# Task: codex-plugin-market-format

## 目标

参考 `/Users/joseph/.agents/plugins/CodeStable` 中已由 Codex 修正并可用的配置，更新当前项目的 Codex plugin manifest 与 marketplace 格式。

## 当前状态

completed

## 执行步骤

- [x] 对比当前项目与已修正版的 `.codex-plugin/plugin.json` 和 `.agents/plugins/marketplace.json`。
- [x] 修改当前项目的 Codex plugin manifest 与 marketplace 配置。
- [x] 更新 package checker 与测试样例，防止格式回退。
- [x] 运行验证命令确认配置可通过现有检查。

## CodeStable 文档索引

- 暂无独立 issue 文档；本次为维护类配置修复，Task 记录作为轻量 spine。

## 决策记录

- 保留当前项目正式版本号来源，不直接复制已安装目录中的本地修正版版本后缀。

## 验证记录

- `python3 tools/check-plugin-package.py --root .` 已运行；Codex 配置相关字段不再报错，但全量检查仍被既有非本次问题阻塞：根目录 `cs-onboard` 残留、plugin tree 中 `__pycache__`、`README.en.md` 缺少安装命令。
- `python3 -m pytest tests/test_plugin_package.py` 已尝试；当前 Python 环境缺少 `pytest`，无法执行 pytest。
- 定向验证脚本已运行；`.agents/plugins/marketplace.json` 与 `plugins/codestable/.codex-plugin/plugin.json` 的 checker findings 为 0。

## 完成与归档记录

- 2026-07-06：执行步骤已完成，进入归档流程。
