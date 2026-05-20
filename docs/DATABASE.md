# AiKhbar — Database Schema

PostgreSQL 16, accessed asynchronously via SQLAlchemy 2 + asyncpg.
Schema migrations are managed with Alembic (`backend/migrations`).

## Entity-Relationship Overview

```
            ┌──────────────────┐
            │  story_clusters  │
            └─────────┬────────┘
       ┌──────────────┼───────────────┬───────────────┐
       │              │               │               │
 ┌─────▼─────┐  ┌─────▼─────┐  ┌──────▼──────┐  ┌──────▼────────┐
 │ articles  │  │ summaries │  │  opinions   │  │timeline_events│
 └───────────┘  └───────────┘  └─────────────┘  └───────────────┘

 ┌───────────┐        ┌────────────────────┐
 │   users   │────────│ user_interactions  │
 └───────────┘        └────────────────────┘
```

## Tables

### `articles`
One scraped news article with structured metadata and AI enrichment.

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID (str) | PK |
| `headline` | varchar(512) | |
| `body` | text | Extracted full text |
| `url` | varchar(1024) | **unique** |
| `source` | varchar(64) | `bbc_urdu` / `geo_urdu` / `jang` |
| `author` | varchar(256) | nullable |
| `published_at` | timestamptz | from RSS |
| `category` | varchar(32) | AI-classified |
| `category_confidence` | float | |
| `region` | varchar(64) | nullable |
| `tags` | json | keyword list |
| `language` | varchar(8) | default `ur` |
| `content_hash` | varchar(64) | SHA-256, dedup key (indexed) |
| `tone` / `political_leaning` / `sentiment_score` | | media analysis output |
| `is_indexed` | bool | true once in FAISS |
| `cluster_id` | FK → story_clusters | nullable |

Indexes: `(category, published_at)`, `source`, `content_hash`.

### `story_clusters`
A group of articles covering one real-world story.

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID | PK |
| `title` | varchar(512) | representative headline |
| `category` | varchar(32) | indexed |
| `centroid` | json | mean embedding vector |
| `article_count` | int | |
| `first_seen_at` / `last_updated_at` | timestamptz | |
| `keywords` | json | aggregated tags |
| `unified_summary` | text | cached short summary |

### `summaries`
An LLM-generated summary of a cluster at a given depth.

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID | PK |
| `cluster_id` | FK → story_clusters | cascade delete |
| `mode` | varchar(32) | `short`/`detailed`/`morning`/`deep_dive` |
| `language` | varchar(8) | |
| `content` | text | |
| `model` | varchar(128) | LLM used |
| `audio_path` | varchar(512) | generated TTS file |

### `opinions`
A clustered viewpoint produced by RAG opinion aggregation.

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID | PK |
| `cluster_id` | FK → story_clusters | cascade delete |
| `perspective` | varchar(64) | e.g. `pro_government`, `expert` |
| `summary` | text | Urdu viewpoint summary |
| `stance` | varchar(32) | supportive/critical/neutral/mixed |
| `confidence` | float | |
| `source_article_ids` | json | provenance |

### `timeline_events`
A dated historical event linked to a cluster.

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID | PK |
| `cluster_id` | FK → story_clusters | cascade delete |
| `event_date` | timestamptz | nullable |
| `date_label` | varchar(64) | free-text when exact date unknown |
| `title` | varchar(512) | |
| `description` | text | |
| `ordering` | int | chronological index |

### `users`
| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID | PK |
| `email` | varchar(256) | **unique** |
| `display_name` | varchar(128) | |
| `preferred_categories` | json | explicit preferences |
| `saved_topics` | json | |
| `category_affinity` | json | learned `{category: score}` |

### `user_interactions`
| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID | PK |
| `user_id` | FK → users | cascade delete, indexed |
| `article_id` / `cluster_id` | str | indexed |
| `action` | varchar(32) | `view`/`read`/`listen`/`save`/`chat` |
| `category` | varchar(32) | |
| `duration_seconds` | float | engagement time |
| `weight` | int | |

All tables include `created_at` / `updated_at` via the `TimestampMixin`.

## Migrations

```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

In development the app auto-creates tables on startup (`Base.metadata.create_all`).
Production relies exclusively on Alembic migrations.
