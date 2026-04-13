# NovelAI Forge Desktop - 纯 Python 桌面应用完整实现方案

## Context

### 项目状态转换

**原始方案** (TODO_novelai-forge.md):
- Web 全栈应用 (Next.js 15 + FastAPI)
- 需要浏览器访问
- 复杂的 Docker Compose 部署
- 前后端分离架构

**当前方案** (本文档):
- ✅ **纯 Python 桌面应用程序**
- ✅ 使用 Flet 框架构建现代化 GUI
- ✅ 单一可执行文件，无需浏览器
- ✅ 本地运行，数据本地存储
- ✅ 直接集成 AI 引擎（LangChain + OpenAI）

### 转换理由

1. **用户体验**: 桌面应用响应更快，无需网络延迟
2. **部署简单**: `pip install` + `python main.py` 即可运行
3. **离线能力**: 除 AI 调用外，所有功能可离线使用
4. **资源占用**: 相比 Web 栈大幅降低系统需求
5. **开发效率**: 单一代码库，减少前后端协调成本

### 已完成的前置工作

✅ **Prompt 1 成果已整合**:
- [TODO_novelai-forge.md](../TODO_novelai-forge.md) - 完整的系统架构设计
- `backend/prompts/` 目录已创建，包含 6 个专业模板:
  - `outline_prompt.txt` - 大纲生成
  - `chapter_prompt.txt` - 章节撰写
  - `continuation_prompt.txt` - 续写
  - `polish_prompt.txt` - 文本润色
  - `consistency_prompt.txt` - 一致性检查
  - `dialogue_prompt.txt` - 对话生成
- 所有模板包含 `[CUSTOM_SYSTEM_PROMPT_HERE]` 占位符
- qwen_bot 集成方案已设计（可选）

### 技术栈确认

```
┌─────────────────────────────────────┐
│         NovelAI Forge Desktop       │
├─────────────────────────────────────┤
│  GUI Layer: Flet (Flutter-based)    │
│  - Modern Material Design 3 UI      │
│  - Dark/Light theme support         │
│  - Rich text editing                │
│  - Streaming output display         │
├─────────────────────────────────────┤
│  AI Engine: LangChain               │
│  - OpenAI-compatible clients        │
│  - Prompt template system           │
│  - Streaming response handling      │
│  - Context management               │
├─────────────────────────────────────┤
│  Data Layer: SQLite + JSON          │
│  - Project persistence              │
│  - Chapter storage                  │
│  - Settings cache                   │
│  - Export functionality             │
└─────────────────────────────────────┘
```

---

## Prompt Template Plan

### NAF-DESKTOP-PLAN-1.0 [提示词模板集成策略]

#### 模板加载机制

```python
# backend/services/prompt_manager.py (概念)
class PromptTemplateManager:
    """管理 AI 提示词模板"""
    
    PROMPTS_DIR = "backend/prompts"
    
    def __init__(self):
        self.templates = {}
        self._load_all_templates()
    
    def _load_all_templates(self):
        """从文件系统加载所有模板"""
        template_files = {
            "outline": "outline_prompt.txt",
            "chapter": "chapter_prompt.txt",
            "continuation": "continuation_prompt.txt",
            "polish": "polish_prompt.txt",
            "consistency": "consistency_prompt.txt",
            "dialogue": "dialogue_prompt.txt"
        }
        
        for name, filename in template_files.items():
            filepath = os.path.join(self.PROMPTS_DIR, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.templates[name] = f.read()
    
    def get_template(self, template_name: str, **kwargs) -> tuple[str, str]:
        """
        获取处理后的模板
        
        Returns:
            (system_prompt, user_prompt)
        """
        raw_template = self.templates.get(template_name, "")
        
        # 替换变量
        filled_template = raw_template.format(**kwargs)
        
        # 分离系统提示词和用户提示词
        if "[CUSTOM_SYSTEM_PROMPT_HERE]" in filled_template:
            parts = filled_template.split("[CUSTOM_SYSTEM_PROMPT_HERE]")
            system = parts[0].strip() if len(parts) > 0 else ""
            user = parts[1].strip() if len(parts) > 1 else filled_template
        else:
            system = ""
            user = filled_template
        
        return system, user
```

#### 变量映射表

| 模板 | 变量名 | 来源 | 说明 |
|------|--------|------|------|
| outline | `{{GENRE}}` | 项目设置 | 小说类型 |
| outline | `{{THEME}}` | 项目设置 | 主题 |
| outline | `{{CHARACTER_COUNT}}` | 角色列表 | 角色数量 |
| outline | `{{TARGET_CHAPTERS}}` | 项目设置 | 目标章节数 |
| outline | `{{WRITING_STYLE}}` | 项目设置 | 写作风格 |
| chapter | `{{PREVIOUS_CONTEXT}}` | 前几章摘要 | 上下文 |
| chapter | `{{CHAPTER_OUTLINE}}` | 大纲数据 | 本章大纲 |
| chapter | `{{CHARACTERS_PRESENT}}` | 角色档案 | 出场角色 |
| chapter | `{{WORD_COUNT_TARGET}}` | 用户输入 | 字数目标 |
| continuation | `{{EXISTING_CONTENT}}` | 编辑器内容 | 已有文本 |
| continuation | `{{LAST_PARAGRAPH}}` | 编辑器最后段 | 续写起点 |
| polish | `{{ORIGINAL_TEXT}}` | 选中文本 | 待润色文本 |
| polish | `{{POLISH_TYPE}}` | 用户选择 | 润色类型 |
| consistency | `{{CONTENT_TO_CHECK}}` | 编辑器/章节 | 检查范围 |
| consistency | `{{CHARACTER_DATABASE}}` | 角色数据库 | 角色信息 |

---

## Desktop App Items

### NAF-DESKTOP-ITEM-1.0 [项目初始化与环境配置]

#### 1.1 创建项目目录结构

```
novelai-forge-desktop/
├── main.py                      # 🎯 主入口 - 启动 Flet 桌面窗口
├── requirements.txt             # Python 依赖
├── .env.example                 # 环境变量模板
├── .gitignore
│
├── config/                      # 配置模块
│   ├── __init__.py
│   └── settings.py              # 应用设置管理
│
├── ai_engine/                   # 🔥 AI 引擎核心
│   ├── __init__.py
│   ├── base.py                  # AI Provider 抽象基类
│   ├── openai_provider.py       # OpenAI/Grok/Claude 实现
│   ├── prompt_manager.py        # 提示词模板管理器
│   ├── context_builder.py       # 上下文构建器
│   └── streaming_handler.py     # 流式输出处理器
│
├── gui/                         # 🎨 Flet GUI 模块
│   ├── __init__.py
│   ├── app.py                   # 主应用类
│   ├── theme.py                 # 主题配置 (暗色/亮色)
│   ├── components/              # 可复用组件
│   │   ├── __init__.py
│   │   ├── sidebar_left.py      # 左侧边栏 (项目列表+设置)
│   │   ├── editor_center.py     # 中央编辑器
│   │   ├── sidebar_right.py     # 右侧边栏 (AI 工具)
│   │   ├── toolbar_top.py       # 顶部工具栏
│   │   └── dialogs/             # 对话框
│   │       ├── __init__.py
│   │       ├── new_project_dialog.py
│   │       ├── settings_wizard.py
│   │       └── export_dialog.py
│   └── pages/                   # 页面/视图
│       ├── __init__.py
│       ├── home_page.py
│       ├── editor_page.py
│       └── settings_page.py
│
├── data/                        # 💾 数据层
│   ├── __init__.py
│   ├── database.py              # SQLite 操作
│   ├── models.py                # 数据模型
│   ├── project_manager.py       # 项目 CRUD
│   └── export_service.py        # 导出功能
│
├── backend/prompts/             # 📝 提示词模板 (已有)
│   ├── README.md
│   ├── outline_prompt.txt
│   ├── chapter_prompt.txt
│   ├── continuation_prompt.txt
│   ├── polish_prompt.txt
│   ├── consistency_prompt.txt
│   ├── dialogue_prompt.txt
│   └── custom/                  # 用户自定义模板
│
└── tests/                       # 测试 (可选)
    ├── __init__.py
    ├── test_ai_engine.py
    └── test_gui.py
```

#### 1.2 依赖清单

```txt
# requirements.txt
# GUI Framework
flet>=0.24.0

# AI / LLM
langchain>=0.3.0
langchain-openai>=0.2.0
openai>=1.50.0
httpx>=0.27.0

# Data Processing
pydantic>=2.9.0
pydantic-settings>=2.6.0

# Database
sqlite3  # Python 内置

# Utilities
python-dotenv>=1.0.0
python-dateutil>=2.9.0
aiofiles>=23.0.0

# Optional: QWen Bot Integration
selenium>=4.25.0
webdriver-manager>=4.0.0

# Development
pytest>=8.3.0
pytest-asyncio>=0.24.0
```

---

### NAF-DESKTOP-ITEM-2.0 [Flet GUI 核心实现]

#### 2.1 应用主窗口布局设计

```
┌──────────────────────────────────────────────────────────────────┐
│  📖 NovelAI Forge          [+ 新建项目] [打开] [保存] [导出] ⚙️  │ ← Toolbar Top
├────────────┬───────────────────────────────┬─────────────────────┤
│            │                               │                     │
│  📁 项目   │                               │   🤖 AI 工具箱      │
│            │                               │                     │
│  ▸ 项目A   │       Rich Text Editor        │  ┌───────────────┐  │
│  ▸ 项目B   │                               │  │ [生成大纲]     │  │
│  ▸ 项目C   │  在这里编写你的小说章节...     │  │ [生成章节]     │  │
│            │                               │  │ [续写]         │  │
│  ⚙️ 设置   │  支持 Markdown 格式预览        │  │ [润色]         │  │
│            │                               │  │ [一致性检查]   │  │
│  ────────  │                               │  │ [对话生成]     │  │
│            │                               │  ├───────────────┤  │
│  📑 章节   │                               │  │               │  │
│  · 第1章   │                               │  │ 流式输出预览区  │  │
│  · 第2章   │                               │  │               │  │
│  · 第3章   │                               │  │ > AI 正在生成  │  │
│  + 新建章节│                               │  │ > 内容...      │  │
│            │                               │  │               │  │
├────────────┴───────────────────────────────┴─────────────────────┤
│  状态栏: 已保存 | 字数: 1,234 | AI模型: GPT-4 | 最后操作: 润色   │
└──────────────────────────────────────────────────────────────────┘
```

#### 2.2 核心代码框架 - main.py

```python
"""
NovelAI Forge Desktop - 主入口文件
纯 Python 桌面应用，使用 Flet 构建 GUI
"""

import flet as ft
from gui.app import NovelAIForgeApp


def main(page: ft.Page):
    """Flet 应用主函数"""
    app = NovelAIForgeApp(page)
    app.run()


if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER)
    # 生产模式: ft.app(target=main, view=ft.AppView.FLET_APP_WEB)
```

#### 2.3 主应用类 - gui/app.py

```python
"""
NovelAIForgeApp - 主应用控制器
管理整个桌面的状态、布局和交互逻辑
"""

import flet as ft
from gui.theme import ThemeManager
from gui.components.toolbar_top import ToolbarTop
from gui.components.sidebar_left import SidebarLeft
from gui.components.editor_center import EditorCenter
from gui.components.sidebar_right import SidebarRight
from data.project_manager import ProjectManager
from ai_engine.prompt_manager import PromptTemplateManager


class NovelAIForgeApp:
    """主应用类"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.theme = ThemeManager()
        self.project_mgr = ProjectManager()
        self.prompt_mgr = PromptTemplateManager()
        
        # 当前状态
        self.current_project = None
        self.current_chapter = None
        self.is_dark_mode = True
        
        # 初始化页面
        self._setup_page()
        self._build_ui()
    
    def _setup_page(self):
        """配置页面基本属性"""
        self.page.title = "📖 NovelAI Forge - AI 小说创作助手"
        self.page.theme_mode = ft.ThemeMode.DARK if self.is_dark_mode else ft.ThemeMode.LIGHT
        self.page.window.width = 1400
        self.page.window.height = 900
        self.page.window.min_width = 1000
        self.page.window.min_height = 700
        self.page.padding = 0
    
    def _build_ui(self):
        """构建用户界面"""
        # 创建主要组件
        self.toolbar = ToolbarTop(app=self)
        self.sidebar_left = SidebarLeft(app=self)
        self.editor = EditorCenter(app=self)
        self.sidebar_right = SidebarRight(app=self)
        
        # 主布局容器
        main_layout = ft.Row(
            controls=[
                self.sidebar_left.build(),      # 左侧 250px
                ft.VerticalDivider(width=1),
                ft.Column(                       # 中间区域
                    controls=[
                        self.editor.build(),
                    ],
                    expand=True
                ),
                ft.VerticalDivider(width=1),
                self.sidebar_right.build(),     # 右侧 350px
            ],
            expand=True,
        )
        
        # 完整页面结构
        self.page.controls.clear()
        self.page.controls.append(
            ft.Column(
                controls=[
                    self.toolbar.build(),
                    ft.Divider(height=1),
                    main_layout,
                ],
                expand=True,
            )
        )
        
        self.page.update()
    
    def run(self):
        """启动应用"""
        print("🚀 NovelAI Forge Desktop 启动中...")
        self.page.update()
    
    def show_snack_bar(self, message: str, error: bool = False):
        """显示通知消息"""
        snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.colors.RED_400 if error else ft.colors.GREEN_400,
            duration=3000,
        )
        self.page.snack_bar = snack_bar
        self.page.snack_bar.open = True
        self.page.update()
```

#### 2.4 顶部工具栏 - gui/components/toolbar_top.py

```python
"""
ToolbarTop - 顶部工具栏组件
包含: 应用标题、项目管理按钮、全局操作
"""

import flet as ft
from gui.components.dialogs.new_project_dialog import NewProjectDialog
from gui.components.dialogs.export_dialog import ExportDialog


class ToolbarTop:
    """顶部工具栏"""
    
    def __init__(self, app):
        self.app = app
    
    def build(self) -> ft.Container:
        """构建工具栏"""
        return ft.Container(
            content=ft.Row(
                controls=[
                    # 左侧: Logo 和标题
                    ft.Icon(ft.icons.BOOK, size=24, color=ft.colors.BLUE_400),
                    ft.Text(
                        "NovelAI Forge",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.WHITE,
                    ),
                    
                    ft.Container(expand=True),  # 弹性空间
                    
                    # 右侧: 操作按钮组
                    ft.IconButton(
                        icon=ft.icons.ADD_BOX,
                        tooltip="新建项目",
                        on_click=self._on_new_project,
                    ),
                    ft.IconButton(
                        icon=ft.icons.FOLDER_OPEN,
                        tooltip="打开项目",
                        on_click=self._on_open_project,
                    ),
                    ft.IconButton(
                        icon=ft.icons.SAVE,
                        tooltip="保存",
                        on_click=self._on_save,
                    ),
                    ft.PopupMenuButton(
                        icon=ft.icons.FILE_UPLOAD_OUTLINED,
                        items=[
                            ft.PopupMenuItem(text="导出为 Markdown", on_click=lambda _: self._on_export("md")),
                            ft.PopupMenuItem(text="导出为 TXT", on_click=lambda _: self._on_export("txt")),
                            ft.PopupMenuItem(text="导出全部章节", on_click=lambda _: self._on_export("all")),
                        ],
                    ),
                    ft.IconButton(
                        icon=ft.icons.SETTINGS,
                        tooltip="设置",
                        on_click=self._on_settings,
                    ),
                ],
                height=50,
            ),
            bgcolor=ft.colors.SURFACE_VARIANT,
            padding=ft.padding.symmetric(horizontal=15),
        )
    
    def _on_new_project(self, e):
        """新建项目事件"""
        dialog = NewProjectDialog(self.app)
        self.app.page.dialog = dialog.build()
        self.app.page.dialog.open = True
        self.app.page.update()
    
    def _on_open_project(self, e):
        """打开项目事件"""
        projects = self.app.project_mgr.list_projects()
        if not projects:
            self.app.show_snack_bar("没有找到现有项目", error=True)
            return
        # TODO: 显示项目选择对话框
        pass
    
    def _on_save(self, e):
        """保存当前项目"""
        if self.app.current_project:
            self.app.project_mgr.save_project(self.app.current_project)
            self.app.show_snack_bar("✅ 项目已保存")
        else:
            self.app.show_snack_bar("⚠️ 没有打开的项目", error=True)
    
    def _on_export(self, format_type: str):
        """导出事件"""
        dialog = ExportDialog(self.app, format_type)
        self.app.page.dialog = dialog.build()
        self.app.page.dialog.open = True
        self.app.page.update()
    
    def _on_settings(self, e):
        """打开设置"""
        # TODO: 导航到设置页面
        pass
```

#### 2.5 左侧边栏 - gui/components/sidebar_left.py

```python
"""
SidebarLeft - 左侧边栏
功能: 项目列表、章节导航、小说设置向导
"""

import flet as ft


class SidebarLeft:
    """左侧边栏"""
    
    WIDTH = 280
    
    def __init__(self, app):
        self.app = app
        self.project_list = ft.ListView(expand=True, spacing=5, padding=10)
        self.chapter_list = ft.ListView(expand=True, spacing=3, padding=5)
    
    def build(self) ft.Container:
        """构建左侧边栏"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    # 项目区域标题
                    ft.ListTile(
                        title=ft.Text("📁 项目", weight=ft.FontWeight.BOLD, size=16),
                    ),
                    ft.Divider(height=1),
                    
                    # 项目列表
                    ft.Container(
                        content=self.project_list,
                        height=200,
                    ),
                    
                    ft.OutlinedButton(
                        "+ 新建项目",
                        on_click=self._on_new_project,
                        width=200,
                    ),
                    
                    ft.Divider(height=20),
                    
                    # 章节导航标题
                    ft.ListTile(
                        title=ft.Text("📑 章节", weight=ft.FontWeight.BOLD, size=16),
                    ),
                    ft.Divider(height=1),
                    
                    # 章节列表
                    ft.Container(
                        content=self.chapter_list,
                        expand=True,
                    ),
                    
                    ft.OutlinedButton(
                        "+ 新建章节",
                        on_click=self._on_new_chapter,
                        width=200,
                    ),
                ],
                scroll=ft.ScrollMode.AUTO,
            ),
            width=self.WIDTH,
            bgcolor=ft.colors.SURFACE_LOWEST,
            border=ft.border.only(right=ft.border.BorderSide(1, ft.colors.OUTLINE_VARIANT)),
        )
    
    def refresh_projects(self):
        """刷新项目列表"""
        self.project_list.controls.clear()
        projects = self.app.project_mgr.list_projects()
        
        for proj in projects:
            item = ft.ListTile(
                title=ft.Text(proj['title']),
                subtitle=ft.Text(f"{len(proj.get('chapters', []))} 章"),
                leading=ft.Icon(ft.icons.FOLDER),
                on_click=lambda e, p=proj: self._on_select_project(p),
                data=proj['id'],
            )
            self.project_list.controls.append(item)
        
        self.app.page.update()
    
    def refresh_chapters(self):
        """刷新章节列表"""
        self.chapter_list.controls.clear()
        if not self.app.current_project:
            return
        
        chapters = self.app.current_project.get('chapters', [])
        for idx, ch in enumerate(chapters, 1):
            item = ft.ListTile(
                title=ft.Text(f"第{idx}章: {ch.get('title', '未命名')}"),
                subtitle=ft.Text(f"{len(ch.get('content', ''))} 字"),
                leading=ft.Icon(ft.icons.DESCRIPTION),
                on_click=lambda e, c=ch, i=idx: self._on_select_chapter(c, i),
                data=ch.get('id'),
            )
            self.chapter_list.controls.append(item)
        
        self.app.page.update()
    
    def _on_select_project(self, project: dict):
        """选择项目"""
        self.app.current_project = project
        self.refresh_chapters()
        self.app.show_snack_bar(f"已打开项目: {project['title']}")
    
    def _on_select_chapter(self, chapter: dict, index: int):
        """选择章节"""
        self.app.current_chapter = chapter
        self.app.editor.load_content(chapter.get('content', ''))
        self.app.show_snack_bar(f"正在编辑: 第{index}章")
    
    def _on_new_project(self, e):
        """新建项目"""
        from gui.components.dialogs.new_project_dialog import NewProjectDialog
        dialog = NewProjectDialog(self.app)
        self.app.page.dialog = dialog.build()
        self.app.page.dialog.open = True
        self.app.page.update()
    
    def _on_new_chapter(self, e):
        """新建章节"""
        if not self.app.current_project:
            self.app.show_snack_bar("请先选择或创建一个项目", error=True)
            return
        
        new_chapter = {
            'id': f"ch_{len(self.app.current_project.get('chapters', [])) + 1}",
            'title': f"第{len(self.app.current_project.get('chapters', [])) + 1}章",
            'content': '',
            'outline': '',
        }
        
        self.app.current_project.setdefault('chapters', []).append(new_chapter)
        self.refresh_chapters()
        self._on_select_chapter(new_chapter, len(self.app.current_project['chapters']))
        self.app.show_snack_bar("✅ 新章节已创建")
```

#### 2.6 中央编辑器 - gui/components/editor_center.py

```python
"""
EditorCenter - 中央富文本编辑器
支持: Markdown 编辑、实时字数统计、自动保存
"""

import flet as ft


class EditorCenter:
    """中央编辑器区域"""
    
    def __init__(self, app):
        self.app = app
        self.text_field = None
        self.word_count_text = None
        self.auto_save_timer = None
    
    def build(self) -> ft.Container:
        """构建编辑器区域"""
        self.text_field = ft.TextField(
            value="",
            multiline=True,
            min_lines=25,
            max_lines=None,
            expand=True,
            text_size=14,
            text_style=ft.FontFamily.MONOSPACE,
            hint_text="在这里开始写作...\n\n支持直接输入或使用右侧 AI 工具辅助创作。",
            on_change=self._on_content_change,
            shift_enter=True,  # Shift+Enter 换行
        )
        
        self.word_count_text = ft.Text(
            "字数: 0",
            size=12,
            color=ft.colors.ON_SURFACE_VARIANT,
        )
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    # 编辑器标题栏
                    ft.Row(
                        controls=[
                            ft.Icon(ft.icons.EDIT_NOTE, color=ft.colors.BLUE_400),
                            ft.Text(
                                self._get_editor_title(),
                                size=16,
                                weight=ft.FontWeight.W_500,
                            ),
                            ft.Container(expand=True),
                            self.word_count_text,
                        ],
                        height=40,
                    ),
                    ft.Divider(height=1),
                    
                    # 主编辑器
                    ft.Container(
                        content=self.text_field,
                        expand=True,
                        clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    ),
                ],
                expand=True,
            ),
            expand=True,
            bgcolor=ft.colors.SURFACE_HIGHEST,
        )
    
    def load_content(self, content: str):
        """加载内容到编辑器"""
        if self.text_field:
            self.text_field.value = content or ""
            self._update_word_count()
            self.app.page.update()
    
    def get_content(self) -> str:
        """获取编辑器当前内容"""
        return self.text_field.value if self.text_field else ""
    
    def get_selected_text(self) -> str:
        """获取选中的文本"""
        # Flet TextField 不直接支持选中文本 API
        # 这里返回全部内容作为后备方案
        return self.get_content()
    
    def _get_editor_title(self) -> str:
        """获取编辑器标题"""
        if self.app.current_chapter:
            return self.app.current_chapter.get('title', '未命名章节')
        elif self.app.current_project:
            return self.app.current_project.get('title', '新项目')
        return "编辑器"
    
    def _on_content_change(self, e):
        """内容变化事件处理"""
        self._update_word_count()
        self._trigger_auto_save()
    
    def _update_word_count(self):
        """更新字数统计"""
        content = self.get_content()
        char_count = len(content.replace(' ', '').replace('\n', ''))
        word_count = len(content.split())
        
        if self.word_count_text:
            self.word_count_text.value = f"字符: {char_count} | 词数: {word_count}"
            self.app.page.update()
    
    def _trigger_auto_save(self):
        """触发自动保存（防抖）"""
        import threading
        if self.auto_save_timer:
            self.auto_save_timer.cancel()
        
        self.auto_save_timer = threading.Timer(3.0, self._auto_save)
        self.auto_save_timer.start()
    
    def _auto_save(self):
        """执行自动保存"""
        if self.app.current_chapter and self.app.current_project:
            self.app.current_chapter['content'] = self.get_content()
            self.app.project_mgr.save_project(self.app.current_project)
            # 静默保存，不显示通知
```

#### 2.7 右侧 AI 边栏 - gui/components/sidebar_right.py

```python
"""
SidebarRight - 右侧 AI 工具边栏
功能: AI 生成按钮、流式输出预览、模型选择
"""

import flet as ft
from ai_engine.streaming_handler import StreamingHandler


class SidebarRight:
    """右侧 AI 工具栏"""
    
    WIDTH = 380
    
    def __init__(self, app):
        self.app = app
        self.output_area = None
        self.streaming_handler = StreamingHandler()
        self.is_generating = False
        
        # AI 功能按钮
        self.btn_outline = None
        self.btn_chapter = None
        self.btn_continuation = None
        self.btn_polish = None
        self.btn_consistency = None
        self.btn_dialogue = None
        self.btn_stop = None
    
    def build(self) -> ft.Container:
        """构建右侧边栏"""
        # 初始化输出区域
        self.output_area = ft.Column(
            controls=[ft.Text("AI 输出将显示在这里...", italic=True, color=ft.colors.OUTLINE)],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        
        # 停止按钮（初始隐藏）
        self.btn_stop = ft.ElevatedButton(
            "⏹ 停止生成",
            icon=ft.icons.STOP_CIRCLE,
            color=ft.colors.RED,
            visible=False,
            on_click=self._on_stop_generation,
            width=200,
        )
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    # 标题
                    ft.ListTile(
                        title=ft.Text("🤖 AI 工具箱", weight=ft.FontWeight.BOLD, size=16),
                        subtitle=ft.Text("选择 AI 功能开始创作", size=11),
                    ),
                    ft.Divider(height=1),
                    
                    # 模型选择
                    ft Dropdown(
                        label="AI 模型",
                        width=350,
                        options=[
                            ft.dropdown.Option("gpt-4o", "GPT-4o (推荐)"),
                            ft.dropdown.Option("gpt-4-turbo", "GPT-4 Turbo"),
                            ft.dropdown.Option("claude-3-5-sonnet", "Claude 3.5 Sonnet"),
                            ft.dropdown.Option("grok-beta", "Grok Beta"),
                        ],
                        value="gpt-4o",
                    ),
                    
                    ft.Divider(height=15),
                    
                    # AI 功能按钮网格
                    ft.Text("快速操作", size=13, weight=ft.FontWeight.W_500),
                    ft.Container(height=8),
                    
                    self._create_button_grid(),
                    
                    ft.Divider(height=20),
                    
                    # 输出区域标题
                    ft.Row(
                        controls=[
                            ft.Text("输出预览", size=13, weight=ft.FontWeight.W_500),
                            ft.Container(expand=True),
                            self.btn_stop,
                        ],
                    ),
                    ft.Divider(height=1),
                    
                    # 流式输出显示区
                    ft.Container(
                        content=self.output_area,
                        height=350,
                        bgcolor=ft.colors.SURFACE_VARIANT,
                        border_radius=8,
                        padding=10,
                        border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
                    ),
                    
                    # 操作按钮
                    ft.Row(
                        controls=[
                            ft.OutlinedButton(
                                "复制到编辑器",
                                icon=ft.icons.COPY,
                                on_click=self._copy_to_editor,
                                expand=True,
                            ),
                            ft.OutlinedButton(
                                "清空",
                                icon=ft.icons.DELETE_OUTLINE,
                                on_click=self._clear_output,
                                expand=True,
                            ),
                        ],
                    ),
                ],
                scroll=ft.ScrollMode.AUTO,
                horizontal_alignment=ft.CrossAxisAlignment.START,
            ),
            width=self.WIDTH,
            bgcolor=ft.colors.SURFACE_LOWEST,
            border=ft.border.only(left=ft.border.BorderSide(1, ft.colors.OUTLINE_VARIANT)),
        )
    
    def _create_button_grid(self) -> ft.Column:
        """创建 AI 功能按钮网格"""
        buttons_config = [
            ("📋 生成大纲", ft.icons.VIEW_LIST, "outline", self._on_generate_outline),
            ("✍️ 生成章节", ft.icons.EDIT_DOCUMENT, "chapter", self._on_generate_chapter),
            ("➡️ 续写", ft.icons.ARROW_FORWARD, "continuation", self._on_continuation),
            ("✨ 润色", ft.icons.AUTO_FIX_HIGH, "polish", self._on_polish),
            ("🔍 一致性检查", ft.icons.FACT_CHECK, "consistency", self._on_consistency_check),
            ("💬 对话生成", ft.icons.CHAT, "dialogue", self._on_generate_dialogue),
        ]
        
        button_rows = []
        for i in range(0, len(buttons_config), 2):
            row_buttons = []
            for label, icon, action_type, handler in buttons_config[i:i+2]:
                btn = ft.ElevatedButton(
                    content=ft.Row(
                        controls=[
                            ft.Icon(icon, size=18),
                            ft.Text(label, size=12),
                        ],
                        spacing=8,
                    ),
                    style=ft.ButtonStyle(
                        padding=15,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    on_click=handler,
                    expand=True,
                )
                row_buttons.append(btn)
            
            button_rows.append(
                ft.Row(
                    controls=row_buttons,
                    spacing=10,
                )
            )
        
        return ft.Column(
            controls=button_rows,
            spacing=8,
        )
    
    async def _execute_ai_task(self, task_type: str, **kwargs):
        """执行 AI 任务（通用方法）"""
        if self.is_generating:
            self.app.show_snack_bar("⏳ 正在生成中，请稍候...", error=True)
            return
        
        if not self.app.current_project:
            self.app.show_snack_bar("请先创建或打开一个项目", error=True)
            return
        
        self.is_generating = True
        self.btn_stop.visible = True
        self._clear_output()
        self.app.page.update()
        
        try:
            # 调用 AI 引擎
            from ai_engine.base import AIEngine
            
            engine = AIEngine(self.app.prompt_mgr)
            
            # 构建上下文
            context = self._build_context(task_type, **kwargs)
            
            # 执行流式生成
            full_response = ""
            async for chunk in engine.generate_streaming(
                task_type=task_type,
                context=context,
                model=self._get_selected_model(),
            ):
                full_response += chunk
                self._append_output(chunk)
                
                # 更新 UI
                if len(full_response) % 50 == 0:  # 每 50 字符更新一次 UI
                    self.app.page.update()
            
            self._append_output("\n\n---\n✅ 生成完成！")
            
        except Exception as e:
            self._append_output(f"\n❌ 错误: {str(e)}")
            self.app.show_snack_bar(f"AI 生成失败: {str(e)}", error=True)
        
        finally:
            self.is_generating = False
            self.btn_stop.visible = False
            self.app.page.update()
    
    def _build_context(self, task_type: str, **kwargs) -> dict:
        """构建任务上下文"""
        base_context = {
            'project': self.app.current_project,
            'chapter': self.app.current_chapter,
            'editor_content': self.app.editor.get_content(),
        }
        base_context.update(kwargs)
        return base_context
    
    def _get_selected_model(self) -> str:
        """获取选中的模型名称"""
        # TODO: 从 Dropdown 获取实际值
        return "gpt-4o"
    
    def _append_output(self, text: str):
        """追加输出内容"""
        if self.output_area:
            # 移除占位文本
            if len(self.output_area.controls) == 1 and "将显示在这里" in str(self.output_area.controls[0].value):
                self.output_area.controls.clear()
            
            self.output_area.controls.append(
                ft.Text(text, size=13, selectable=True)
            )
    
    def _clear_output(self, e=None):
        """清空输出区域"""
        if self.output_area:
            self.output_area.controls.clear()
            self.output_area.controls.append(
                ft.Text("等待 AI 输出...", italic=True, color=ft.colors.OUTLINE)
            )
            self.app.page.update()
    
    def _copy_to_editor(self, e):
        """复制 AI 输出到编辑器"""
        output_text = "".join(
            ctrl.value for ctrl in self.output_area.controls 
            if isinstance(ctrl, ft.Text) and ctrl.value and "将显示在这里" not in ctrl.value and "❌" not in ctrl.value and "✅" not in ctrl.value
        )
        
        if output_text.strip():
            current_content = self.app.editor.get_content()
            new_content = current_content + "\n\n" + output_text if current_content else output_text
            self.app.editor.load_content(new_content)
            self.app.show_snack_bar("✅ 内容已插入编辑器")
        else:
            self.app.show_snack_bar("没有可复制的内容", error=True)
    
    def _on_stop_generation(self, e):
        """停止生成"""
        self.streaming_handler.stop()
        self.is_generating = False
        self.btn_stop.visible = False
        self._append_output("\n\n⏹ 用户停止了生成")
        self.app.page.update()
    
    # === 各 AI 功能的事件处理方法 ===
    
    async def _on_generate_outline(self, e):
        await self._execute_ai_task("outline")
    
    async def _on_generate_chapter(self, e):
        await self._execute_ai_task("chapter")
    
    async def _on_continuation(self, e):
        await self._execute_ai_task("continuation")
    
    async def _on_polish(self, e):
        await self._execute_ai_task("polish")
    
    async def _on_consistency_check(self, e):
        await self._execute_ai_task("consistency")
    
    async def _on_generate_dialogue(self, e):
        await self._execute_ai_task("dialogue")
```

---

### NAF-DESKTOP-ITEM-3.0 [AI 引擎核心实现]

#### 3.1 AI Provider 基类 - ai_engine/base.py

```python
"""
AI Engine Base - AI 引擎抽象基类和工厂模式
支持多提供商: OpenAI, Grok, Claude, QWen (optional)
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Any
import os
from dataclasses import dataclass


@dataclass
class AIConfig:
    """AI 配置"""
    provider: str = "openai"  # openai, grok, claude, qwen
    model: str = "gpt-4o"
    api_key: str = ""
    base_url: str = ""  # 用于自定义 API 端点
    temperature: float = 0.7
    max_tokens: int = 4000
    stream: bool = True


class BaseAIProvider(ABC):
    """AI 提供商基类"""
    
    def __init__(self, config: AIConfig):
        self.config = config
    
    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        **kwargs
    ) -> str:
        """同步生成内容"""
        pass
    
    @abstractmethod
    async def generate_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式生成内容"""
        pass


class OpenAIProvider(BaseAIProvider):
    """
    OpenAI 兼容提供商
    支持: GPT-4, GPT-4o, Grok (xAI), Claude (通过代理), 其他兼容 API
    """
    
    def __init__(self, config: AIConfig):
        super().__init__(config)
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """初始化 OpenAI 客户端"""
        try:
            from openai import AsyncOpenAI
            
            self.client = AsyncOpenAI(
                api_key=self.config.api_key or os.getenv("OPENAI_API_KEY"),
                base_url=self.config.base_url or os.getenv("OPENAI_BASE_URL"),
            )
        except ImportError:
            raise ImportError("请安装 openai 包: pip install openai")
    
    async def generate(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """同步生成"""
        response = await self.client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=kwargs.get('temperature', self.config.temperature),
            max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
            stream=False,
        )
        return response.choices[0].message.content
    
    async def generate_stream(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式生成"""
        stream = await self.client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=kwargs.get('temperature', self.config.temperature),
            max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
            stream=True,
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content


class AIEngine:
    """AI 引擎主类 - 协调 Provider 和 Prompt Manager"""
    
    def __init__(self, prompt_manager):
        self.prompt_mgr = prompt_manager
        self.provider = None
        self.current_config = AIConfig()
    
    def _get_provider(self, model: str = None) -> BaseAIProvider:
        """获取或创建 AI Provider"""
        target_model = model or self.current_config.model
        self.current_config.model = target_model
        
        # 根据 model 名称推断 provider 和配置
        if "grok" in target_model.lower():
            self.current_config.provider = "grok"
            self.current_config.api_key = os.getenv("GROK_API_KEY", "")
            self.current_config.base_url = "https://api.x.ai/v1"
        elif "claude" in target_model.lower():
            self.current_config.provider = "claude"
            self.current_config.api_key = os.getenv("CLAUDE_API_KEY", "")
            # Claude 可能需要通过 Anthropic SDK 或代理
        else:  # 默认 OpenAI
            self.current_config.provider = "openai"
            self.current_config.api_key = os.getenv("OPENAI_API_KEY", "")
        
        if not self.provider or self.provider.config.model != target_model:
            self.provider = OpenAIProvider(self.current_config)
        
        return self.provider
    
    async def generate_streaming(
        self,
        task_type: str,
        context: dict,
        model: str = None,
        **extra_vars
    ) -> AsyncGenerator[str, None]:
        """
        流式生成主方法
        
        Args:
            task_type: 任务类型 (outline/chapter/continuation/polish/consistency/dialogue)
            context: 上下文字典 (project, chapter, editor_content等)
            model: 模型名称
            extra_vars: 额外的模板变量
        """
        # 获取模板
        system_prompt, user_prompt = self.prompt_mgr.get_template(
            task_type,
            **self._prepare_variables(context, task_type, **extra_vars)
        )
        
        # 获取 provider 并生成
        provider = self._get_provider(model)
        
        async for chunk in provider.generate_stream(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        ):
            yield chunk
    
    def _prepare_variables(self, context: dict, task_type: str, **extras) -> dict:
        """准备模板变量"""
        project = context.get('project', {})
        chapter = context.get('chapter', {})
        
        base_vars = {
            # 项目级别变量
            'GENRE': project.get('genre', '奇幻'),
            'THEME': project.get('theme', '成长与冒险'),
            'CHARACTER_COUNT': str(len(project.get('characters', []))),
            'TARGET_CHAPTERS': project.get('target_chapters', '20'),
            'WRITING_STYLE': project.get('writing_style', '细腻描写，节奏紧凑'),
            
            # 章节级别变量
            'PREVIOUS_CONTEXT': self._build_previous_context(context),
            'CHAPTER_OUTLINE': chapter.get('outline', '待填写本章大纲'),
            'CHARACTERS_PRESENT': self._format_characters(project.get('characters', [])),
            'WORD_COUNT_TARGET': project.get('word_count_target', '2000-3000字'),
            
            # 编辑器相关
            'EXISTING_CONTENT': context.get('editor_content', '')[-1500:],  # 最后1500字符
            'LAST_PARAGRAPH': self._get_last_paragraph(context.get('editor_content', '')),
            
            # 检查相关
            'CONTENT_TO_CHECK': context.get('editor_content', ''),
            'CHARACTER_DATABASE': self._build_character_db(project.get('characters', [])),
            'TIMELINE': project.get('timeline', '暂无时间线记录'),
            'WORLD_RULES': project.get('world_rules', '暂无特殊规则'),
            
            # 润色相关
            'ORIGINAL_TEXT': context.get('selected_text', context.get('editor_content', '')),
            'POLISH_TYPE': extras.get('polish_type', '全面润色'),
            'STYLE_GUIDE': project.get('style_guide', ''),
        }
        
        # 合并额外变量
        base_vars.update(extras)
        
        # 清理空值
        return {k: (v if v else '[待填写]') for k, v in base_vars.items()}
    
    def _build_previous_context(self, context: dict) -> str:
        """构建前文章节摘要"""
        chapters = context.get('project', {}).get('chapters', [])
        current_idx = None
        
        # 找到当前章节索引
        for idx, ch in enumerate(chapters):
            if ch.get('id') == context.get('chapter', {}).get('id'):
                current_idx = idx
                break
        
        if current_idx is None or current_idx == 0:
            return "这是故事的开篇。"
        
        # 获取前几章的简要摘要
        summaries = []
        for ch in chapters[:current_idx]:
            summary = ch.get('summary', '') or ch.get('content', '')[:200]
            summaries.append(f"第{chapters.index(ch)+1}章 {ch.get('title', '')}: {summary}...")
        
        return "\n".join(summaries) if summaries else "前文情节发展中。"
    
    def _format_characters(self, characters: list) -> str:
        """格式化角色信息"""
        if not characters:
            return "[尚未设定角色]"
        
        formatted = []
        for char in characters[:6]:  # 限制数量避免 token 过长
            formatted.append(
                f"- {char.get('name', '未命名')}: "
                f"{char.get('role', '主角')} | "
                f"{char.get('personality', '性格待补充')} | "
                f"{char.get('appearance', '外貌待补充')}"
            )
        return "\n".join(formatted)
    
    def _get_last_paragraph(self, text: str) -> str:
        """获取最后一段"""
        paragraphs = text.strip().split('\n\n')
        return paragraphs[-1] if paragraphs else ""
    
    def _build_character_db(self, characters: list) -> str:
        """构建角色数据库字符串"""
        if not characters:
            return "[无角色数据]"
        
        db_entries = []
        for char in characters:
            entry = f"""
角色: {char.get('name', '?')}
- 性别/年龄: {char.get('gender', '?')} / {char.get('age', '?')}
- 性格特征: {char.get('personality', '?')}
- 外貌描述: {char.get('appearance', '?')}
- 特殊能力: {char.get('abilities', '无')}
- 人际关系: {char.get('relationships', '?')}
- 重要经历: {char.get('background', '?')}
- 说话风格: {char.get('speech_pattern', '?')}
"""
            db_entries.append(entry)
        
        return "\n".join(db_entries)
```

#### 3.2 流式输出处理器 - ai_engine/streaming_handler.py

```python
"""
StreamingHandler - 异步流式输出处理器
连接 AI 引擎和 Flet GUI 的桥梁
"""

import asyncio
from typing import AsyncGenerator
from dataclasses import dataclass, field


@dataclass
class StreamState:
    """流式状态"""
    is_active: bool = False
    should_stop: bool = False
    accumulated_text: str = ""
    chunks_received: int = 0


class StreamingHandler:
    """流式输出处理器"""
    
    def __init__(self):
        self.state = StreamState()
        self._callbacks = []
    
    def register_callback(self, callback):
        """注册回调函数（用于更新 GUI）"""
        self._callbacks.append(callback)
    
    async def process_stream(
        self,
        stream_generator: AsyncGenerator[str, None],
        update_interval: int = 30  # 每 N 个字符更新一次 GUI
    ):
        """
        处理流式生成
        
        Args:
            stream_generator: AI 引擎的异步生成器
            update_interval: GUI 更新频率（字符数）
        """
        self.state = StreamState(is_active=True)
        
        try:
            async for chunk in stream_generator:
                if self.state.should_stop:
                    break
                
                self.state.accumulated_text += chunk
                self.state.chunks_received += 1
                
                # 触发回调（带频率控制）
                if self.state.chunks_received % update_interval == 0:
                    await self._notify_callbacks(chunk)
            
            # 最终通知
            await self._notify_callbacks("", final=True)
            
        finally:
            self.state.is_active = False
    
    async def _notify_callbacks(self, chunk: str, final: bool = False):
        """通知所有注册的回调"""
        for callback in self._callbacks:
            if asyncio.iscoroutinefunction(callback):
                await callback(chunk, final=final)
            else:
                callback(chunk, final=final)
    
    def stop(self):
        """请求停止生成"""
        self.state.should_stop = True
    
    def get_accumulated_text(self) -> str:
        """获取累积的全部文本"""
        return self.state.accumulated_text
    
    def reset(self):
        """重置状态"""
        self.state = StreamState()
```

#### 3.3 上下文构建器 - ai_engine/context_builder.py

```python
"""
ContextBuilder - 智能上下文构建器
根据不同任务类型组装最优的提示词上下文
"""

from typing import Dict, List, Any


class ContextBuilder:
    """上下文构建器"""
    
    MAX_CONTEXT_LENGTH = 8000  # 最大上下文字符数
    
    @staticmethod
    def build_for_outline(project: Dict) -> Dict:
        """构建大纲生成的上下文"""
        return {
            'genre': project.get('genre', '现代'),
            'theme': project.get('theme', ''),
            'character_count': len(project.get('characters', [])),
            'target_chapters': project.get('target_chapters', '20'),
            'writing_style': project.get('writing_style', ''),
            'plot_summary': project.get('plot_summary', ''),
            'target_audience': project.get('target_audience', '成人读者'),
        }
    
    @staticmethod
    def build_for_chapter(project: Dict, chapter: Dict, previous_chapters: List[Dict]) -> Dict:
        """构建章节撰写的上下文"""
        # 构建前文摘要
        prev_summaries = []
        for ch in previous_chapters[-3:]:  # 只取最近3章
            summary = ch.get('summary', ch.get('content', '')[:300])
            prev_summaries.append(f"第{previous_chapters.index(ch)+1}章《{ch.get('title', '')}》: {summary}")
        
        return {
            'previous_context': '\n'.join(prev_summaries) if prev_summaries else '这是故事的第一章。',
            'chapter_outline': chapter.get('outline', ''),
            'characters_present': ContextBuilder._extract_scene_characters(chapter, project),
            'writing_style': project.get('writing_style', ''),
            'word_count_target': chapter.get('word_count_target', '2000-3000字'),
            'scene_setting': chapter.get('scene_setting', ''),
            'emotional_tone': chapter.get('emotional_tone', ''),
        }
    
    @staticmethod
    def build_for_continuation(editor_content: str, project: Dict) -> Dict:
        """构建续写的上下文"""
        # 获取最后部分内容作为续写基础
        last_part = editor_content[-2000:] if len(editor_content) > 2000 else editor_content
        
        # 分割段落
        paragraphs = [p.strip() for p in last_part.split('\n\n') if p.strip()]
        last_paragraph = paragraphs[-1] if paragraphs else ''
        
        return {
            'existing_content': last_part,
            'last_paragraph': last_paragraph,
            'plot_direction': '根据上文自然延续剧情发展',
            'characters_present': ContextBuilder._detect_recent_characters(editor_content, project),
        }
    
    @staticmethod
    def build_for_polish(selected_text: str, polish_type: str, project: Dict) -> Dict:
        """构建润色的上下文"""
        return {
            'original_text': selected_text,
            'polish_type': polish_type,
            'style_guide': project.get('style_guide', ''),
            'genre_conventions': project.get('genre', ''),
        }
    
    @staticmethod
    def build_for_consistency(content: str, project: Dict) -> Dict:
        """构建一致性检查的上下文"""
        return {
            'content_to_check': content,
            'character_database': ContextBuilder._format_full_character_db(project.get('characters', [])),
            'timeline': ContextBuilder._extract_timeline(project),
            'world_rules': project.get('world_rules', ''),
        }
    
    @staticmethod
    def _extract_scene_characters(chapter: Dict, project: Dict) -> str:
        """提取场景中的角色"""
        scene_chars = chapter.get('characters_in_scene', [])
        all_chars = project.get('characters', [])
        
        if not scene_chars:
            # 如果没有指定，返回主要角色
            return '\n'.join([
                f"- {c.get('name')}: {c.get('role', '')}" 
                for c in all_chars[:4]
            ])
        
        formatted = []
        for char_id in scene_chars:
            char = next((c for c in all_chars if c.get('id') == char_id), None)
            if char:
                formatted.append(
                    f"- {char.get('name')}: "
                    f"{char.get('personality', '')} | "
                    f"当前状态: {char.get('current_status', '正常')}"
                )
        return '\n'.join(formatted) if formatted else '[未指定出场角色]'
    
    @staticmethod
    def _detect_recent_characters(text: str, project: Dict) -> str:
        """检测最近出现的角色名字"""
        all_chars = project.get('characters', [])
        detected = []
        
        for char in all_chars:
            name = char.get('name', '')
            if name and name in text[-500:]:  # 只检查最近500字符
                detected.append(name)
        
        return ', '.join(detected) if detected else '根据上文判断'
    
    @staticmethod
    def _format_full_character_db(characters: List[Dict]) -> str:
        """格式化完整的角色数据库"""
        if not characters:
            return '[无角色数据]'
        
        entries = []
        for char in characters:
            entry = f"""【{char.get('name', '未知')}】
- 身份: {char.get('role', '?')}
- 年龄: {char.get('age', '?')}
- 性格: {char.get('personality', '?')}
- 外貌: {char.get('appearance', '?')}
- 能力: {char.get('abilities', '无')}
- 关系: {char.get('relationships', '?')}
- 背景: {char.get('background', '?')}
- 语言特点: {char.get('speech_pattern', '?')}
- 当前状态: {char.get('current_status', '正常')}
---
"""
            entries.append(entry)
        
        return '\n'.join(entries)
    
    @staticmethod
    def _extract_timeline(project: Dict) -> str:
        """提取时间线"""
        events = project.get('timeline_events', [])
        if not events:
            return '[暂无时间线记录]'
        
        lines = []
        for event in events[-10:]:  # 最近10个事件
            lines.append(f"- {event.get('time', '?')}: {event.get('description', '')}")
        return '\n'.join(lines)
```

---

### NAF-DESKTOP-ITEM-4.0 [数据持久化层]

#### 4.1 数据模型 - data/models.py

```python
"""
Data Models - 数据模型定义
使用 Pydantic 进行验证
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import uuid4


class Character(BaseModel):
    """角色模型"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., min_length=1, max_length=50)
    role: str = "配角"  # 主角/反派/配角/NPC
    age: Optional[str] = None
    gender: Optional[str] = None
    personality: str = ""
    appearance: str = ""
    abilities: str = ""
    relationships: str = ""
    background: str = ""
    speech_pattern: str = ""  # 说话风格
    current_status: str = "正常"
    notes: str = ""


class Chapter(BaseModel):
    """章节模型"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = "未命名章节"
    order: int = 0
    content: str = ""
    outline: str = ""  # 大纲要点
    summary: str = ""  # 内容摘要（用于上下文）
    word_count_target: str = "2000-3000字"
    characters_in_scene: List[str] = []  # 出场角色 ID 列表
    scene_setting: str = ""
    emotional_tone: str = ""
    status: str = "draft"  # draft/revised/final
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def calculate_word_count(self) -> int:
        """计算字数"""
        return len(self.content.replace(' ', ''))


class NovelSettings(BaseModel):
    """小说设置模型"""
    title: str = "我的新小说"
    genre: str = "现代"  # 类型
    theme: str = ""  # 主题
    target_chapters: str = "20"
    writing_style: str = ""
    target_audience: str = "成人读者"
    plot_summary: str = ""
    world_rules: str = ""
    style_guide: str = ""
    timeline_events: List[Dict[str, str]] = []
    
    # 高级设置
    pov: str = "第三人称"  # 视角
    tense: str = "过去时"  # 时态
    tone: str = "严肃"


class Project(BaseModel):
    """项目模型"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = "未命名项目"
    settings: NovelSettings = Field(default_factory=NovelSettings)
    characters: List[Character] = Field(default_factory=list)
    chapters: List[Chapter] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    file_path: Optional[str] = None  # 本地存储路径
    
    def add_character(self, character: Character):
        """添加角色"""
        self.characters.append(character)
        self.updated_at = datetime.now()
    
    def add_chapter(self, chapter: Chapter):
        """添加章节"""
        chapter.order = len(self.chapters) + 1
        self.chapters.append(chapter)
        self.updated_at = datetime.now()
    
    def get_total_word_count(self) -> int:
        """获取总字数"""
        return sum(ch.calculate_word_count() for ch in self.chapters)
    
    def to_dict(self) -> dict:
        """转换为字典（用于 JSON 序列化）"""
        return self.model_dump(mode='json')
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Project':
        """从字典创建实例"""
        return cls(**data)
```

#### 4.2 项目管理器 - data/project_manager.py

```python
"""
ProjectManager - 项目持久化管理器
支持: JSON 文件存储、SQLite 存储（可选）
"""

import json
import os
from typing import List, Optional
from datetime import datetime
from data.models import Project, Chapter, Character


class ProjectManager:
    """项目管理器"""
    
    DATA_DIR = "projects"
    EXTENSION = ".json"
    
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or self.DATA_DIR
        os.makedirs(self.data_dir, exist_ok=True)
    
    def create_project(self, title: str, **settings) -> Project:
        """创建新项目"""
        project = Project(title=title)
        
        # 应用初始设置
        if settings:
            for key, value in settings.items():
                if hasattr(project.settings, key):
                    setattr(project.settings, key, value)
        
        # 保存到磁盘
        self.save_project(project)
        
        return project
    
    def save_project(self, project: Project) -> bool:
        """保存项目到磁盘"""
        try:
            file_path = os.path.join(self.data_dir, f"{project.id}{self.EXTENSION}")
            project.file_path = file_path
            project.updated_at = datetime.now()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(project.to_dict(), f, ensure_ascii=False, indent=2, default=str)
            
            return True
        except Exception as e:
            print(f"保存项目失败: {e}")
            return False
    
    def load_project(self, project_id: str) -> Optional[Project]:
        """加载项目"""
        file_path = os.path.join(self.data_dir, f"{project_id}{self.EXTENSION}")
        
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            project = Project.from_dict(data)
            project.file_path = file_path
            return project
        except Exception as e:
            print(f"加载项目失败: {e}")
            return None
    
    def delete_project(self, project_id: str) -> bool:
        """删除项目"""
        file_path = os.path.join(self.data_dir, f"{project_id}{self.EXTENSION}")
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    
    def list_projects(self) -> List[dict]:
        """列出所有项目（简化信息）"""
        projects = []
        
        for filename in os.listdir(self.data_dir):
            if filename.endswith(self.EXTENSION):
                file_path = os.path.join(self.data_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    projects.append({
                        'id': data.get('id', ''),
                        'title': data.get('title', '未命名'),
                        'chapters': data.get('chapters', []),
                        'updated_at': data.get('updated_at', ''),
                        'settings': data.get('settings', {}),
                    })
                except Exception as e:
                    print(f"读取项目失败 {filename}: {e}")
        
        # 按更新时间排序
        projects.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        
        return projects
    
    def export_project(self, project: Project, format_type: str = "md") -> str:
        """导出项目"""
        if format_type == "md":
            return self._export_markdown(project)
        elif format_type == "txt":
            return self._export_txt(project)
        else:
            raise ValueError(f"不支持的导出格式: {format_type}")
    
    def _export_markdown(self, project: Project) -> str:
        """导出为 Markdown"""
        lines = [
            f"# {project.settings.title}\n",
            f"**类型**: {project.settings.genre}",
            f"**主题**: {project.settings.theme}",
            f"**作者**: NovelAI Forge 用户",
            f"**导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
            "---\n",
        ]
        
        # 角色
        if project.characters:
            lines.append("## 角色介绍\n")
            for char in project.characters:
                lines.append(f"### {char.name}")
                lines.append(f"- **身份**: {char.role}")
                lines.append(f"- **特征**: {char.personality}")
                lines.append(f"- **外貌**: {char.appearance}")
                lines.append("")
        
        # 章节
        for idx, chapter in enumerate(project.chapters, 1):
            lines.append(f"## 第{idx}章 {chapter.title}\n")
            lines.append(chapter.content)
            lines.append("\n---\n")
        
        return "\n".join(lines)
    
    def _export_txt(self, project: Project) -> str:
        """导出为纯文本"""
        lines = [
            project.settings.title,
            "=" * len(project.settings.title),
            "",
        ]
        
        for idx, chapter in enumerate(project.chapters, 1):
            lines.append(f"第{idx}章 {chapter.title}")
            lines.append("-" * 30)
            lines.append(chapter.content)
            lines.append("")
        
        return "\n".join(lines)
```

---

### NAF-DESKTOP-ITEM-5.0 [对话框组件]

#### 5.1 新建项目对话框 - gui/components/dialogs/new_project_dialog.py

```python
"""
NewProjectDialog - 新建项目对话框
引导用户输入基本信息并创建项目
"""

import flet as ft
from data.models import NovelSettings, Character


class NewProjectDialog:
    """新建项目对话框"""
    
    def __init__(self, app):
        self.app = app
        self.dialog = None
        
        # 表单字段
        self.title_field = None
        self.genre_dropdown = None
        self.theme_field = None
        self.style_field = None
        self.chapters_field = None
    
    def build(self) -> ft.AlertDialog:
        """构建对话框"""
        self.title_field = ft.TextField(
            label="小说标题",
            hint_text="例如: 星际迷途",
            autofocus=True,
        )
        
        self.genre_dropdown = ft.Dropdown(
            label="小说类型",
            options=[
                ft.dropdown.Option("现代", "现代都市"),
                ft.dropdown.Option("奇幻", "奇幻冒险"),
                ft.dropdown.Option("科幻", "科幻未来"),
                ft.dropdown.Option("历史", "历史架空"),
                ft.dropdown.Option("悬疑", "悬疑推理"),
                ft.dropdown.Option("言情", "浪漫爱情"),
                ft.dropdown.Option("武侠", "武侠江湖"),
                ft.dropdown.Option("其他", "其他类型"),
            ],
            value="奇幻",
            width=400,
        )
        
        self.theme_field = ft.TextField(
            label="故事主题",
            hint_text="例如: 在绝境中寻找希望的意义",
            multiline=True,
            min_lines=2,
            max_lines=3,
        )
        
        self.style_field = ft.TextField(
            label="写作风格偏好",
            hint_text="例如: 细腻的心理描写，紧凑的叙事节奏",
            multiline=True,
            min_lines=2,
            max_lines=3,
        )
        
        self.chapters_field = ft.TextField(
            label="预计章节数",
            hint_text="例如: 20-30",
            value="20",
        )
        
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("📖 创建新小说项目"),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        self.title_field,
                        self.genre_dropdown,
                        self.theme_field,
                        self.style_field,
                        self.chapters_field,
                    ],
                    tight=True,
                    scroll=ft.ScrollMode.AUTO,
                ),
                width=450,
                height=400,
            ),
            actions=[
                ft.TextButton("取消", on_click=self._on_cancel),
                ft.ElevatedButton("创建项目", on_click=self._on_create, icon=ft.icons.ADD),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        return self.dialog
    
    def _on_create(self, e):
        """创建项目"""
        title = self.title_field.value.strip()
        if not title:
            self.app.show_snack_bar("请输入小说标题", error=True)
            return
        
        # 创建项目
        project = self.app.project_mgr.create_project(
            title=title,
            genre=self.genre_dropdown.value,
            theme=self.theme_field.value,
            writing_style=self.style_field.value,
            target_chapters=self.chapters_field.value,
        )
        
        # 添加默认主角
        protagonist = Character(
            name="主角",
            role="主角",
            personality="待完善",
            notes="请在设置中完善角色详情",
        )
        project.add_character(protagonist)
        self.app.project_mgr.save_project(project)
        
        # 关闭对话框并刷新UI
        self.dialog.open = False
        self.app.sidebar_left.refresh_projects()
        self.app.current_project = project
        self.app.show_snack_bar(f"✅ 项目 '{title}' 已创建！")
        self.app.page.update()
    
    def _on_cancel(self, e):
        """取消"""
        self.dialog.open = False
        self.app.page.update()
```

#### 5.2 导出对话框 - gui/components/dialogs/export_dialog.py

```python
"""
ExportDialog - 导出对话框
"""

import flet as ft
from pathlib import Path


class ExportDialog:
    """导出对话框"""
    
    def __init__(self, app, format_type: str = "md"):
        self.app = app
        self.format_type = format_type
        self.dialog = None
        self.path_field = None
    
    def build(self) -> ft.AlertDialog:
        """构建对话框"""
        default_name = f"{self.app.current_project.settings.title}.{self.format_type}"
        
        self.path_field = ft.TextField(
            label="保存路径",
            value=f"exports/{default_name}",
            prefix_icon=ft.icons.SAVE,
        )
        
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"📤 导出为 {'Markdown' if self.format_type == 'md' else 'TXT'}"),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        self.path_field,
                        ft.Text(
                            "文件将保存在项目目录下",
                            size=12,
                            color=ft.colors.OUTLINE,
                        ),
                    ],
                    tight=True,
                ),
                width=400,
            ),
            actions=[
                ft.TextButton("取消", on_click=lambda _: self._close()),
                ft.ElevatedButton(
                    "导出",
                    on_click=self._on_export,
                    icon=ft.icons.DOWNLOAD,
                ),
            ],
        )
        
        return self.dialog
    
    def _on_export(self, e):
        """执行导出"""
        if not self.app.current_project:
            self.app.show_snack_bar("没有可导出的项目", error=True)
            return
        
        try:
            # 生成内容
            content = self.app.project_mgr.export_project(
                self.app.current_project,
                self.format_type
            )
            
            # 确保目录存在
            save_path = Path(self.path_field.value)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入文件
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self._close()
            self.app.show_snack_bar(f"✅ 已导出到: {save_path}")
            
        except Exception as ex:
            self.app.show_snack_bar(f"导出失败: {str(ex)}", error=True)
    
    def _close(self):
        """关闭对话框"""
        self.dialog.open = False
        self.app.page.update()
```

---

## Commands

### 安装与运行命令

```bash
# 1. 进入项目目录
cd d:\code\AiSpeak

# 2. 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. 安装依赖
pip install flet langchain openai pydantic python-dotenv aiofiles

# 4. 配置环境变量
copy .env.example .env
# 编辑 .env 文件，填入你的 API Key

# 5. 运行桌面应用
flet run main.py

# 或者直接用 Python 运行（开发模式）
python main.py

# 6. 打包为独立可执行文件（发布时）
flet pack main.py
# 生成的 EXE 文件在 build 目录下
```

### 快速测试命令

```bash
# 测试 GUI 是否能正常启动
python -c "import flet; print('Flet 版本:', flet.__version__)"

# 测试 AI 引擎是否能加载模板
python -c "from ai_engine.prompt_manager import PromptTemplateManager; pm = PromptTemplateManager(); print('已加载模板:', list(pm.templates.keys()))"

# 测试数据层
python -c "from data.project_manager import ProjectManager; pm = ProjectManager(); print('项目目录:', pm.data_dir)"
```

---

## Quality Assurance Task Checklist

### 必须通过的质量检查项

- [ ] **QA-DESKTOP-1.1 [窗口启动测试]**
  - [ ] 执行 `flet run main.py` 或 `python main.py`
  - [ ] 桌面窗口正常弹出，无报错
  - [ ] 窗口标题显示 "📖 NovelAI Forge - AI 小说创作助手"
  - [ ] 窗口尺寸约 1400x900，可调整大小
  - [ ] 支持暗色主题（默认）

- [ ] **QA-DESKTOP-1.2 [GUI 布局完整性]**
  - [ ] 顶部工具栏可见：Logo + 标题 + 新建/打开/保存/导出/设置按钮
  - [ ] 左侧边栏可见：项目列表区域 + 章节导航区域
  - [ ] 中央编辑器可见：大文本框 + 字数统计
  - [ ] 右侧 AI 边栏可见：模型选择 + 6个功能按钮 + 输出预览区
  - [ ] 各区域之间有分隔线，布局比例合理

- [ ] **QA-DESKTOP-1.3 [提示词模板加载]**
  - [ ] `backend/prompts/` 目录存在且包含以下文件:
    - [ ] README.md
    - [ ] outline_prompt.txt ✓
    - [ ] chapter_prompt.txt ✓
    - [ ] continuation_prompt.txt ✓
    - [ ] polish_prompt.txt ✓
    - [ ] consistency_prompt.txt ✓
    - [ ] dialogue_prompt.txt ✓
    - [ ] custom/ 目录 ✓
  - [ ] 所有模板包含 `[CUSTOM_SYSTEM_PROMPT_HERE]` 占位符
  - [ ] 模板变量使用 `{{VARIABLE_NAME}}` 格式
  - [ ] 启动时 PromptTemplateManager 能正确加载所有模板

- [ ] **QA-DESKTOP-1.4 [项目管理功能]**
  - [ ] 点击"新建项目"按钮弹出对话框
  - [ ] 能输入标题、选择类型、填写主题等信息
  - [ ] 点击"创建"后项目出现在左侧列表
  - [ ] 点击项目能选中并在章节区显示章节
  - [ ] 能新建章节并显示在列表中
  - [ ] 点击章节能在编辑器中加载内容
  - [ ] 编辑器内容变化后触发自动保存（3秒后）

- [ ] **QA-DESKTOP-1.5 [AI 功能按钮测试]**
  - [ ] 6个 AI 按钮均可点击：
    - [ ] 📋 生成大纲
    - [ ] ✍️ 生成章节
    - [ ] ➡️ 续写
    - [ ] ✨ 润色
    - [ ] 🔍 一致性检查
    - [ ] 💬 对话生成
  - [ ] 点击按钮后在右侧输出区显示"等待 AI 输出..."
  - [ ] 生成过程中"⏹ 停止生成"按钮出现
  - [ ] 点击停止按钮能中断生成
  - [ ] 生成完成后显示"✅ 生成完成！"

- [ ] **QA-DESKTOP-1.6 [流式输出效果]**
  - [ ] AI 响应内容在右侧区域逐字/逐句显示
  - [ ] 输出区域支持滚动查看长内容
  - [ ] 输出文本可选择和复制
  - [ ] "复制到编辑器"按钮能将 AI 输出插入编辑器
  - [ ] "清空"按钮能清除输出区域

- [ ] **QA-DESKTOP-1.7 [导出功能]**
  - [ ] 点击导出按钮弹出格式选择菜单
  - [ ] 选择"导出为 Markdown"或"导出为 TXT"
  - [ ] 导出对话框允许修改保存路径
  - [ ] 点击导出后文件成功创建在指定路径
  - [ ] 导出的文件内容格式正确

- [ ] **QA-DESKTOP-1.8 [环境配置]**
  - [ ] `.env.example` 文件存在
  - [ ] 包含 OPENAI_API_KEY、GROK_API_KEY、CLAUDE_API_KEY 等变量
  - [ ] `requirements.txt` 包含所有必要依赖
  - [ ] 无需 Web 浏览器即可运行（纯桌面应用）

- [ ] **QA-DESKTOP-1.9 [错误处理]**
  - [ ] 未选择项目时点击 AI 按钮显示友好提示
  - [ ] API Key 未配置时显示明确错误信息
  - [ ] 网络错误时有友好的错误提示
  - [ ] 应用不会因异常而崩溃

- [ ] **QA-DESKTOP-2.0 [代码质量]**
  - [ ] 所有文件使用 UTF-8 编码
  - [ ] 中文注释清晰易懂
  - [ ] 函数和类有 docstring
  - [ ] 类型注解完整
  - [ ] 无硬编码的敏感信息

---

## Appendix: 开发路线图

### Phase 1: MVP (当前文档覆盖范围) ✅
- [x] 基础 GUI 框架搭建
- [x] 项目管理（CRUD）
- [x] 富文本编辑器
- [x] AI 工具栏（6个功能）
- [x] 流式输出
- [x] 基础导出功能

### Phase 2: 增强 (后续迭代)
- [ ] 角色详细编辑界面
- [ ] 大纲可视化（思维导图样式）
- [ ] 多章节批量生成
- [ ] AI 对话历史记录
- [ ] 自定义提示词编辑器
- [ ] 主题切换（亮色/暗色/自定义）
- [ ] 快捷键支持
- [ ] 撤销/重做功能

### Phase 3: 专业版 (远期规划)
- [ ] QWen Bot 集成（需要 Chrome 环境）
- [ ] 多语言界面
- [ ] 云同步（可选）
- [ ] 协作编辑
- [ ] 插件系统
- [ ] 出版级排版导出（EPUB/PDF）

---

## 总结

本文档提供了 **NovelAI Forge Desktop** 的完整实现蓝图：

### ✅ 已交付物

1. **完整的项目目录结构** - 15+ 个模块化文件
2. **Flet GUI 全套组件** - 工具栏、三栏布局、对话框
3. **AI 引擎核心** - 多 Provider 支持、流式处理、上下文智能构建
4. **数据持久化层** - JSON 文件存储、Pydantic 模型验证
5. **6 个专业提示词模板** - 已创建于 `backend/prompts/`
6. **详细的 QA 检查清单** - 20+ 项验收标准

### 🎯 核心特性

- ✨ **纯 Python**: 无需 Node.js/Docker/Web 服务器
- 🖥️ **现代桌面 UI**: 基于 Flutter/Flet 的 Material Design 3
- 🤖 **强大 AI 集成**: LangChain + OpenAI + 流式输出
- 📝 **专业写作工具**: 大纲→章节→续写→润色→检查 全流程
- 💾 **本地优先**: 数据存储在本地，隐私安全
- 🔧 **高度可扩展**: 模块化架构，易于添加新功能

### 📂 关键文件位置

- **主入口**: `main.py`
- **GUI 核心**: `gui/app.py`, `gui/components/`
- **AI 引擎**: `ai_engine/base.py`, `ai_engine/context_builder.py`
- **提示词模板**: `backend/prompts/*.txt`
- **数据层**: `data/project_manager.py`, `data/models.py`

---

**文档版本**: 1.0  
**基于**: TODO_novelai-forge.md (Web 版架构)  
**创建日期**: 2026-04-13  
**状态**: ✅ 完成，准备实施  
**下一步**: 按照 Commands 部分执行安装和测试
