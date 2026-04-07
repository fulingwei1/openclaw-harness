# Golden Rules Template

## 全局规则 (Global)

- [P5] 所有输出必须使用中文
- [P4] 代码必须有清晰的注释
- [P4] 重要决策必须有理由说明
- [P3] 避免使用模糊的表述

## 领域规则 (Domain)

- [P4] 代码变更必须向后兼容
- [P3] API 变更必须更新文档
- [P3] 依赖项变更必须说明原因

## 格式规则 (Format)

- [P3] 输出格式必须整洁规范
- [P3] Markdown 必须符合标准语法
- [P2] 代码块必须指定语言

---

## 规则说明

- **Priority**: 1-5, 数字越大优先级越高
- **Category**: global (全局) / domain (领域) / format (格式)
- **Content**: 规则的具体描述

## 使用方式

```bash
# 添加规则
harness add-rule "规则内容" --category global --priority 4

# 列出规则
harness list-rules

# 删除规则
harness remove-rule rule_1
```
