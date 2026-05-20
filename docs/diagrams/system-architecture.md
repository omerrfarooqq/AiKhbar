# AiKhbar — System Architecture Diagrams

Diagrams use [Mermaid](https://mermaid.js.org) — they render on GitHub and in
most Markdown viewers.

## 1. High-Level System

```mermaid
graph TB
    subgraph Client
        UI[React + Vite SPA<br/>Redux Toolkit · Framer Motion]
    end

    subgraph Backend["FastAPI Backend"]
        API[API v1 Routes]
        WS[WebSocket Routes]
        ORCH[Orchestration<br/>ingestion · daily brief · scheduler]
        AI[AI / Domain Services<br/>scraping · classification · summarization<br/>RAG · TTS · analytics · personalization]
    end

    subgraph Data
        PG[(PostgreSQL)]
        FAISS[(FAISS Index)]
    end

    subgraph External
        NIM[NVIDIA NIM LLM]
        ORATOR[Urdu Orator TTS]
        SRC[BBC Urdu · Geo · Jang]
    end

    UI -->|REST| API
    UI -->|WebSocket| WS
    API --> ORCH
    WS --> AI
    ORCH --> AI
    AI --> PG
    AI --> FAISS
    AI --> NIM
    AI --> ORATOR
    ORCH --> SRC
```

## 2. News Ingestion Pipeline

```mermaid
flowchart LR
    A[Scheduler / API trigger] --> B[Scrape RSS feeds]
    B --> C[Extract full text<br/>trafilatura]
    C --> D[Deduplicate<br/>URL + content hash]
    D --> E[Classify<br/>LLM zero-shot]
    E --> F[(Persist to PostgreSQL)]
    F --> G[Chunk + embed<br/>E5 embeddings]
    G --> H[(FAISS index)]
    F --> I[Cluster articles<br/>agglomerative]
    I --> J[(Story clusters)]
```

## 3. RAG Pipeline

```mermaid
flowchart TB
    subgraph Indexing
        A1[Article body] --> A2[Chunk<br/>220-word windows]
        A2 --> A3[Embed<br/>multilingual-e5-base]
        A3 --> A4[(FAISS<br/>IndexFlatIP)]
    end

    subgraph Retrieval
        B1[User query / story title] --> B2[Embed query]
        B2 --> B3[Cosine search top-k]
        A4 --> B3
        B3 --> B4[Format context]
        B4 --> B5[LLM generation]
    end

    B5 --> C1[Chat answer]
    B5 --> C2[Opinion aggregation]
    B5 --> C3[Timeline]
```

## 4. One-Click Daily Brief

```mermaid
sequenceDiagram
    participant U as User
    participant API as Daily Brief API
    participant DB as PostgreSQL
    participant S as Summarizer
    participant R as RAG Opinion
    participant T as TTS Service

    U->>API: POST /briefs/daily
    API->>DB: select top / personalized clusters
    loop each story
        API->>S: summarize_cluster()
        S->>S: LLM unified summary
        API->>R: aggregate_opinions()
        R->>R: retrieve + LLM viewpoints
    end
    API->>T: synthesize narration (Urdu)
    T-->>API: audio URL
    API-->>U: stories + summaries + opinions + audio
```

## 5. TTS Provider Selection

```mermaid
flowchart TB
    A[synthesize text] --> B{Audio cached?}
    B -->|yes| C[Return cached file]
    B -->|no| D{Primary available?}
    D -->|yes| E[Urdu Orator]
    D -->|no| F{Fallback available?}
    F -->|yes| G[Coqui XTTS-v2]
    F -->|no| H[503 ConfigurationError]
    E -->|fails mid-request| G
    E --> I[Cache + return]
    G --> I
```
