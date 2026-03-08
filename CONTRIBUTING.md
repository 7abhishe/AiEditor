# 🤝 Contributing to CodeGenie AI Editor

Thank you for your interest in contributing! Here's how to get started.

---

## 🛠️ Development Setup

### Prerequisites
- Python 3.11+ with `pip`
- Node.js 20+ with `npm`
- Git

### 1. Fork & Clone
```bash
git clone https://github.com/your-username/codegenie.git
cd codegenie
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Environment
```bash
cp .env.example .env
# Edit .env with your GEMINI_API_KEY
```

### 5. Run Locally
```bash
# Terminal 1 — Backend
cd backend && source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend && npm run dev
```

---

## 📏 Code Standards

### Backend (Python)
- **Formatter:** `ruff format`
- **Linter:** `ruff check`
- **Type hints:** Required for all function signatures
- **Docstrings:** Required for all public functions
- **Tests:** Required for new endpoints

### Frontend (JavaScript/React)
- **Components:** Functional components with hooks
- **Naming:** PascalCase for components, camelCase for functions
- **Imports:** Group by external → internal → relative

---

## 🌿 Branch Strategy

| Branch | Purpose |
|---|---|
| `main` | Production-ready code |
| `develop` | Integration branch |
| `feature/*` | New features |
| `bugfix/*` | Bug fixes |
| `hotfix/*` | Urgent production fixes |

### Workflow
1. Create a branch from `develop`
2. Make your changes
3. Write/update tests
4. Open a Pull Request to `develop`
5. Get review approval
6. Merge

---

## 📝 Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add token refresh endpoint
fix: resolve CORS origin validation
docs: update API documentation
test: add auth endpoint tests
refactor: extract rate limiting middleware
security: add null byte email validation
```

---

## 🧪 Running Tests

```bash
# Backend
cd backend && source venv/bin/activate
pytest tests/ -v

# Frontend
cd frontend
npm run build  # Verify build succeeds
```

---

## 🔒 Security

- Never commit `.env` or API keys
- Run `ruff check` before pushing
- See [SECURITY.md](SECURITY.md) for the full security policy
- Report vulnerabilities privately (see SECURITY.md)

---

## 📋 Pull Request Checklist

- [ ] Code follows the project style guide
- [ ] Self-reviewed the code
- [ ] Added/updated tests for new features
- [ ] All tests pass locally
- [ ] Updated documentation (if needed)
- [ ] No secrets or API keys in the code
- [ ] Commit messages follow conventional commits
