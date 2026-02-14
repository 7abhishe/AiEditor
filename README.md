# ⚡ CodeGenie AI Editor

An AI-powered code editor built with **Electron + React + FastAPI + Google Gemini**, featuring intelligent coding assistance, semantic search, and autonomous coding capabilities.

![CodeGenie](https://img.shields.io/badge/Version-0.1.0-blue) ![License](https://img.shields.io/badge/License-MIT-green) ![Python](https://img.shields.io/badge/Python-3.12-yellow) ![React](https://img.shields.io/badge/React-19-61DAFB)

---

## ✨ Features

### 🤖 AI-Powered Editing
- **Smart Chat** — Ask anything about your code, powered by Google Gemini
- **Code Completion** — Inline AI suggestions as you type
- **Code Explanation** — Right-click to explain selected code
- **Bug Detection** — AI identifies potential bugs and suggests fixes
- **Refactoring** — Intelligent code improvement suggestions
- **Test Generation** — Auto-generate unit tests for your code

### 🔍 Semantic Search
- AI-powered codebase search using FAISS vector embeddings
- Search by meaning, not just text matching
- Results grouped by file with relevance scores

### 🔀 Git Integration
- Built-in source control with Changes, History, and Branches tabs
- Stage/unstage files, commit, checkout branches
- AI-generated commit messages

### 🤖 Agentic Mode
- Autonomous Plan → Execute → Verify loop
- Multi-file refactoring across your codebase
- Real-time progress via Server-Sent Events (SSE)

### 🎨 Premium UI
- VS Code-inspired dark theme
- Command Palette (`⌘K`) with fuzzy search
- Resizable sidebar with tabbed panels
- Monaco Editor with bracket colorization, minimap, and more
- Toast notifications and error boundary

---

## 🏗️ Architecture

```
┌────────────────────────────────────────┐
│           Electron Desktop App         │
│  ┌──────────────┐  ┌────────────────┐  │
│  │ Monaco Editor │  │ Sidebar Panels │  │
│  │  (React)      │  │ Chat/Search/Git│  │
│  └──────────────┘  └────────────────┘  │
│           React + Vite Frontend        │
└────────────────────┬───────────────────┘
                     │ HTTP / SSE
┌────────────────────┴───────────────────┐
│         FastAPI Backend                │
│  ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │ AI Service│ │ Git Svc  │ │ Agent  │ │
│  │ (Gemini)  │ │          │ │ Service│ │
│  └──────────┘ └──────────┘ └────────┘ │
│  ┌──────────┐ ┌──────────────────────┐ │
│  │ FAISS    │ │ SQLite / PostgreSQL  │ │
│  │ Vectors  │ │ Database             │ │
│  └──────────┘ └──────────────────────┘ │
└────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.12+**
- **Node.js 20+**
- **Google Gemini API Key** ([Get one here](https://aistudio.google.com/apikey))

### 1. Clone & Setup Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Create .env file in the project root
cp .env.example .env
# Edit .env and add your Gemini API key
```

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash
DATABASE_URL=sqlite+aiosqlite:///./codegenie.db
```

### 3. Run Backend
```bash
uvicorn app.main:app --reload --port 8000
```

### 4. Setup & Run Frontend
```bash
cd frontend
npm install
npm run dev          # Web mode (http://localhost:5173)
npm run electron:dev # Desktop mode (Electron)
```

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `⌘K` | Command Palette |
| `⌘B` | Toggle Sidebar |
| `⌘⇧F` | Semantic Search |
| `⌘S` | Save File |
| `⌘,` | Settings |

---

## 🐳 Docker Deployment

```bash
# Start backend + PostgreSQL + Redis
docker-compose up -d

# Build Electron app
cd frontend && npm run electron:build
```

---

## 📁 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/v1/          # REST API endpoints
│   │   ├── core/            # Config, database
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   └── services/        # AI, Git, Agent services
│   ├── tests/               # pytest test suite
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── electron/            # Main process + preload
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── hooks/           # Custom hooks
│   │   └── services/        # API client
│   └── package.json
├── docker-compose.yml
└── architect.md             # Full architecture doc
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Desktop | Electron 33 |
| Frontend | React 19 + Vite 6 |
| Editor | Monaco Editor |
| Backend | FastAPI (Python 3.12) |
| AI | Google Gemini |
| Vector DB | FAISS |
| Database | SQLite / PostgreSQL |
| Cache | Redis |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

Built with ⚡ by CodeGenie