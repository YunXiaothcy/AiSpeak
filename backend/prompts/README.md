# AI Prompt Templates Guide - NovelAI Forge Desktop

本文件夹包含 NovelAI Forge 桌面版 AI 生成系统的提示词模板。

## 📋 模板结构说明

每个模板文件遵循以下约定:
- `{purpose}_prompt.txt` - 主模板文件
- 变量标记为 `{{VARIABLE_NAME}}`
- 系统提示词与用户提示词通过注释分隔
- **重要**: 包含 `[CUSTOM_SYSTEM_PROMPT_HERE]` 占位符供用户自定义

## 🎯 可用模板列表

### 1. `outline_prompt.txt` - 小说大纲生成
**用途**: 根据小说设定生成章节大纲  
**变量**: `{{GENRE}}`, `{{THEME}}`, `{{CHARACTER_COUNT}}`, `{{TARGET_CHAPTERS}}`, `{{WRITING_STYLE}}`

### 2. `chapter_prompt.txt` - 章节撰写
**用途**: 根据大纲撰写完整章节内容  
**变量**: `{{PREVIOUS_CONTEXT}}`, `{{CHAPTER_OUTLINE}}`, `{{CHARACTERS_PRESENT}}`, `{{WRITING_STYLE}}`, `{{WORD_COUNT_TARGET}}`

### 3. `continuation_prompt.txt` - 续写生成
**用途**: 基于已有内容继续写作  
**变量**: `{{EXISTING_CONTENT}}`, `{{LAST_PARAGRAPH}}`, `{{PLOT_DIRECTION}}`, `{{CHARACTERS_PRESENT}}`

### 4. `polish_prompt.txt` - 文本润色
**用途**: 增强文本质量和表现力  
**变量**: `{{ORIGINAL_TEXT}}`, `{{POLISH_TYPE}}` (描写/对话/节奏), `{{STYLE_GUIDE}}`

### 5. `consistency_prompt.txt` - 一致性检查
**用途**: 检查内容逻辑一致性问题  
**变量**: `{{CONTENT_TO_CHECK}}`, `{{CHARACTER_DATABASE}}`, `{{TIMELINE}}`, `{{WORLD_RULES}}`

### 6. `dialogue_prompt.txt` - 对话生成
**用途**: 生成角色对话场景  
**变量**: `{{CHARACTERS}}`, `{{SCENE}}`, `{{EMOTION}}`, `{{PLOT_POINT}}`

## ✏️ 自定义提示词

用户可以在 `custom/` 目录下创建自己的提示词模板。
自定义提示词应遵循相同的变量命名规范。

## 🔧 使用说明

1. **不要修改占位符**: `[CUSTOM_SYSTEM_PROMPT_HERE]` 标记用于系统注入核心指令
2. **保持变量一致性**: 所有 `{{变量名}}` 必须在代码中定义
3. **测试兼容性**: 在多个 AI 提供商上测试模板效果
4. **版本控制**: 修改前备份原始模板

## ⚠️ 注意事项

- 这些模板由 AI 引擎动态加载
- QWen Bot 可能需要调整部分措辞以获得最佳效果
- 长度限制: 系统提示词建议 < 2000 字，用户提示词 < 4000 字
