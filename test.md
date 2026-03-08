# 🔒 CodeGenie — Penetration Test Results

**Date:** 2026-03-08  
**Target:** `http://localhost:8000` (FastAPI + SQLite)  
**Score:** 17/43 (39%) — ✅ 17 Pass | ❌ 12 Fail | ⚠️ 14 Warn

---

## 🔴 Critical Failures (12)

| ID | Test | Finding |
|---|---|---|
| AUTH-01 | Brute-Force Login | No rate limiting — 50 attempts in 0.9s |
| AUTH-03 | Expired Token | `/search/conversations` returned 404 instead of 401 |
| AUTH-07 | Missing Auth Header | Endpoint returned 404 instead of 401 |
| AUTH-08 | JWT None Algorithm | Endpoint returned 404 instead of 401 |
| AUTHZ-01 | Cross-User Conversation | **No ownership check** — any user can post to any conversation |
| AUTHZ-04 | IDOR (Conversation) | **No ownership validation** on conversation_id |
| INJ-05 | Oversized Payload | No request body size limit — accepts 10MB+ |
| DOS-01 | Login Rate Limiting | No rate limiting on login endpoint |
| DOS-02 | Signup Spam | 20 accounts in 0.4s — no rate limiting |
| DOS-03 | AI Endpoint Abuse | No per-user rate limiting on AI endpoints |
| CORS-01 | CORS Origin | `Access-Control-Allow-Origin: *` — allows any domain |
| CORS-03 | Security Headers | Missing: X-Content-Type-Options, X-Frame-Options, HSTS, CSP |

## 🟡 Warnings (14)

| ID | Test | Finding |
|---|---|---|
| AUTHZ-06 | Swagger Exposure | `/docs`, `/redoc`, `/openapi.json` publicly accessible |
| INJ-01 | XSS via Chat | Skipped (Gemini offline) — AI responses rendered as HTML |
| INJ-03 | Path Traversal | Git endpoints accept file paths — needs audit |
| INJ-07 | Null Byte | Null byte email accepted (status 201) |
| DOS-04 | Slowloris | Only gunicorn timeout=120 protects |
| CORS-02 | Preflight | All HTTP methods allowed including DELETE |
| CORS-04 | Swagger | API docs publicly accessible |
| DATA-01 | Error Leakage | AI service errors forwarded to client |
| FE-01 | Token in localStorage | Vulnerable to XSS — HttpOnly cookies safer |
| FE-02 | XSS in AI Responses | Markdown/HTML rendering needs sanitization |
| FE-04 | Source Maps | Verify excluded from production build |
| SESSION-01 | Token After Logout | No server-side invalidation — JWT valid until expiry |
| SESSION-02 | Concurrent Sessions | Unlimited sessions — no limit policy |
| SESSION-04 | Token Refresh | No refresh endpoint — 7-day hard expiry |

## ✅ Passed (17)

| ID | Test | Result |
|---|---|---|
| AUTH-02 | JWT Tampering | Tampered tokens rejected (401) |
| AUTH-04 | Weak Passwords | All weak passwords rejected by Pydantic validation |
| AUTH-05 | Duplicate Email | Duplicate registration blocked (400) |
| AUTH-06 | SQL Injection | SQLAlchemy parameterized queries block all SQLi |
| AUTHZ-02 | Privilege Escalation | No admin roles in JWT — nothing to escalate |
| AUTHZ-03 | Inactive User | `is_active` check enforced in `get_current_user` |
| AUTHZ-05 | Method Tampering | Unsupported HTTP methods return 405/422 |
| INJ-02 | SSTI | No template rendering — Pydantic serialization only |
| INJ-04 | Command Injection | No subprocess calls — AI generates suggestions only |
| INJ-06 | Malformed JSON | Pydantic validation returns 422 |
| DATA-02 | User Enumeration | Consistent responses — cannot enumerate users |
| DATA-03 | JWT Payload | Only `sub` and `exp` — no sensitive data |
| DATA-04 | DB URL Exposure | Health endpoint clean |
| DATA-05 | Env Variables | No config endpoints accessible |
| FE-03 | Open Redirect | No redirect parameters in SPA |
| FE-05 | HTTPS | Render enforces HTTPS by default |
| SESSION-03 | Token Expiry | 7-day expiry enforced by python-jose |

---

## 🛠️ Recommended Fixes (Priority Order)

### 🔴 P0 — Critical (Fix Immediately)

1. **Add Rate Limiting** — Install `slowapi` for login/signup/AI endpoints
2. **Fix CORS** — Restrict `allow_origins` to the actual frontend domain
3. **Add Security Headers** — Use `starlette-securiy` or middleware
4. **Add Conversation Ownership Check** — Verify `conversation.user_id == current_user.id`
5. **Add Request Body Size Limit** — Set `max_request_size` in middleware

### 🟡 P1 — High (Fix Before Production)

6. **Disable Swagger in Production** — Set `docs_url=None, redoc_url=None` when `DEBUG=False`
7. **Sanitize Error Messages** — Don't forward raw exception details to client
8. **Add Request Body Size Limit** — Middleware to reject payloads > 1MB
9. **Null Byte Email Validation** — Add explicit null byte check

### 🟠 P2 — Medium (Roadmap Items)

10. **Token Refresh Endpoint** — Add `/api/v1/auth/refresh`
11. **Server-Side Token Revocation** — Token blacklist on logout
12. **Content Security Policy** — Add CSP headers
13. **Consider HttpOnly Cookies** — Move JWT from localStorage
