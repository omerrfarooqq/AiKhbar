# AiKhbar — Deployment Guide

Deployment is performed **after development is complete**. This guide covers a
container-based production deployment.

## 1. Production Configuration

Set in the production environment (never commit `.env`):
```ini
APP_ENV=production
DEBUG=false
SECRET_KEY=<long-random-string>
ALLOWED_ORIGINS=https://yourdomain.com
DATABASE_URL=postgresql+asyncpg://user:pass@db-host:5432/aikhbar
NVIDIA_API_KEY=<key>
URDU_ORATOR_API_KEY=<key>
REDIS_ENABLED=true
REDIS_URL=redis://redis-host:6379/0
LOG_JSON=true
```

In production the app does **not** auto-create tables — run migrations:
```bash
alembic upgrade head
```

## 2. Build & Run with Docker Compose

```bash
docker compose -f docker-compose.yml up --build -d
```

The backend image runs Gunicorn with Uvicorn workers:
```
gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 2 -b 0.0.0.0:8000
```
Tune `-w` (workers) to roughly `2 × CPU cores`.

## 3. Persistent Volumes

Persist these paths:
- PostgreSQL data — `pgdata` volume.
- FAISS index + audio cache — `backend/storage/` (mounted).
- Logs — `backend/logs/`.

The FAISS index is a single file; back it up alongside the database so vectors
and rows stay consistent.

## 4. Reverse Proxy / TLS

Front the stack with nginx, Caddy or a managed load balancer terminating TLS.
Ensure WebSocket upgrade headers are forwarded for `/ws/`. The bundled
`frontend/nginx.conf` already proxies `/api`, `/static` and `/ws` to the
backend service.

## 5. Scheduler

APScheduler runs **in-process** inside the backend. With multiple backend
replicas, run the scheduler in exactly **one** instance (set
`SCHEDULER_ENABLED=true` on one replica, `false` on the rest) to avoid
duplicate scraping — or migrate to the Celery beat scheduler (see roadmap).

## 6. Recommended Hosting

| Component | Suggested platform |
|-----------|--------------------|
| Backend + frontend | Render, Railway, Fly.io, or any Docker host / VPS |
| PostgreSQL | Managed Postgres (Neon, Supabase, RDS) |
| Redis | Managed Redis (Upstash, ElastiCache) |
| LLM | NVIDIA NIM (hosted) — no self-hosting needed |

## 7. Health & Monitoring

- Liveness: `GET /api/v1/health`
- Readiness/diagnostics: `GET /api/v1/status`
- The backend container ships a `HEALTHCHECK` hitting `/api/v1/health`.
- With `LOG_JSON=true`, logs are structured for ingestion by a log platform.

## 8. Scaling Notes

- Backend API is stateless → scale horizontally behind a load balancer.
- The FAISS flat index lives on disk per instance; for multi-replica writes,
  move to a shared vector service or a single indexer instance.
- Migrate background work to **Celery + Redis** before high scrape volume.
