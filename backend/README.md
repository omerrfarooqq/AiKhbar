# AiKhbar Backend

FastAPI backend for the AiKhbar Urdu news intelligence platform.

## Run

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements/dev.txt
uvicorn app.main:app --reload
```

Docs at <http://localhost:8000/docs>. See [`../docs/SETUP.md`](../docs/SETUP.md)
for the full guide.

## Layout

| Path | Purpose |
|------|---------|
| `app/api/v1/` | REST endpoints (HTTP layer only) |
| `app/core/` | Config, logging, constants, exceptions |
| `app/db/`, `app/models/` | Async PostgreSQL + ORM |
| `app/scraping/` | RSS scraping, extraction, dedup |
| `app/classification/` | Zero-shot news classifier |
| `app/summarization/` | Clustering + multi-doc summarization |
| `app/rag/` | FAISS store, indexer, retriever, opinion, timeline |
| `app/tts/` | Urdu Orator + Coqui providers, narration |
| `app/analytics/` | Media analysis engine |
| `app/personalization/` | Affinity engine, personalized feed |
| `app/services/` | Repositories + orchestration |
| `app/websocket/` | Live chat & feed sockets |

## Commands

```bash
pytest                          # tests
ruff check .                    # lint
python -m scripts.run_ingestion # run one ingestion cycle
alembic upgrade head            # apply migrations (production)
```
