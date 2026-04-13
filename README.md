# NovelAI Forge

> 🎨 AI-powered novel writing platform with FastAPI backend and Next.js frontend
> 🎨 基于 AI 驱动的小说写作平台，具有 FastAPI 后端和 Next.js 前端

## 🌐 Language / 语言

<details>
<summary>English</summary>

## 📖 Overview

NovelAI Forge is a comprehensive AI-powered novel writing platform designed to assist authors throughout the creative process. It combines a powerful Python backend with a modern frontend to provide a seamless writing experience enhanced by AI capabilities.

### 🌟 Key Features

- **AI-Powered Content Generation**: Generate outlines, chapters, continuations, dialogue, and polish text using OpenAI/GPT, Grok, or Claude
- **Real-time Streaming**: SSE (Server-Sent Events) for real-time AI output display
- **Rich Text Editor**: Modern writing interface with AI sidebar
- **Novel Project Management**: Create and manage multiple novel projects with chapters and characters
- **Character Database**: Build and reference character profiles with personality, appearance, and background
- **Consistency Checker**: AI-powered consistency validation for plot, characters, and timeline
- **Multi-format Export**: Export to Markdown, TXT, and other formats
- **Secure Authentication**: JWT-based user authentication
- **Extensible Architecture**: Modular design with pluggable AI providers

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.115+ (async)
- **Database**: SQLite (development) / PostgreSQL (production)
- **ORM**: SQLAlchemy 2.0+ (async)
- **AI Integration**: LangChain + OpenAI SDK
- **Authentication**: JWT + bcrypt
- **Validation**: Pydantic v2
- **Containerization**: Docker + Docker Compose

### Frontend (Planned)
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript 5.x
- **Styling**: Tailwind CSS + shadcn/ui
- **State Management**: Zustand
- **Editor**: Tiptap (Rich Text)

## 📁 Project Structure

```
NovelAI-Forge/
├── backend/                  # Python Backend
│   ├── app/                  # FastAPI Application
│   │   ├── core/             # Core infrastructure
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── schemas/          # Pydantic validation models
│   │   ├── repositories/     # Data access layer
│   │   ├── services/         # Business logic layer
│   │   └── routers/          # API routes
│   ├── prompts/              # AI prompt templates
│   ├── tests/                # Test suite
│   ├── scripts/              # Utility scripts
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile            # Container configuration
│
├── frontend/                 # Next.js Frontend (Planned)
│   ├── app/                  # App Router pages
│   ├── components/           # UI components
│   └── public/               # Static assets
│
├── docs/                     # Documentation
│   ├── development/          # Development guides
│   └── maintenance/          # Maintenance guides
│
├── docker-compose.yml        # Docker orchestration
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- pip
- Docker (optional, for containerized deployment)
- OpenAI API Key (for AI generation)

### Installation

#### 1. Clone the repository

```bash
git clone https://github.com/yourusername/novelai-forge.git
cd novelai-forge
```

#### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env file to add your OpenAI API key
```

#### 3. Database Initialization

```bash
# For development (SQLite)
# Tables will be created automatically on first run

# For production (PostgreSQL)
# Set DATABASE_URL in .env to your PostgreSQL connection string
```

#### 4. Start the Backend

```bash
# Development mode (with hot reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### 5. Access the API Documentation

Open your browser and navigate to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Docker Deployment

```bash
# Build and start services
docker-compose up --build -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

## 📝 AI Prompt Templates

The platform uses customizable prompt templates stored in `backend/prompts/`. These templates contain placeholders that are dynamically replaced with project-specific information.

### Available Templates:
- `outline_prompt.txt` - Novel outline generation
- `chapter_prompt.txt` - Chapter writing
- `continuation_prompt.txt` - Story continuation
- `polish_prompt.txt` - Text polishing
- `consistency_prompt.txt` - Consistency checking
- `dialogue_prompt.txt` - Dialogue generation

### Customization

Edit the template files to customize the AI behavior. Use `[CUSTOM_SYSTEM_PROMPT_HERE]` as a placeholder for your custom system instructions.

## 🔧 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/auth/me` - Get current user info

### Projects
- `GET /api/v1/projects` - List projects
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects/{id}` - Get project details
- `GET /api/v1/projects/{id}/chapters` - List chapters
- `POST /api/v1/projects/{id}/chapters` - Create chapter
- `GET /api/v1/projects/{id}/characters` - List characters
- `POST /api/v1/projects/{id}/characters` - Create character

### AI Generation (⭐ Core Features)
- `POST /api/v1/ai/generate/stream` - Stream AI content generation
- `GET /api/v1/ai/models` - List available AI models
- `GET /api/v1/ai/templates` - List prompt templates
- `POST /api/v1/ai/consistency-check` - Run consistency check

## 🎯 Usage Examples

### Generating a Chapter

```javascript
// Frontend example using fetch API
const response = await fetch('/api/v1/ai/generate/stream', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  },
  body: JSON.stringify({
    task_type: 'chapter',
    project_id: 1,
    chapter_id: 5,
    model: 'gpt-4o',
  }),
});

// Stream the response
const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const text = decoder.decode(value);
  const lines = text.split('\n').filter(line => line.startsWith('data: '));
  
  for (const line of lines) {
    const data = JSON.parse(line.slice(6));
    if (data.is_final) break;
    
    // Display AI output in real-time
    appendToEditor(data.content);
  }
}
```

## 📚 Documentation

- **Architecture**: `docs/development/ARCHITECTURE.md`
- **API Reference**: `docs/development/API.md`
- **Database Schema**: `docs/development/DATABASE.md`
- **AI Prompt Guide**: `docs/development/AI-PROMPTS.md`
- **Setup Guide**: `docs/development/SETUP.md`
- **Coding Standards**: `docs/development/CODING-STANDARDS.md`
- **Maintenance Guide**: `docs/maintenance/MAINTENANCE.md`
- **Troubleshooting**: `docs/maintenance/TROUBLESHOOTING.md`

## 🔒 Security

- JWT token authentication
- bcrypt password hashing
- CORS configuration
- Input validation with Pydantic
- Rate limiting (planned)

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your code follows the project's coding standards and includes tests when appropriate.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Bug Reports**: Open an issue on GitHub
- **Feature Requests**: Open an issue with the "enhancement" label
- **Questions**: Use the GitHub Discussions tab

## 📢 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast (high-performance) web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - SQL toolkit and ORM
- [Pydantic](https://pydantic.dev/) - Data validation
- [OpenAI](https://openai.com/) - AI models
- [LangChain](https://www.langchain.com/) - AI orchestration framework
- [Next.js](https://nextjs.org/) - React framework (planned)
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework (planned)

---

**END** ✍️✨

*Project for experimental ideas. Feel free to improve.❤️*

</details>

<details>
<summary>中文</summary>

## 📖 项目概述

NovelAI Forge 是一个全面的 AI 驱动小说写作平台，旨在帮助作者完成整个创作过程。它结合了强大的 Python 后端和现代前端，提供了由 AI 能力增强的无缝写作体验。

### 🌟 核心功能

- **AI 内容生成**：使用 OpenAI/GPT、Grok 或 Claude 生成大纲、章节、续写、对话和润色文本
- **实时流式输出**：使用 SSE（Server-Sent Events）实时显示 AI 输出
- **富文本编辑器**：带 AI 侧边栏的现代写作界面
- **小说项目管理**：创建和管理多个小说项目，包含章节和角色
- **角色数据库**：构建和引用包含性格、外貌和背景的角色档案
- **一致性检查器**：AI 驱动的情节、角色和时间线一致性验证
- **多格式导出**：导出为 Markdown、TXT 和其他格式
- **安全认证**：基于 JWT 的用户认证
- **可扩展架构**：具有可插拔 AI 提供商的模块化设计

## 🛠️ 技术栈

### 后端
- **框架**：FastAPI 0.115+（异步）
- **数据库**：SQLite（开发）/ PostgreSQL（生产）
- **ORM**：SQLAlchemy 2.0+（异步）
- **AI 集成**：LangChain + OpenAI SDK
- **认证**：JWT + bcrypt
- **验证**：Pydantic v2
- **容器化**：Docker + Docker Compose

### 前端（计划中）
- **框架**：Next.js 15（App Router）
- **语言**：TypeScript 5.x
- **样式**：Tailwind CSS + shadcn/ui
- **状态管理**：Zustand
- **编辑器**：Tiptap（富文本）

## 📁 项目结构

```
NovelAI-Forge/
├── backend/                  # Python 后端
│   ├── app/                  # FastAPI 应用
│   │   ├── core/             # 核心基础设施
│   │   ├── models/           # SQLAlchemy ORM 模型
│   │   ├── schemas/          # Pydantic 验证模型
│   │   ├── repositories/     # 数据访问层
│   │   ├── services/         # 业务逻辑层
│   │   └── routers/          # API 路由
│   ├── prompts/              # AI 提示词模板
│   ├── tests/                # 测试套件
│   ├── scripts/              # 工具脚本
│   ├── requirements.txt      # Python 依赖
│   └── Dockerfile            # 容器配置
│
├── frontend/                 # Next.js 前端（计划中）
│   ├── app/                  # App Router 页面
│   ├── components/           # UI 组件
│   └── public/               # 静态资源
│
├── docs/                     # 文档
│   ├── development/          # 开发指南
│   └── maintenance/          # 维护指南
│
├── docker-compose.yml        # Docker 编排
├── .env.example              # 环境变量模板
└── README.md                 # 本文档
```

## 🚀 快速开始

### 前提条件

- Python 3.12+
- pip
- Docker（可选，用于容器化部署）
- OpenAI API Key（用于 AI 生成）

### 安装

#### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/novelai-forge.git
cd novelai-forge
```

#### 2. 后端设置

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
cd backend
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件添加你的 OpenAI API 密钥
```

#### 3. 数据库初始化

```bash
# 开发环境（SQLite）
# 表会在首次运行时自动创建

# 生产环境（PostgreSQL）
# 在 .env 中设置 DATABASE_URL 为你的 PostgreSQL 连接字符串
```

#### 4. 启动后端

```bash
# 开发模式（热重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### 5. 访问 API 文档

打开浏览器并导航到：
- **Swagger UI**：http://localhost:8000/docs
- **ReDoc**：http://localhost:8000/redoc

### Docker 部署

```bash
# 构建并启动服务
docker-compose up --build -d

# 查看日志
docker-compose logs -f backend

# 停止服务
docker-compose down
```

## 📝 AI 提示词模板

平台使用存储在 `backend/prompts/` 中的可自定义提示词模板。这些模板包含占位符，会根据项目特定信息动态替换。

### 可用模板：
- `outline_prompt.txt` - 小说大纲生成
- `chapter_prompt.txt` - 章节写作
- `continuation_prompt.txt` - 故事续写
- `polish_prompt.txt` - 文本润色
- `consistency_prompt.txt` - 一致性检查
- `dialogue_prompt.txt` - 对话生成

### 自定义

编辑模板文件来自定义 AI 行为。使用 `[CUSTOM_SYSTEM_PROMPT_HERE]` 作为自定义系统指令的占位符。

## 🔧 API 端点

### 认证
- `POST /api/v1/auth/register` - 注册新用户
- `POST /api/v1/auth/login` - 登录并获取 JWT 令牌
- `GET /api/v1/auth/me` - 获取当前用户信息

### 项目
- `GET /api/v1/projects` - 列出项目
- `POST /api/v1/projects` - 创建项目
- `GET /api/v1/projects/{id}` - 获取项目详情
- `GET /api/v1/projects/{id}/chapters` - 列出章节
- `POST /api/v1/projects/{id}/chapters` - 创建章节
- `GET /api/v1/projects/{id}/characters` - 列出角色
- `POST /api/v1/projects/{id}/characters` - 创建角色

### AI 生成（⭐ 核心功能）
- `POST /api/v1/ai/generate/stream` - 流式 AI 内容生成
- `GET /api/v1/ai/models` - 列出可用 AI 模型
- `GET /api/v1/ai/templates` - 列出提示词模板
- `POST /api/v1/ai/consistency-check` - 运行一致性检查

## 🎯 使用示例

### 生成章节

```javascript
// 前端使用 fetch API 的示例
const response = await fetch('/api/v1/ai/generate/stream', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  },
  body: JSON.stringify({
    task_type: 'chapter',
    project_id: 1,
    chapter_id: 5,
    model: 'gpt-4o',
  }),
});

// 流式处理响应
const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const text = decoder.decode(value);
  const lines = text.split('\n').filter(line => line.startsWith('data: '));
  
  for (const line of lines) {
    const data = JSON.parse(line.slice(6));
    if (data.is_final) break;
    
    // 实时显示 AI 输出
    appendToEditor(data.content);
  }
}
```

## 📚 文档

- **架构**：`docs/development/ARCHITECTURE.md`
- **API 参考**：`docs/development/API.md`
- **数据库 Schema**：`docs/development/DATABASE.md`
- **AI 提示词指南**：`docs/development/AI-PROMPTS.md`
- **设置指南**：`docs/development/SETUP.md`
- **编码标准**：`docs/development/CODING-STANDARDS.md`
- **维护指南**：`docs/maintenance/MAINTENANCE.md`
- **故障排除**：`docs/maintenance/TROUBLESHOOTING.md`

## 🔒 安全

- JWT 令牌认证
- bcrypt 密码哈希
- CORS 配置
- Pydantic 输入验证
- 速率限制（计划中）

## 🤝 贡献

欢迎贡献！请遵循以下步骤：

1. Fork 仓库
2. 创建功能分支（`git checkout -b feature/amazing-feature`）
3. 提交更改（`git commit -m 'Add amazing feature'`）
4. 推送到分支（`git push origin feature/amazing-feature`）
5. 打开 Pull Request

请确保你的代码遵循项目的编码标准，并在适当的情况下包含测试。

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 📞 支持

- **Bug 报告**：在 GitHub 上打开 issue
- **功能请求**：使用 "enhancement" 标签打开 issue
- **问题咨询**：使用 GitHub Discussions 标签

## 📢 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代、快速（高性能）的 Web 框架
- [SQLAlchemy](https://www.sqlalchemy.org/) - SQL 工具包和 ORM
- [Pydantic](https://pydantic.dev/) - 数据验证
- [OpenAI](https://openai.com/) - AI 模型
- [LangChain](https://www.langchain.com/) - AI 编排框架
- [Next.js](https://nextjs.org/) - React 框架（计划中）
- [Tailwind CSS](https://tailwindcss.com/) - 实用优先的 CSS 框架（计划中）

---

**最后**

*一个用于实验想法的项目，欢迎完善❤️*

</details>
