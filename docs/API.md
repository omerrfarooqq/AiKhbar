# AiKhbar — API Reference

Base URL: `http://localhost:8000`  ·  API prefix: `/api/v1`
Interactive docs: `/docs` (Swagger) and `/redoc`.

All error responses share the shape:
```json
{ "error": "NotFoundError", "detail": "Article xyz not found" }
```

---

## Health

### `GET /api/v1/health`
Liveness probe. → `{ "status": "ok", "app": "AiKhbar", "env": "development" }`

### `GET /api/v1/status`
Detailed status: database connectivity, FAISS vector count, NVIDIA/TTS config.

---

## News

### `GET /api/v1/news`
List and filter articles.

| Query param | Type | Default |
|-------------|------|---------|
| `category` | enum | — |
| `source` | string | — |
| `date_from` / `date_to` | ISO datetime | — |
| `page` | int ≥ 1 | 1 |
| `page_size` | int 1–100 | 20 |

Returns a paginated envelope: `{ items, total, page, page_size }`.

### `GET /api/v1/news/categories`
All categories with article counts.

### `GET /api/v1/news/{article_id}`
Full article detail including body and media-analysis fields.

### `POST /api/v1/news/scrape`
Triggers a background ingestion run. → `202`-style `JobResponse`.

---

## Stories (Clusters)

### `GET /api/v1/stories`
List story clusters. Query: `category`, `limit` (1–50).

### `GET /api/v1/stories/top`
Top clusters by article volume. Query: `limit` (1–15), `category`.

### `GET /api/v1/stories/{cluster_id}`
Cluster detail with nested summaries, opinions and timeline.

### `POST /api/v1/stories/{cluster_id}/summary`
Generate (or return cached) a unified summary.
```json
{ "mode": "short|detailed|morning|deep_dive", "language": "ur" }
```

### `POST /api/v1/stories/{cluster_id}/opinions`
RAG opinion aggregation. Query: `force` (bool) to regenerate.

### `POST /api/v1/stories/{cluster_id}/timeline`
Build a historical timeline. Query: `force` (bool).

### `POST /api/v1/stories/articles/{article_id}/analyze`
Run the media-analysis engine on an article (tone, leaning, sentiment).

---

## Daily Brief

### `POST /api/v1/briefs/daily`
The flagship one-click brief.
```json
{
  "user_id": null,
  "max_stories": 6,
  "mode": "morning",
  "include_audio": true,
  "include_opinions": true
}
```
Returns top stories with summaries, opinions, a joined narration script and an
Urdu audio URL.

---

## Chat

### `POST /api/v1/chat`
RAG-grounded conversational answer.
```json
{
  "question": "اس خبر کی اہمیت کیا ہے؟",
  "cluster_id": "optional-cluster-id",
  "history": [{ "role": "user", "content": "…" }],
  "language": "ur"
}
```
Returns `{ answer, sources[], cluster_id }`.

### `WS /ws/chat`
Stateful chat over WebSocket. Send `{ "question": "...", "cluster_id"?: "..." }`;
the server maintains conversation memory per connection.

### `WS /ws/feed`
Receive live notifications when new stories are ingested.

---

## TTS

### `POST /api/v1/tts/synthesize`
```json
{ "text": "...", "narration_mode": "neutral|podcast|headline", "voice": null }
```
Returns `{ audio_path, audio_url, provider, cached }`. Audio is served from
`/static/audio/`.

---

## Users & Personalization

### `POST /api/v1/users`
Create a user (`email`, `display_name`, `preferred_categories`).

### `GET /api/v1/users/{user_id}`
User profile including learned `category_affinity`.

### `POST /api/v1/users/interactions`
Record an interaction; affinity is recomputed.
```json
{ "user_id": "...", "article_id": "...", "action": "read", "category": "politics",
  "duration_seconds": 45 }
```

### `GET /api/v1/users/{user_id}/feed`
Personalized, affinity-ranked article feed. Query: `limit` (1–50).
