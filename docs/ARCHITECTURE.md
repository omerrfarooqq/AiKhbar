# AiKhbar — System Architecture

This document explains the architecture and the reasoning behind the major
design decisions.

## 1. Architectural Principles

AiKhbar follows **clean architecture**, organised so that dependencies point
inward toward the domain:

```
HTTP layer  →  Orchestration  →  AI / domain services  →  Infrastructure
(api/v1)       (services/)       (rag, tts, summ…)        (db, FAISS, NIM)
```

- **API routes are thin.** Endpoint modules only validate input, call a
  service, and shape the response. They contain no AI or persistence logic.
- **AI pipelines are isolated.** Each capability (scraping, classification,
  summarization, RAG, TTS, analytics, personalization) is its own package with
  a narrow public function. They can be tested and replaced independently.
- **One LLM gateway.** Every model call goes through `services/nvidia_client.py`.
  Swapping the model provider touches exactly one file.
- **Prompts are centralised** in `services/prompts.py` — auditable and tunable
  without editing business logic.

## 2. Component Map

| Layer | Package | Responsibility |
|-------|---------|----------------|
| HTTP | `api/v1` | REST endpoints, request validation |
| HTTP | `websocket` | Live chat & feed sockets |
| Orchestration | `services/ingestion_pipeline.py` | scrape → dedup → classify → store → index → cluster |
| Orchestration | `services/daily_brief.py` | Daily brief composition |
| Orchestration | `services/scheduler.py` | APScheduler periodic ingestion |
| Domain | `scraping/` | RSS parsing, content extraction, dedup |
| Domain | `classification/` | Zero-shot category assignment |
| Domain | `summarization/` | Clustering + multi-document summaries |
| Domain | `rag/` | FAISS store, indexer, retriever, opinion & timeline |
| Domain | `tts/` | Provider-agnostic Urdu speech synthesis |
| Domain | `analytics/` | Media bias / tone analysis |
| Domain | `personalization/` | Affinity learning, personalized feed |
| Infra | `db/`, `models/` | Async PostgreSQL via SQLAlchemy 2 |
| Infra | `core/` | Config, logging, constants, exceptions |

## 3. The Ingestion Pipeline

The pipeline (`services/ingestion_pipeline.py`) is the heart of the system. It
runs on a schedule and on demand:

```
scrape_all()           RSS feeds → article URLs → full-text extraction
   │
filter_new_articles()  exact dedup by URL + content hash
   │
classify_article()     LLM zero-shot category + tags + region (bounded concurrency)
   │
bulk_create()          persist to PostgreSQL
   │
index_pending()        chunk → embed (E5) → FAISS
   │
cluster_recent()       agglomerative clustering per category → StoryCluster
```

Each stage is wrapped in isolated error handling so a failure in one stage
(e.g. classification rate-limit) degrades gracefully instead of aborting the
run. The `IngestionReport` returns per-stage counts and errors.

## 4. RAG Pipeline

```
Indexing:   article.body → chunk_text() (220-word windows, 40 overlap)
                         → EmbeddingService.embed_documents() (E5, normalised)
                         → FaissVectorStore.add()  (IndexIDMap + IndexFlatIP)

Retrieval:  query → embed_query() → FAISS inner-product search (= cosine)
                  → optional category post-filter → top-k chunks
                  → format_context() → injected into LLM prompt
```

RAG powers three features behind one retriever: **conversational chat**,
**opinion aggregation** and **timeline reconstruction**.

**Why FAISS + a flat index?** For an MVP corpus, `IndexFlatIP` gives exact
search with zero tuning. The `FaissVectorStore` interface hides the index type,
so an IVF/HNSW index can be dropped in later without touching callers.

**Why `multilingual-e5-base`?** Scraped articles are Urdu while some retrieved
editorials are English; a strong multilingual embedding model keeps both in one
shared space. E5's `query:`/`passage:` prefixes are applied automatically.

## 5. Story Clustering

Articles from different outlets covering the same event are grouped so they
share one summary, opinion set and timeline. Clustering uses agglomerative
clustering with a cosine-distance threshold on headline+lead embeddings, run
**per category** to prevent cross-topic merges.

## 6. TTS Design

`TTSProvider` is an abstract interface. `TTSService` selects the configured
primary provider, falls back to the secondary if the primary is unavailable or
fails mid-request, and caches synthesised audio on disk keyed by a hash of
`(text, narration_mode, voice)` — identical text is never re-synthesised.

- **Primary:** Urdu Orator API (purpose-built Urdu TTS).
- **Fallback:** Coqui XTTS-v2 (open-source, multilingual, Urdu-capable).

## 7. Personalization

A deliberately **simple, explainable** model: per-category affinity is a
time-decayed, action-weighted sum of interactions (`view < read < listen <
chat < save`), normalised to `[0,1]`. The personalized feed ranks recent
articles by `0.7 · affinity + 0.3 · recency`. Cold-start users are seeded with
their explicitly preferred categories.

## 8. Async & Scheduling

The MVP uses **FastAPI BackgroundTasks + APScheduler** instead of Celery:
fewer moving parts, no broker to operate. CPU-bound work (embedding, FAISS,
Coqui inference) is pushed off the event loop with `asyncio.to_thread`. The
roadmap migrates to Celery + Redis when horizontal scaling is needed.

## 9. Data Model

```
Article ──many-to-one──► StoryCluster ──one-to-many──► Summary
                              │                        Opinion
                              │                        TimelineEvent
User ──one-to-many──► UserInteraction
```

See [`DATABASE.md`](DATABASE.md) for the full schema.

## 10. Configuration & Failure Policy

All configuration is environment-driven via `pydantic-settings`. The system is
**real-calls-only**: if `NVIDIA_API_KEY` is missing, the LLM client raises a
clear `ConfigurationError` rather than silently mocking — failures are explicit.
