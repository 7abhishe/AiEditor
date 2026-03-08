# ⚡ CodeGenie AI Editor

An AI-powered code editor built as a **web application** with **React + Vite + FastAPI + Google Gemini**, featuring intelligent coding assistance, semantic search, and autonomous coding capabilities.

![CodeGenie](https://img.shields.io/badge/Version-0.1.0-blue) ![License](https://img.shields.io/badge/License-MIT-green) ![Python](https://img.shields.io/badge/Python-3.14-yellow) ![React](https://img.shields.io/badge/React-19-61DAFB) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)

**🌐 Live:** [codegenie-web.onrender.com](https://codegenie-web.onrender.com) • **📡 API:** [codegenie-backend-27y2.onrender.com](https://codegenie-backend-27y2.onrender.com)

---

## ✨ Features

### 🤖 AI-Powered Editing
- **Smart Chat** — Ask anything about your code, powered by Google Gemini with RAG context
- **Code Completion** — Inline AI suggestions as you type
- **Code Explanation** — Explain selected code in natural language
- **Bug Detection** — AI identifies potential bugs and suggests fixes
- **Refactoring** — Intelligent code improvement suggestions with diffs
- **Test Generation** — Auto-generate unit tests for your code

### 🔍 Semantic Search
- AI-powered codebase search using FAISS vector embeddings
- Search by meaning, not just text matching
- Results grouped by file with relevance scores

### 🔀 Git Integration
- Built-in source control with Status, Staging, and Commit
- AI-generated commit messages from your diffs

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

### 🔒 Security Hardened
- Penetration tested (86% score, 43 test cases)
- Rate limiting, CORS, security headers, IDOR protection
- JWT authentication with token refresh

---

## 🏗️ Architecture

```
┌────────────────────────────────────────┐
│        Web Browser (React + Vite)      │
│  ┌──────────────┐  ┌────────────────┐  │
│  │ Monaco Editor │  │ Sidebar Panels │  │
│  │              │  │ Chat/Search/Git│  │
│  └──────────────┘  └────────────────┘  │
│          Login / Signup (JWT)          │
└────────────────────┬───────────────────┘
                     │ HTTPS REST + JWT
┌────────────────────┴───────────────────┐
│         FastAPI Backend                │
│  ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │ AI Service│ │ Git Svc  │ │ Agent  │ │
│  │ (Gemini)  │ │          │ │ Service│ │
│  └──────────┘ └──────────┘ └────────┘ │
│  ┌──────────┐ ┌──────────────────────┐ │
│  │ FAISS    │ │ SQLite / PostgreSQL  │ │
│  │ Vectors  │ │ (Render.com)         │ │
│  └──────────┘ └──────────────────────┘ │
└────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+**
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
cp .env.example .env
# Edit .env and add your Gemini API key
```

### 3. Run Backend
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 4. Run Frontend
```bash
cd frontend
npm install
npm run dev          # http://localhost:5173
```

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `⌘K` | Command Palette |
| `⌘B` | Toggle Sidebar |
| `⌘⇧F` | Semantic Search |
| `⌘S` | Save File |

---

## 🐳 Docker

```bash
docker compose up --build
```

---

## 📁 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/v1/          # 13 REST API endpoints
│   │   ├── core/            # Config, auth, security, rate limiting
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   └── services/        # AI, Git, Agent, Indexing services
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # 10 React components
│   │   └── services/        # API client
│   └── package.json
├── .env.example             # Environment template
├── .github/workflows/       # CI/CD pipeline
├── docker-compose.yml
├── architect.md             # Full architecture document
├── API.md                   # API documentation
├── DEPLOYMENT.md            # Deployment guide
├── SECURITY.md              # Security policy
└── CONTRIBUTING.md          # Contributing guide
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19 + Vite 6 |
| Editor | Monaco Editor |
| Backend | FastAPI (Python 3.14) |
| AI | Google Gemini (gemini-3-flash-preview) |
| Vector DB | FAISS |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Auth | JWT (python-jose + passlib) |
| Security | slowapi rate limiting |
| Hosting | Render.com |
| CI/CD | GitHub Actions |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

Built with ⚡ by CodeGenie