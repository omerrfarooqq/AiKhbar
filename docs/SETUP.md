# AiKhbar — Setup Guide

## 1. Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.11 or 3.12 |
| Node.js | 20+ |
| PostgreSQL | 16 |
| Git | any recent |
| (optional) Docker | 24+ with Compose v2 |

You also need a **free NVIDIA NIM API key** — register at
<https://build.nvidia.com> and create a key.

## 2. Clone & Environment

```bash
git clone https://github.com/omerrfarooqq/AiKhbar.git
cd AiKhbar
cp .env.example .env
```

Edit `.env` and set at minimum:
```ini
NVIDIA_API_KEY=nvapi-xxxxxxxxxxxxxxxx
POSTGRES_PASSWORD=your_password
URDU_ORATOR_API_KEY=          # optional; Coqui fallback used if empty
```

## 3. Database

Create the database (matching `.env`):
```sql
CREATE DATABASE aikhbar;
CREATE USER aikhbar WITH PASSWORD 'aikhbar';
GRANT ALL PRIVILEGES ON DATABASE aikhbar TO aikhbar;
```

## 4. Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements/dev.txt
```

> The first run downloads the `multilingual-e5-base` embedding model
> (~1 GB) and, if used, Coqui XTTS-v2 weights. Allow time on first start.

Run the API:
```bash
uvicorn app.main:app --reload
```

- In development the schema is auto-created on startup.
- For production, apply migrations instead: `alembic upgrade head`.

Verify: <http://localhost:8000/api/v1/health> and `/docs`.

### Optional: enable the Coqui TTS fallback
Coqui is heavy and commented out in `requirements/base.txt`. To enable:
```bash
pip install TTS
```

## 5. Frontend

```bash
cd frontend
npm install
npm run dev
```
Open <http://localhost:5173>. Vite proxies `/api` and `/ws` to the backend.

## 6. First Data

The scheduler scrapes automatically every `SCRAPE_INTERVAL_MINUTES`. To pull
data immediately:

```bash
# from backend/, with the venv active
python -m scripts.run_ingestion
```

or `POST /api/v1/news/scrape`.

## 7. Docker (all-in-one)

```bash
docker compose up --build
```
Brings up PostgreSQL, Redis, backend (`:8000`) and frontend (`:5173`).

## 8. Tests

```bash
cd backend
pytest
ruff check .
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ConfigurationError: NVIDIA_API_KEY is not set` | Set the key in `.env`. |
| `faiss` install fails on Windows | Use Python 3.11/3.12 64-bit; install `faiss-cpu` from a wheel. |
| Embedding model download slow | First run only; it is cached locally afterwards. |
| No articles appear | Run an ingestion cycle (step 6). |
| TTS returns 503 | Set `URDU_ORATOR_API_KEY` or `pip install TTS` for the fallback. |
