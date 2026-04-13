# NovelAI Forge - 项目初始化与架构文档

## Context

**项目名称**: NovelAI Forge  
**项目类型**: Web 全栈 AI 小说写作软件  
**创建日期**: 2026-04-13  
**当前状态**: 初始化阶段  

### 背景说明

NovelAI Forge 是一个基于 Web 的 AI 辅助小说创作平台，旨在为小说作者提供：
- 智能化的故事生成工具
- 一致性检查与角色管理
- 多模型 AI 支持（OpenAI/Grok/Claude/QWen）
- 富文本编辑器 + AI 协作侧边栏

### 现有资产集成

本项目将集成已有的 **qwen_bot** 爬虫脚本作为 AI 调用选项之一：

**qwen_bot 功能概述**:
- 基于 Selenium 的 QWen (chat.qwen.ai) 自动化交互
- 支持多轮对话与会话管理
- 可选网页搜索功能
- 通过网络请求拦截获取完整 AI 响应数据
- CSV 格式对话记录导出

**集成策略**: 将 qwen_bot 封装为后端 AI Provider 之一，支持通过 REST API 调用 QWen 模型进行小说内容生成。

---

## Architecture Plan

### NAF-PLAN-1.1 [系统总体架构]

```
┌─────────────────────────────────────────────────────────────┐
│                    NovelAI Forge                            │
├─────────────────────────────────────────────────────────────┤
│  Frontend (Next.js 15)                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │ Dashboard │ │ Editor   │ │ Settings │ │ Export       │   │
│  │          │ │ + AI     │ │ Wizard   │ │              │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  Backend (FastAPI)                                          │
│  ┌───────────┐ ┌──────────┐ ┌──────────┐ ┌─────────────┐   │
│  │ Auth      │ │ Projects │ │ AI Engine│ │ Consistency │   │
│  │ (JWT)     │ │ CRUD     │ │ (LangChain+│ │ Checker    │   │
│  │           │ │          │ │ QWen Bot)│ │             │   │
│  └───────────┘ └──────────┘ └──────────┘ └─────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  Database (SQLite/PostgreSQL)                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │ Users    │ │ Novels   │ │ Chapters │ │ Characters   │   │
│  │          │ │          │ │          │ │ & Settings   │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  External Services                                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │ OpenAI   │ │ Grok     │ │ Claude   │ │ QWen (via    │   │
│  │ API      │ │ API      │ │ API      │ │ Selenium)    │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### NAF-PLAN-1.2 [技术栈详情]

#### 前端技术栈
- **框架**: Next.js 15 (App Router)
- **语言**: TypeScript 5.x
- **样式**: Tailwind CSS 3.x + shadcn/ui
- **状态管理**: React Context / Zustand
- **富文本编辑器**: Tiptap 或 Plate
- **HTTP 客户端**: Axios / TanStack Query

#### 后端技术栈
- **框架**: FastAPI (Python 3.12)
- **ORM**: SQLAlchemy 2.x + Alembic 迁移
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **AI 集成**: LangChain + OpenAI-compatible client
- **特殊集成**: qwen_bot (Selenium-based QWen interface)
- **认证**: JWT (PyJWT)

---

## User Stories & MVP Features

### NAF-US-1.0 [用户故事列表]

#### 核心用户故事

- [ ] **US-1.1 [用户注册/登录]**
  - 作为新用户，我希望能够注册账户并登录系统，以便开始我的小说创作项目。
  - **优先级**: P0 (必须)
  - **验收标准**: 支持邮箱密码注册、JWT token 认证、自动续期

- [ ] **US-1.2 [项目管理]**
  - 作为作者，我希望能够创建和管理多个小说项目，每个项目有独立的设置和章节。
  - **优先级**: P0 (必须)
  - **验收标准**: CRUD 操作、项目列表视图、项目切换

- [ ] **US-1.3 [小说设置向导]**
  - 作为作者，我希望通过向导式界面设置小说的基本信息（标题、类型、风格、世界观等）。
  - **优先级**: P0 (必须)
  - **验收标准**: 分步表单、预设模板、自定义字段

- [ ] **US-1.4 [AI 内容生成]**
  - 作为作者，我希望能够使用 AI 工具生成小说内容（大纲、章节、对话、描写等）。
  - **优先级**: P0 (必须)
  - **验收标准**: 
    - 支持多种 AI 模型选择（GPT/Claude/Grok/QWen）
    - 可配置的提示词模板
    - 流式输出支持
    - 上下文感知（基于已有内容）

- [ ] **US-1.5 [富文本编辑器 + AI 侧边栏]**
  - 作为作者，我希望在编辑器中编写内容时，能够随时调用 AI 辅助功能。
  - **优先级**: P0 (必须)
  - **验收标准**:
    - Markdown/富文本编辑
    - AI 侧边栏面板
    - 选中文本调用 AI
    - 实时建议插入

- [ ] **US-1.6 [一致性检查]**
  - 作为作者，我希望系统能够检查小说内容的一致性（角色特征、情节逻辑、时间线等）。
  - **优先级**: P1 (重要)
  - **验收标准**: 
    - 角色数据库比对
    - 情节矛盾检测
    - 时间线验证
    - 问题高亮与修复建议

- [ ] **US-1.7 [导出功能]**
  - 作为作者，我希望能够将完成的小说导出为多种格式（TXT/DOCX/PDF/EPUB）。
  - **优先级**: P1 (重要)
  - **验收标准**: 多格式支持、格式保留、封面定制

#### 技术用户故事

- [ ] **US-2.1 [QWen Bot 集成]**
  - 作为开发者，我需要将现有的 qwen_bot 脚本集成为 AI Provider，以便用户可以选择使用 QWen 模型。
  - **优先级**: P0 (必须)
  - **验收标准**:
    - 异步封装 qwen_bot 功能
    - 会话管理与复用
    - 错误处理与重试机制
    - 与 LangChain 接口兼容

---

## Task Items

### NAF-ITEM-1.1 [需求分析与架构设计]
- [x] 分析项目需求并编写用户故事
- [ ] 设计系统整体架构图
- [ ] 定义技术栈选型理由
- [ ] 编写接口规范文档

### NAF-ITEM-1.2 [数据库模型设计]
- [ ] 设计 Users 表结构
- [ ] 设计 Novels 表结构
- [ ] 设计 Chapters 表结构
- [ ] 设计 Characters 表结构
- [ ] 设计 WorldSettings 表结构
- [ ] 设计 AISessions 表结构（用于记录 AI 对话历史）
- [ ] 设计 GenerationTasks 表结构（异步任务跟踪）
- [ ] 创建 SQLAlchemy ORM 模型文件
- [ ] 编写 Alembic 迁移脚本模板

### NAF-ITEM-1.3 [REST API 端点设计]

#### Auth API (`/api/v1/auth`)
```
POST   /auth/register          # 用户注册
POST   /auth/login             # 用户登录
POST   /auth/refresh           # 刷新 token
GET    /auth/me                # 获取当前用户信息
PUT    /auth/profile           # 更新用户资料
```

#### Projects API (`/api/v1/projects`)
```
GET    /projects               # 获取项目列表
POST   /projects               # 创建新项目
GET    /projects/{id}          # 获取项目详情
PUT    /projects/{id}          # 更新项目
DELETE /projects/{id}          # 删除项目
POST   /projects/{id}/settings # 更新小说设置
GET    /projects/{id}/settings # 获取小说设置
```

#### Chapters API (`/api/v1/chapters`)
```
GET    /projects/{id}/chapters        # 获取章节列表
POST   /projects/{id}/chapters        # 创建新章节
GET    /chapters/{chapter_id}         # 获取章节详情
PUT    /chapters/{chapter_id}         # 更新章节内容
DELETE /chapters/{chapter_id}         # 删除章节
PUT    /chapters/{chapter_id}/reorder # 调整章节顺序
```

#### Characters API (`/api/v1/characters`)
```
GET    /projects/{id}/characters      # 获取角色列表
POST   /projects/{id}/characters      # 创建角色
GET    /characters/{char_id}          # 获取角色详情
PUT    /characters/{char_id}          # 更新角色
DELETE /characters/{char_id}          # 删除角色
```

#### AI Generation API (`/api/v1/ai`)
```
POST   /ai/generate                   # 生成内容（同步）
POST   /ai/generate/stream            # 生成内容（流式 SSE）
POST   /ai/chat                       # 多轮对话
GET    /ai/models                     # 获取可用模型列表
GET    /ai/providers                  # 获取 AI 提供商列表
POST   /ai/consistency-check          # 执行一致性检查
GET    /ai/tasks/{task_id}            # 获取任务状态（异步）
```

#### Export API (`/api/v1/export`)
```
POST   /export                        # 导出小说
GET    /export/{job_id}               # 获取导出状态
GET    /export/{job_id}/download      # 下载导出文件
```

### NAF-ITEM-1.4 [前端路由设计]

```typescript
// app/router.ts (概念设计)
const routes = {
  // 公开页面
  '/': 'Home Page',
  '/login': 'Login',
  '/register': 'Register',

  // 受保护页面（需要认证）
  '/dashboard': 'Dashboard - 项目列表',
  '/project/new': '新建项目向导',
  '/project/[id]': '项目概览',
  '/project/[id]/editor': '编辑器主界面',
  '/project/[id]/settings': '小说设置',
  '/project/[id]/characters': '角色管理',
  '/project/[id]/outline': '大纲管理',
  '/project/[id]/export': '导出中心',
  '/profile': '个人设置',
};
```

### NAF-ITEM-1.5 [AI 生成流程设计]

#### AI Provider 架构（核心）

```python
# backend/services/ai/base.py (概念代码)
from abc import ABC, abstractmethod
from typing import AsyncGenerator

class BaseAIProvider(ABC):
    """AI 提供商基类"""
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        context: list[dict] | None = None,
        **kwargs
    ) -> str:
        """同步生成内容"""
        pass
    
    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        context: list[dict] | None = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式生成内容"""
        pass
    
    @abstractmethod
    async def chat(
        self,
        messages: list[dict],
        **kwargs
    ) -> dict:
        """多轮对话"""
        pass

class OpenAIProvider(BaseAIProvider):
    """OpenAI 兼容提供商 (支持 GPT/Claude/Grok)"""
    pass

class QWenBotProvider(BaseAIProvider):
    """QWen Bot 提供商 (基于 Selenium)"""
    pass
```

#### QWen Bot 集成方案

```python
# backend/services/ai/qwen_provider.py (概念代码)
import asyncio
from typing import AsyncGenerator
from ..base import BaseAIProvider
# 将从 qwen_bot/main.py 导入并适配

class QWenBotProvider(BaseAIProvider):
    """
    QWen AI 提供商实现
    
    集成策略:
    1. 将 QWenChatBot 封装为异步操作
    2. 使用浏览器池管理多个会话
    3. 实现 LangChain LLM 接口兼容
    4. 添加超时和重试机制
    """
    
    def __init__(self, config: dict):
        self.config = config
        self._bot_instance = None
        self._session_pool = {}
    
    async def _get_or_create_bot(self, session_id: str = None):
        """获取或创建 bot 实例（带连接池）"""
        if session_id and session_id in self._session_pool:
            return self._session_pool[session_id]
        
        # 在线程池中运行同步的 Selenium 代码
        loop = asyncio.get_event_loop()
        bot = await loop.run_in_executor(None, lambda: QWenChatBot(headless=True))
        
        if session_id:
            self._session_pool[session_id] = bot
        
        return bot
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """使用 QWen 生成内容"""
        bot = await self._get_or_create_bot(kwargs.get('session_id'))
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: bot.query(prompt, web_search=kwargs.get('web_search', False))
        )
        
        return result['response']
    
    async def generate_stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """
        流式生成（模拟：QWen Bot 不原生支持流式，
        我们可以轮询或返回完整结果）
        """
        result = await self.generate(prompt, **kwargs)
        yield result
    
    async def cleanup_session(self, session_id: str):
        """清理指定会话资源"""
        if session_id in self._session_pool:
            bot = self._session_pool.pop(session_id)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, bot.close)
```

#### AI Prompt 模板系统

```python
# backend/prompts/templates.py (概念代码)
PROMPT_TEMPLATES = {
    "outline_generation": {
        "name": "大纲生成",
        "description": "根据设定生成小说章节大纲",
        "template_path": "prompts/outline.txt",
        "variables": ["genre", "theme", "character_count", "target_chapters"]
    },
    "chapter_writing": {
        "name": "章节撰写",
        "description": "根据大纲撰写具体章节",
        "template_path": "prompts/chapter.txt",
        "variables": [
            "previous_context",
            "chapter_outline",
            "characters_present",
            "writing_style",
            "word_count_target"
        ]
    },
    "dialogue_generation": {
        "name": "对话生成",
        "description": "生成角色对话场景",
        "template_path": "prompts/dialogue.txt",
        "variables": ["characters", "scene", "emotion", "plot_point"]
    },
    "description_enhancement": {
        "name": "描写增强",
        "description": "增强场景或动作描写",
        "template_path": "prompts/description.txt",
        "variables": ["basic_description", "style", "sensory_details"]
    },
    "consistency_check": {
        "name": "一致性检查",
        "description": "检查内容一致性问题",
        "template_path": "prompts/consistency.txt",
        "variables": ["content", "character_db", "timeline", "previous_events"]
    }
}
```

### NAF-ITEM-1.6 [项目目录结构规划]

```
novelai-forge/
├── README.md
├── docker-compose.yml
├── .env.example
├── .gitignore
│
├── frontend/                          # Next.js 15 前端
│   ├── package.json
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── public/
│   │   └── favicon.ico
│   ├── src/
│   │   ├── app/                      # App Router 页面
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx              # 首页
│   │   │   ├── login/
│   │   │   ├── register/
│   │   │   ├── dashboard/
│   │   │   ├── project/
│   │   │   │   ├── [id]/
│   │   │   │   ├── page.tsx
│   │   │   │   ├── editor/
│   │   │   │   ├── settings/
│   │   │   │   ├── characters/
│   │   │   │   └── export/
│   │   │   └── profile/
│   │   ├── components/               # UI 组件
│   │   │   ├── ui/                   # shadcn/ui 基础组件
│   │   │   ├── editor/               # 编辑器相关组件
│   │   │   │   ├── RichTextEditor.tsx
│   │   │   │   ├── AISidebar.tsx
│   │   │   │   └── Toolbar.tsx
│   │   │   ├── project/              # 项目组件
│   │   │   │   ├── ProjectCard.tsx
│   │   │   │   ├── SettingsWizard.tsx
│   │   │   │   └── CharacterForm.tsx
│   │   │   └── ai/                   # AI 相关组件
│   │   │       ├── AIPanel.tsx
│   │   │       ├── ModelSelector.tsx
│   │   │       └── GenerationResult.tsx
│   │   ├── lib/                      # 工具库
│   │   │   ├── api.ts                # API 客户端
│   │   │   ├── auth.ts               # 认证工具
│   │   │   └── utils.ts
│   │   ├── hooks/                    # 自定义 Hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── useProject.ts
│   │   │   └── useAI.ts
│   │   ├── store/                    # 状态管理
│   │   │   └── index.ts
│   │   └── types/                    # TypeScript 类型定义
│   │       └── index.ts
│   └── components.json               # shadcn/ui 配置
│
├── backend/                          # FastAPI 后端
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── .env.example
│   ├── main.py                       # FastAPI 应用入口
│   ├── config.py                     # 配置管理
│   ├── alembic/                      # 数据库迁移
│   │   ├── env.py
│   │   └── versions/
│   ├── app/                          # 应用主包
│   │   ├── __init__.py
│   │   ├── main.py                   # 路由注册
│   │   ├── models/                   # SQLAlchemy 模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── novel.py
│   │   │   ├── chapter.py
│   │   │   ├── character.py
│   │   │   └── ai_session.py
│   │   ├── schemas/                  # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── novel.py
│   │   │   └── ai.py
│   │   ├── api/                      # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── projects.py
│   │   │   ├── chapters.py
│   │   │   ├── characters.py
│   │   │   ├── ai.py
│   │   │   └── export.py
│   │   ├── services/                 # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── project_service.py
│   │   │   ├── ai/                   # AI 服务模块
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py           # AI Provider 基类
│   │   │   │   ├── openai_provider.py
│   │   │   │   ├── qwen_provider.py  # QWen Bot 集成
│   │   │   │   ├── factory.py        # Provider 工厂
│   │   │   │   └── prompt_manager.py # 提示词管理
│   │   │   └── consistency_service.py
│   │   ├── core/                     # 核心工具
│   │   │   ├── __init__.py
│   │   │   ├── security.py           # JWT/密码哈希
│   │   │   ├── database.py           # DB 连接
│   │   │   └── dependencies.py       # FastAPI 依赖注入
│   │   └── utils/                    # 工具函数
│   │       └── __init__.py
│   ├── prompts/                      # AI 提示词模板 ⭐
│   │   ├── README.md                 # 提示词编写指南
│   │   ├── outline.txt               # 大纲生成模板
│   │   ├── chapter.txt               # 章节撰写模板
│   │   ├── dialogue.txt              # 对话生成模板
│   │   ├── description.txt           # 描写增强模板
│   │   ├── consistency.txt           # 一致性检查模板
│   │   └── custom/                   # 用户自定义提示词
│   │       └── .gitkeep
│   └── tests/                        # 测试
│       ├── __init__.py
│       ├── test_auth.py
│       ├── test_projects.py
│       └── test_ai.py
│
└── docs/                             # 文档（可选）
    └── api.md
```

### NAF-ITEM-1.7 [Docker Compose 配置]

```yaml
# docker-compose.yml (开发环境)
version: '3.8'

services:
  # PostgreSQL 数据库 (生产环境)
  postgres:
    image: postgres:16-alpine
    container_name: novelai-forge-db
    environment:
      POSTGRES_USER: ${DB_USER:-forge}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-forge123}
      POSTGRES_DB: ${DB_NAME:-novelai_forge}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-forge}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis (缓存 & 任务队列)
  redis:
    image: redis:7-alpine
    container_name: novelai-forge-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    container_name: novelai-forge-backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./backend:/app
      - ./backend/prompts:/app/prompts
    environment:
      DATABASE_URL: postgresql://${DB_USER:-forge}:${DB_PASSWORD:-forge}@postgres:5432/${DB_NAME:-novelai_forge}
      REDIS_URL: redis://redis:6379/0
      JWT_SECRET_KEY: ${JWT_SECRET_KEY:-your-super-secret-key}
      OPENAI_API_KEY: ${OPENAI_API_KEY:-}
      GROK_API_KEY: ${GROK_API_KEY:-}
      CLAUDE_API_KEY: ${CLAUDE_API_KEY:-}
      QWEN_EMAIL: ${QWEN_EMAIL:-}
      QWEN_PASSWORD: ${QWEN_PASSWORD:-}
      # 开发模式使用 SQLite
      USE_SQLITE: "true"
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    # 如果使用 QWen Bot，需要 Chrome 环境
    # 对于本地开发，建议直接运行而不使用 Docker

  # Frontend (Next.js)
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    container_name: novelai-forge-frontend
    command: npm run dev
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000/api/v1
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
  redis_data:

networks:
  default:
    name: novelai-forge-network
```

---

## Proposed Code & Files

### File: `docker-compose.yml` (根目录)

见上方 NAF-ITEM-1.7

### File: `backend/.env.example`

```bash
# Database Configuration
DATABASE_URL=sqlite:///./dev.db
# 生产环境: DATABASE_URL=postgresql://user:pass@localhost:5432/novelai_forge
USE_SQLITE=true

# JWT Authentication
JWT_SECRET_KEY=change-this-to-a-random-secret-key-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Providers - OpenAI Compatible
OPENAI_API_KEY=sk-your-openai-key
OPENAI_BASE_URL=https://api.openai.com/v1

# Grok (xAI)
GROK_API_KEY=xai-your-grok-key
GROK_BASE_URL=https://api.x.ai/v1

# Claude (Anthropic)
CLAUDE_API_KEY=sk-ant-your-claude-key

# QWen Bot (Selenium-based)
QWEN_EMAIL=your-qwen-email@example.com
QWEN_PASSWORD=your-qwen-password
QWEN_HEADLESS=true

# Redis (可选，用于缓存)
REDIS_URL=redis://localhost:6379/0

# Application
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
```

### File: `backend/prompts/README.md` (提示词模板指南)

```markdown
# AI Prompt Templates Guide

This folder contains prompt templates for the NovelAI Forge AI generation system.

## Template Structure

Each template file follows this convention:
- `{purpose}.txt` - Main template file
- Variables are marked as `{{VARIABLE_NAME}}`
- System prompts vs user prompts are separated by comments

## Available Templates

### 1. `outline.txt` - Novel Outline Generation
**Purpose**: Generate chapter outlines based on novel settings.
**Variables**:
- `{{GENRE}}` - Novel genre (fantasy, sci-fi, romance, etc.)
- `{{THEME}}` - Central theme or message
- `{{CHARACTER_COUNT}}` - Number of main characters
- `{{TARGET_CHAPTERS}}` - Estimated number of chapters
- `{{WRITING_STYLE}}` - Desired narrative style

### 2. `chapter.txt` - Chapter Writing
**Purpose**: Write a complete chapter based on outline.
**Variables**:
- `{{PREVIOUS_CONTEXT}}` - Summary of previous chapters
- `{{CHAPTER_OUTLINE}}` - Current chapter's outline points
- `{{CHARACTERS_PRESENT}}` - List of characters in this scene
- `{{WRITING_STYLE}}` - Style guidelines
- `{{WORD_COUNT_TARGET}}` - Target word count (e.g., "2000-3000 words")

### 3. `dialogue.txt` - Dialogue Generation
**Purpose**: Generate natural character dialogue for scenes.
**Variables**:
- `{{CHARACTERS}}` - Character profiles with speech patterns
- `{{SCENE}}` - Scene description and setting
- `{{EMOTION}}` - Emotional tone required
- `{{PLOT_POINT}}` - What information must be conveyed through dialogue

### 4. `description.txt` - Description Enhancement
**Purpose**: Enhance basic descriptions with sensory details.
**Variables**:
- `{{BASIC_DESCRIPTION}}` - The original simple description
- `{{STYLE}}` - Poetic, realistic, minimalist, etc.
- `{{SENSORY_DETAILS}}` - Which senses to emphasize (sight, sound, smell, etc.)

### 5. `consistency.txt` - Consistency Checking
**Purpose**: Check content for logical inconsistencies.
**Variables**:
- `{{CONTENT}}` - The text to check
- `{{CHARACTER_DB}}` - Known character traits and history
- `{{TIMELINE}}` - Established timeline of events
- `{{PREVIOUS_EVENTS}}` - Summary of what has happened before

## Custom Prompts

Users can create custom prompts in the `custom/` directory.
Custom prompts should follow the same variable naming convention.

## Best Practices

1. Be specific about desired output format
2. Include examples when possible (few-shot prompting)
3. Specify constraints (word count, style restrictions)
4. Use clear section markers in templates
5. Test templates with multiple AI providers for compatibility

## Integration Notes

- These templates are loaded by `backend/services/ai/prompt_manager.py`
- The QWen Bot provider may require slightly adjusted prompts due to model differences
- Always validate template variables before sending to AI providers
```

### File: `backend/prompts/outline.txt` (示例模板 - 占位符)

```
[System Prompt]
你是一位专业的小说策划师。请根据以下设定为一部{{GENRE}}类型小说创建详细的章节大纲。

[Context]
小说主题: {{THEME}}
主要角色数量: {{CHARACTER_COUNT}}个
预计章节数: {{TARGET_CHAPTERS}}章
写作风格: {{WRITING_STYLE}}

[Instructions]
1. 为每个章节提供:
   - 章节标题
   - 主要情节点 (3-5个关键事件)
   - 涉及的主要角色
   - 情感基调
   - 与主线剧情的关系

2. 确保情节发展符合以下原则:
   - 节奏合理，张弛有度
   - 冲突逐步升级
   - 角色成长弧线清晰
   - 伏笔与呼应

3. 输出格式要求:
   使用Markdown格式，每个章节用 ## 标题标记。

[User Input]
请开始创建这部小说的大纲。
```

### File: `backend/prompts/chapter.txt` (示例模板 - 占位符)

```
[System Prompt]
你是一位经验丰富的{{GENRE}}小说作家。请根据提供的大纲和上下文撰写一个完整的章节。

[Context]
前文摘要: {{PREVIOUS_CONTEXT}}

本章大纲: {{CHAPTER_OUTLINE}}

出场角色:
{{CHARACTERS_PRESENT}}

写作风格要求: {{WRITING_STYLE}}

目标字数: {{WORD_COUNT_TARGET}}

[Instructions]
1. 写作质量标准:
   - 人物对话自然生动
   - 场景描写细腻有画面感
   - 情节推进流畅
   - 保持与前文的连贯性

2. 注意事项:
   - 维持已建立的角色性格特征
   - 不要引入未设定的新角色（除非大纲明确要求）
   - 保持时间线的一致性
   - 适当使用伏笔

3. 输出格式:
   - 直接输出正文内容
   - 使用Markdown格式（如需要可使用**加粗**表示强调）
   - 不需要输出章节标题（系统会自动添加）

[User Input]
请根据以上信息撰写本章内容。
```

### File: `backend/Dockerfile.dev`

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖 (Chrome for QWen Bot)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# 设置 Chromium 环境变量
ENV CHROMIUM_PATH=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### File: `frontend/.env.example.local`

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Authentication
NEXT_PUBLIC_AUTH_TOKEN_KEY=novelai_forge_token

# Feature Flags
NEXT_PUBLIC_ENABLE_QWEN_BOT=true
NEXT_PUBLIC_ENABLE_STREAMING=true

# Editor Configuration
NEXT_PUBLIC_EDITOR_DEFAULT_FONT=Inter
NEXT_PUBLIC_EDITOR_FONT_SIZE=16
```

### File: `backend/requirements.txt`

```txt
# Web Framework
fastapi==0.115.0
uvicorn[standard]==0.30.6
python-multipart==0.0.12

# Database
sqlalchemy==2.0.35
alembic==1.13.3
asyncpg==0.29.0
aiosqlite==0.20.0

# Authentication
pyjwt==2.9.0
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0

# AI / LLM
langchain==0.3.7
langchain-openai==0.2.8
openai==1.51.2
httpx==0.27.2
# QWen Bot Dependencies
selenium==4.25.0
webdriver-manager==4.0.2
python-dotenv==1.0.1

# Data Validation
pydantic==2.9.2
pydantic-settings==2.6.1
email-validator==2.2.0

# Utilities
python-dateutil==2.9.0.post0
orjson==3.10.7
redis==5.1.1

# Development
pytest==8.3.3
pytest-asyncio==0.24.0
httpx==0.27.2  # For TestClient
```

---

## Commands

### 初始化项目命令清单

```bash
# 1. 创建根目录和基本结构
mkdir novelai-forge && cd novelai-forge

# 2. 初始化 Git
git init
touch README.md .gitignore

# 3. 创建后端目录结构
mkdir -p backend/{app/{models,schemas,api,services/ai,core,utils},prompts/custom,tests,alembic/versions}

# 4. 创建前端目录结构
mkdir -p frontend/src/{app/{project/\[id\]},components/{ui,editor,project,ai},lib,hooks,store,types}

# 5. 初始化后端 Python 环境
cd backend
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate
pip install fastapi uvicorn sqlalchemy alembic pyjwt passlib langchain openai selenium webdriver-manager python-dotenv

# 6. 初始化前端 Node.js 环境
cd ../frontend
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
npm install @tanstack/react-query axios zustand @tiptap/react @tiptap/starter-kit lucide-react

# 7. 安装 shadcn/ui
npx shadcn@latest init
npx shadcn@latest add button card dialog input textarea select tabs

# 8. 复制配置文件到相应位置
cp ../TODO_novelai-forge.md .  # 参考文档
# 手动创建上述 Proposed Code & Files 中的所有文件

# 9. 启动开发环境 (Docker Compose)
cd ..
docker-compose up -d --build

# 或分别启动（推荐用于调试 QWen Bot）:
# Terminal 1: Backend
cd backend && uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev

# 10. 初始化数据库迁移
cd backend
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

# 11. 测试 QWen Bot 集成（需要 Chrome 和 QWen 账号）
# 设置环境变量后运行测试
export QWEN_EMAIL="your-email@example.com"
export QWEN_PASSWORD="your-password"
python -m pytest tests/test_ai.py::test_qwen_provider -v
```

---

## Quality Assurance Task Checklist

### 必须完成的质量检查项

- [ ] **QA-1.1 [Monorepo 结构完整性]**
  - [ ] 根目录包含 `README.md`, `.gitignore`, `docker-compose.yml`, `TODO_novelai-forge.md`
  - [ ] `frontend/` 目录存在且包含 Next.js 15 项目骨架
  - [ ] `backend/` 目录存在且包含 FastAPI 项目骨架
  - [ ] 所有子目录按 NAF-ITEM-1.6 规划创建

- [ ] **QA-1.2 [Backend 提示词模板]**
  - [ ] `backend/prompts/` 目录存在
  - [ ] `backend/prompts/README.md` 存在且包含详细的使用指南
  - [ ] `backend/prompts/outline.txt` 模板文件存在（占位符）
  - [ ] `backend/prompts/chapter.txt` 模板文件存在（占位符）
  - [ ] `backend/prompts/dialogue.txt` 模板文件存在（占位符）
  - [ ] `backend/prompts/description.txt` 模板文件存在（占位符）
  - [ ] `backend/prompts/consistency.txt` 模板文件存在（占位符）
  - [ ] `backend/prompts/custom/` 目录存在（用于用户自定义提示词）

- [ ] **QA-1.3 [Docker Compose 配置]**
  - [ ] `docker-compose.yml` 文件语法正确
  - [ ] 包含 PostgreSQL 服务定义
  - [ ] 包含 Redis 服务定义（可选）
  - [ ] 包含 Backend 服务定义，正确挂载 `prompts` 卷
  - [ ] 包含 Frontend 服务定义
  - [ ] 服务间依赖关系正确配置
  - [ ] 环境变量通过 `.env` 文件或默认值配置

- [ ] **QA-1.4 [QWen Bot 集成准备]**
  - [ ] `backend/app/services/ai/qwen_provider.py` 文件存在（框架代码）
  - [ ] `backend/requirements.txt` 包含 selenium 和 webdriver-manager
  - [ ] `backend/Dockerfile.dev` 包含 Chrome/Chromium 安装步骤
  - [ ] `backend/.env.example` 包含 QWEN_EMAIL 和 QWEN_PASSWORD 变量
  - [ ] QWen Bot 的原始代码位于 `../qwen_bot/` 且可被引用

- [ ] **QA-1.5 [配置文件完整性]**
  - [ ] `backend/.env.example` 包含所有必要的环境变量
  - [ ] `frontend/.env.example.local` 包含前端必要变量
  - [ ] `backend/requirements.txt` 包含所有依赖
  - [ ] `frontend/package.json` 包含必要的依赖脚本

- [ ] **QA-1.6 [文档完整性]**
  - [ ] 本文件 (`TODO_novelai-forge.md`) 包含所有必需部分:
    - [ ] Context 部分
    - [ ] Architecture Plan (至少 2 个 plan items)
    - [ ] Task Items (至少 7 个 task items)
    - [ ] Proposed Code & Files (至少 8 个文件块)
    - [ ] Commands 部分
    - [ ] Quality Assurance Checklist (本部分)

---

## Appendix: QWen Bot 集成注意事项

### 技术限制与解决方案

| 问题 | 解决方案 |
|------|----------|
| Selenium 是同步阻塞的 | 使用 `run_in_executor()` 在异步环境中运行 |
| QWen 不支持真正的流式输出 | 实现伪流式：先收集完整响应，再分块发送 |
| 浏览器实例资源消耗大 | 实现连接池，限制并发数，设置空闲超时 |
| 可能遇到验证码 | 使用真实账号凭证，避免频繁请求，实现重试逻辑 |
| Cookie 过期 | 定期刷新 cookies，检测 401 错误自动重新登录 |

### 性能优化建议

1. **浏览器复用**: 维护一个浏览器实例池，按 session_id 分配
2. **预热机制**: 在系统启动时预登录一个浏览器实例
3. **降级策略**: 当 QWen 不可用时，自动切换到其他 AI Provider
4. **缓存响应**: 对相同或相似的查询结果进行短期缓存
5. **监控告警**: 监控 QWen Bot 的响应时间和错误率

### 安全考虑

- QWen 凭证存储在环境变量中，不硬编码在代码里
- 限制 QWen Bot 的访问权限，仅允许内部服务调用
- 记录所有 QWen API 调用的审计日志
- 定期轮换 QWen 账号密码

---

## 下一步行动

完成本文档后，执行以下步骤：

1. ✅ **阅读并理解本文档** (当前步骤)
2. 🔄 **创建实际的项目文件结构** (执行 Commands 部分的命令)
3. ⏳ **填充骨架代码** (创建空的 Python/TypeScript 文件)
4. ⏳ **实现核心功能** (Auth → Projects → AI Generation)
5. ⏳ **集成 QWen Bot** (完善 `qwen_provider.py`)
6. ⏳ **编写单元测试和集成测试**
7. ⏳ **用户验收测试**

---

**文档版本**: 1.0  
**最后更新**: 2026-04-13  
**作者**: AI Architect Assistant  
**状态**: 待审核
