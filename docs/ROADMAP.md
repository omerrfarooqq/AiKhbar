# AiKhbar — Development Roadmap

A phased plan from the current MVP toward a production-scale platform.

## Phase 0 — MVP (current)

- [x] Clean-architecture FastAPI backend
- [x] RSS ingestion (BBC Urdu, Geo, Jang) + extraction + dedup
- [x] LLM zero-shot classification (NVIDIA NIM)
- [x] Story clustering + multi-document Urdu summarization
- [x] FAISS RAG: chat, opinion aggregation, timeline
- [x] TTS abstraction: Urdu Orator + Coqui fallback
- [x] Media analysis & personalization engines
- [x] One-click daily brief
- [x] Cinematic React + Redux frontend
- [x] Docker, docs, academic report

## Phase 1 — Hardening (weeks 1–3 post-MVP)

- [ ] JWT authentication & per-user sessions
- [ ] Rate limiting on AI endpoints
- [ ] Integration test suite against a test database
- [ ] Structured request tracing / metrics (OpenTelemetry)
- [ ] Saved-topics & bookmarks dashboard
- [ ] Frontend WebSocket chat wired to `/ws/chat`

## Phase 2 — Scale (months 1–2)

- [ ] **Celery + Redis** for distributed scraping, summarization, TTS jobs
- [ ] Celery Beat replaces in-process APScheduler
- [ ] FAISS IVF/HNSW index (or a managed vector DB) for large corpora
- [ ] Redis caching of summaries, feeds and retrieval results
- [ ] Streaming LLM responses over WebSocket (token-by-token chat)
- [ ] CDN for generated audio files

## Phase 3 — Intelligence (months 2–4)

- [ ] Fine-tuned Urdu transformer classifier (replaces zero-shot LLM call)
- [ ] Cross-lingual ingestion (English sources merged into Urdu clusters)
- [ ] Entity & topic graph for richer timeline reconstruction
- [ ] Embedding-based / collaborative-filtering recommender
- [ ] Automated fact-consistency checks on generated summaries
- [ ] Sentiment trend analytics over time per topic

## Phase 4 — Product (months 4+)

- [ ] Mobile app (React Native) sharing the same API
- [ ] Scheduled email / push daily briefs
- [ ] Multi-voice narration & user-selectable presenters
- [ ] Editor dashboard for source management & moderation
- [ ] Public API with API keys for third-party developers

## Future Scalability Suggestions

1. **Separate the indexer service.** Move FAISS writes into a dedicated
   service so API replicas stay stateless and read-only against the index.
2. **Event-driven pipeline.** Replace the linear ingestion pipeline with a
   message queue (Kafka/Redis Streams): scrape → classify → index → cluster
   as independent consumers.
3. **Model routing.** Route cheap tasks (classification) to the fast model and
   expensive tasks (deep dive) to the large model — already structured via the
   single LLM gateway.
4. **Caching layer.** Summaries, opinions and timelines are deterministic per
   cluster — aggressively cache them in Redis with cluster-version keys.
5. **Observability.** Per-pipeline-stage metrics and dashboards to catch
   upstream (NVIDIA / scrape target) degradation early.
