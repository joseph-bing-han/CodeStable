---
doc_type: requirement-delta
requirement: plugin-market-distribution
feature: 2026-07-16-cursor-plugin-v104-hardening
status: applied
created: 2026-07-16
applied: 2026-07-18
---

# plugin-market-distribution requirement delta

## 变更原因

现有 requirement 只明确 Codex、Claude 和 `skills` CLI 三种分发入口；当前 feature 新增 Cursor marketplace 入口，属于用户可感的宿主范围扩展，需要 owner 在实现前确认。

## 拟议变更

### 用户故事

追加：

- 作为使用 Cursor 的开发者，我希望通过 Cursor marketplace 安装同一份 CodeStable skills，并与其他宿主保持同一版本。

### 怎么解决

将“同时适配 Codex、Claude 和 `skills` CLI”扩展为“同时适配 Codex、Claude、Cursor 和 `skills` CLI”；仍由 `plugins/codestable/skills/` 维护唯一 skill 源。

### 变更日志

验收通过后追加：

- 2026-07-16：新增 Cursor marketplace 分发入口，并加固跨宿主 manifest 身份、版本和安装文档校验。

## 保持不变

- pitch、status 和既有 `implemented_by` 不变。
- 不迁移仓库地址，不发布到公开 marketplace。
- 仍只打包 CodeStable 自己的 `cs` / `cs-*` skills。
- `dist/` 仍不能作为用户安装入口。
- 2026-07-01 的第一版实现记录保持原文，不做历史重写。

## 应用条件

- owner 批准本 delta；
- feature 的实现、code review、QA 和 acceptance 全部通过；
- acceptance 只机械应用上述三处变更，不自由扩写 requirement。
