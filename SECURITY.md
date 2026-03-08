# 🔒 Security Policy — CodeGenie AI Editor

## Supported Versions

| Version | Supported |
|---|---|
| 0.1.x (current) | ✅ Active |

---

## Security Measures Implemented

### Authentication & Authorization
- **JWT-based authentication** — Signup/login with email and password
- **Password hashing** — PBKDF2-SHA256 via passlib
- **Token expiry** — 7-day expiry enforced by python-jose
- **Token refresh** — `POST /api/v1/auth/refresh` for seamless renewal
- **Conversation ownership** — Users can only access their own conversations (IDOR protection)
- **Inactive user check** — `is_active=True` enforced in `get_current_user`

### Rate Limiting
| Endpoint | Limit |
|---|---|
| Login | 10 requests/minute/IP |
| Signup | 5 requests/minute/IP |
| AI endpoints (chat, completion, explain, refactor, bugs, tests) | 30 requests/minute/IP |
| Agent endpoints | 15 requests/minute/IP |

### CORS
- Origins restricted to: `localhost:5173`, `localhost:3000`, `codegenie-web.onrender.com`
- Methods restricted to: `GET`, `POST`, `PUT`, `OPTIONS`, `HEAD`
- Credentials allowed with specific origins only

### Security Headers
| Header | Value |
|---|---|
| X-Content-Type-Options | `nosniff` |
| X-Frame-Options | `DENY` |
| Strict-Transport-Security | `max-age=31536000; includeSubDomains` |
| Content-Security-Policy | `default-src 'self'; frame-ancestors 'none'` |
| X-XSS-Protection | `1; mode=block` |
| Referrer-Policy | `strict-origin-when-cross-origin` |
| Permissions-Policy | `camera=(), microphone=(), geolocation=()` |

### Input Validation
- **Pydantic models** — All API inputs validated via schemas
- **SQL injection** — Prevented by SQLAlchemy parameterized queries
- **Null byte rejection** — Email inputs reject `\x00` characters
- **Unicode validation** — Non-ASCII characters blocked in email local parts
- **Request body limit** — 1MB maximum payload size
- **Malformed JSON** — Returns 422 via Pydantic validation

### Error Handling
- Generic error messages returned to clients (no stack traces or raw exceptions)
- Error reference codes included for debugging (`ref: ExceptionType`)

### API Documentation
- Swagger UI disabled in production (`DEBUG=false`)
- `/docs`, `/redoc`, `/openapi.json` only accessible in development

---

## Penetration Test Results

**Date:** March 8, 2026  
**Tests:** 43 across 8 OWASP categories  
**Score:** 37/43 passing (86%)

| Category | Score |
|---|---|
| Authentication & JWT | 8/8 |
| Authorization & Access Control | 6/6 |
| Input Validation & Injection | 6/7 |
| Rate Limiting & DoS | 4/4 |
| CORS & Security Headers | 4/4 |
| Data Exposure & Leakage | 5/5 |
| Frontend Security | 3/5 |
| Session Management | 3/4 |

Full reports available in:
- `pentest_report.html` — Original findings
- `pentest_remediation_report.html` — Post-fix results

---

## Reporting a Vulnerability

If you discover a security vulnerability, please:

1. **DO NOT** open a public issue
2. Email: **security@codegenie.dev** (or contact the maintainer directly)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
4. Expected response time: **48 hours**

---

## Environment Security

⚠️ **Critical reminders:**
- Never commit `.env` to Git (it's in `.gitignore`)
- Use `.env.example` as a template
- Change `JWT_SECRET_KEY` from the default in production
- Change `MASTER_API_KEY` from the default in production
- Generate secrets with: `openssl rand -hex 32`
