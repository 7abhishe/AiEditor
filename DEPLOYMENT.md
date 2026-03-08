# 🚀 Deployment Guide — CodeGenie AI Editor

## Deployment Targets

| Environment | Platform | URL |
|---|---|---|
| **Production** | Render.com | https://codegenie-backend-27y2.onrender.com |
| **Frontend** | Render.com | https://codegenie-web.onrender.com |
| **Local Dev** | localhost | http://localhost:8000 / http://localhost:5173 |

---

## 1. Render.com Deployment (Current)

### Backend

1. **Create a Web Service** on [Render Dashboard](https://dashboard.render.com)
2. Connect your GitHub repository
3. Configure:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120`
4. **Environment Variables** (set in Render dashboard):

   | Variable | Value | Required |
   |---|---|---|
   | `GEMINI_API_KEY` | Your Gemini API key | ✅ Yes |
   | `GEMINI_MODEL` | `gemini-3-flash-preview` | ✅ Yes |
   | `DATABASE_URL` | Render PostgreSQL internal URL | ✅ Yes |
   | `JWT_SECRET_KEY` | Random 64-char hex string | ✅ Yes |
   | `DEBUG` | `false` | ✅ Yes |
   | `MASTER_API_KEY` | Strong random key | Optional |
   | `REDIS_URL` | Redis URL (if using) | Optional |

5. **Database:** Create a PostgreSQL instance on Render, copy the Internal Database URL

### Frontend

1. **Create a Static Site** on Render
2. Connect same GitHub repository
3. Configure:
   - **Root Directory:** `frontend`
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `frontend/dist`

---

## 2. Docker Deployment

```bash
# Full stack
docker compose up --build -d

# Backend only
docker build -t codegenie-backend ./backend
docker run -d -p 8000:8000 --env-file .env codegenie-backend
```

### docker-compose.yml Services:
- `backend` — FastAPI on port 8000
- `frontend` — Vite dev server on port 5173
- `db` — PostgreSQL on port 5432

---

## 3. AWS Deployment (Advanced)

As described in `architect.md`:

```
User → ALB → ECS (FastAPI x3) → RDS PostgreSQL
                               → ElastiCache Redis
                               → Google Gemini API
```

### Steps:
1. Push Docker image to ECR
2. Create ECS Fargate cluster
3. Create RDS PostgreSQL instance
4. Create ALB with HTTPS listener
5. Set environment variables in ECS task definition
6. Configure auto-scaling (min 2, max 10 containers)

---

## 4. Environment Variables Reference

```bash
# Required
GEMINI_API_KEY=           # Google Gemini API key
GEMINI_MODEL=             # AI model name
DATABASE_URL=             # Database connection string
JWT_SECRET_KEY=           # JWT signing secret (change in production!)

# Optional
DEBUG=false               # Enable Swagger docs
MASTER_API_KEY=           # Legacy API key auth
REDIS_URL=                # Redis for caching (future)
API_HOST=0.0.0.0          # Server bind address
API_PORT=8000             # Server port
PORT=8000                 # Render.com sets this automatically
```

---

## 5. Health Check

```bash
curl https://codegenie-backend-27y2.onrender.com/health
# {"status":"ok","app_name":"CodeGenie AI Editor","version":"0.1.0"}
```

---

## 6. Post-Deployment Checklist

- [ ] Set `DEBUG=false` in production
- [ ] Set a strong random `JWT_SECRET_KEY` (not the default!)
- [ ] Verify CORS origins match your frontend URL
- [ ] Test `/health` endpoint returns 200
- [ ] Verify Swagger is NOT accessible at `/docs`
- [ ] Test login and signup work
- [ ] Verify rate limiting is active (try 11 rapid login attempts)
