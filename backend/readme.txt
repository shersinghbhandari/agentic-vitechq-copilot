agentic-vitechq-copilot/
│
├── backend/
│   │
│   ├── app/
│   │   │
│   │   ├── api/
│   │   │   └── document_routes.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── logging.py
│   │   │
│   │   ├── rag/
│   │   │   │
│   │   │   ├── db/
│   │   │   │   ├── schema.sql
│   │   │   │   ├── models.py
│   │   │   │   └── repositories/
│   │   │   │       ├── document_repository.py
│   │   │   │       ├── chunk_repository.py
│   │   │   │       ├── ingestion_job_repository.py
│   │   │   │       └── ingestion_error_repository.py
│   │   │   │
│   │   │   ├── ingestion/
│   │   │   │   ├── ingestion_service.py
│   │   │   │   ├── duplicate_service.py
│   │   │   │   ├── checksum_service.py
│   │   │   │   └── notification_service.py
│   │   │   │
│   │   │   ├── loaders/
│   │   │   │   ├── base_loader.py
│   │   │   │   ├── upload_loader.py
│   │   │   │   └── s3_loader.py
│   │   │   │
│   │   │   ├── parsing/
│   │   │   │   ├── base_parser.py
│   │   │   │   ├── pdf_parser.py
│   │   │   │   ├── txt_parser.py
│   │   │   │   └── docx_parser.py
│   │   │   │
│   │   │   ├── chunking/
│   │   │   │   └── chunk_service.py
│   │   │   │
│   │   │   ├── embeddings/
│   │   │   │   └── embedding_service.py
│   │   │   │
│   │   │   ├── vectorstore/
│   │   │   │   └── pgvector_store.py
│   │   │   │
│   │   │   └── models/
│   │   │       ├── document_models.py
│   │   │       └── ingestion_models.py
│   │   │
│   │   └── main.py
│   │
│   ├── scripts/
│   │   ├── local_ingest.py
│   │   └── create_tables.py
│   │
│   ├── tests/
│   │
│   ├── requirements.txt
│   └── .env
│
├── docker-compose.yml
├── README.md
└── .gitignore



models/	Database persistence	SQLAlchemy tables
schemas/	API/request/response objects	Pydantic
graph/	LangGraph runtime state	IngestionState

| Folder                  | Purpose in Your Agentic VitechQ Copilot Project                                                                                                                                                                               |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `backend/`              | Main backend application containing FastAPI APIs, RAG pipeline, LangGraph orchestration, services, DB logic, ingestion workflows, retrieval pipeline, and AI orchestration.                                                   |
| `app/`                  | Main Python application package root.                                                                                                                                                                                         |
| `__pycache__/`          | Auto-generated Python bytecode cache. Not part of business logic. Should be ignored in Git.                                                                                                                                   |
| `api/`                  | FastAPI REST endpoints. Handles upload APIs, chat APIs, search APIs, admin APIs, logs APIs, health APIs, etc.                                                                                                                 |
| `core/`                 | Shared infrastructure utilities such as DB connection management, config loading, dependency injection, environment configuration, constants, common helpers, startup initialization, middleware, and app lifecycle handling. |
| `rag/`                  | Entire Retrieval-Augmented Generation platform implementation. Core GenAI engine of your system.                                                                                                                              |
| `rag/caching/`          | Response caching, embedding caching, retrieval caching, prompt caching, Redis integration, Bedrock/OpenAI token optimization, semantic cache implementation.                                                                  |
| `rag/chunking/`         | Text chunking logic. Splits extracted documents into semantic chunks before embeddings generation. Includes recursive splitters, token-aware splitters, semantic chunking strategies.                                         |
| `rag/citations/`        | Citation tracking and source attribution system for generated answers. Helps show which chunks/documents were used to generate a response.                                                                                    |
| `rag/context_building/` | Builds final LLM context window from retrieved chunks. Includes context compression, context ordering, token budgeting, prompt assembly.                                                                                      |
| `rag/db/`               | Database layer. SQLAlchemy models, repositories, DB transaction handling, persistence logic for documents, chunks, jobs, embeddings metadata, logs, conversations.                                                            |
| `rag/db/repositories/`  | Repository layer implementing DB access abstraction. Keeps business logic separate from raw SQLAlchemy queries.                                                                                                               |
| `rag/embeddings/`       | Embedding generation logic using OpenAI, Bedrock Titan, HuggingFace, SentenceTransformers, etc. Converts chunks into vector embeddings.                                                                                       |
| `rag/enums/`            | Shared enums/constants such as job status, document status, pipeline stages, retrieval modes, model types, source types.                                                                                                      |
| `rag/evaluation/`       | RAG evaluation framework. Measures retrieval quality, hallucination detection, answer relevance, latency, faithfulness, precision/recall, benchmark testing.                                                                  |
| `rag/extractors/`       | File extraction logic for PDF, DOCX, TXT, CSV, HTML, etc. Converts raw uploaded documents into plain text.                                                                                                                    |
| `rag/filtering/`        | Metadata filtering, tenant filtering, RBAC filtering, semantic filtering, document-level authorization filtering before retrieval.                                                                                            |
| `rag/generation/`       | Final answer generation using LLMs. Responsible for prompt execution, streaming responses, formatting answers, and LLM orchestration.                                                                                         |
| `rag/graphs/`           | LangGraph orchestration layer. Defines graph workflows for ingestion, retrieval, agent routing, retries, conditional branching, and future agentic workflows.                                                                 |
| `rag/guardrails/`       | AI safety and validation layer. Prevents hallucinations, prompt injection, unsafe output, data leakage, invalid citations, and malicious prompts.                                                                             |
| `rag/hybrid_search/`    | Hybrid retrieval implementation combining vector search + keyword/BM25 search + metadata filtering.                                                                                                                           |
| `rag/indexing/`         | Index creation and indexing workflows for pgvector/OpenSearch/Pinecone/vector stores. Handles vector persistence optimization.                                                                                                |
| `rag/ingestion/`        | High-level ingestion orchestration logic for document intake pipelines. May later include schedulers, batch ingestion, streaming ingestion.                                                                                   |
| `rag/jobs/`             | Background worker logic and job execution framework. Handles async ingestion jobs, retries, scheduling, status updates, long-running tasks.                                                                                   |
| `rag/loaders/`          | Document loaders responsible for loading files from local disk, S3, SharePoint, Confluence, Jira, APIs, databases, etc.                                                                                                       |
| `rag/memory/`           | Conversational memory layer for chat agents. Stores prior interactions, summaries, session memory, long-term memory, semantic memory.                                                                                         |
| `rag/models/`           | Runtime/domain models and dataclasses. Contains non-DB business objects such as RawDocument, RetrievalResult, AgentContext, etc.                                                                                              |
| `rag/observability/`    | Logging, tracing, metrics, OpenTelemetry integration, correlation IDs, request tracing, monitoring, audit logging, performance analytics.                                                                                     |
| `rag/parsing/`          | Parsing logic for structured data extraction such as tables, JSON extraction, markdown parsing, HTML parsing, XML parsing.                                                                                                    |
| `rag/preprocessing/`    | Text cleanup and normalization before chunking. Includes OCR cleanup, whitespace normalization, metadata enrichment, language normalization.                                                                                  |
| `rag/prompts/`          | Centralized prompt management. Stores prompt templates for retrieval, summarization, chat agents, classification, guardrails, evaluation.                                                                                     |
| `rag/reranking/`        | Reranking pipeline using cross-encoders or LLM reranking to improve retrieval quality after vector search.                                                                                                                    |
| `rag/retrieval/`        | Core retrieval engine. Performs semantic search, hybrid search, top-k retrieval, tenant filtering, metadata filtering, query expansion.                                                                                       |
| `rag/services/`         | Business service layer containing reusable orchestration/business logic for documents, embeddings, extraction, indexing, jobs, retrieval, etc.                                                                                |
| `rag/vectorstore/`      | Vector DB abstraction layer. Handles pgvector, Pinecone, OpenSearch, ChromaDB, FAISS integrations.                                                                                                                            |
| `security/`             | Authentication, authorization, JWT validation, RBAC, tenant isolation, API security, encryption utilities, SSO integration.                                                                                                   |
| `data/`                 | Local data storage root used during development/testing.                                                                                                                                                                      |
| `data/raw/`             | Raw uploaded documents before extraction/chunking. Temporary or persistent source document storage.                                                                                                                           |
| `logs/`                 | Centralized application logs.                                                                                                                                                                                                 |
| `logs/users/`           | User-specific logs grouped by correlation ID, uploaded_by, request tracking, ingestion pipeline tracing.                                                                                                                      |
| `scripts/`              | Utility scripts for DB migration, cleanup, ingestion testing, indexing rebuilds, benchmarking, deployment helpers, setup scripts.                                                                                             |
| `tests/`                | Unit tests, integration tests, API tests, RAG evaluation tests, ingestion pipeline tests, LangGraph workflow tests.                                                                                                           |


Initial IngestionState
{
  document_id,
  job_id,
  tenant_id,
  uploaded_by,
  correlation_id,
  file_type,
  local_path
}
        │
        ▼
┌────────────────────┐
│ parsing_node        │
│ Extract raw text    │
└─────────┬──────────┘
          │ raw_text
          ▼
┌────────────────────────────┐
│ langchain_document_node     │
│ Convert text to             │
│ LangChain Document          │
└─────────┬──────────────────┘
          │ langchain_documents
          ▼
┌────────────────────┐
│ chunking_node       │
│ LangChain splitter  │
│ creates chunks      │
└─────────┬──────────┘
          │ chunks
          ▼
┌────────────────────┐
│ vectorstore_node    │
│ Save chunks to DB   │
│ document_chunks     │
└─────────┬──────────┘
          │ processed_chunks
          ▼
┌────────────────────┐
│ finalize_node       │
│ Mark job COMPLETED  │
└─────────┬──────────┘
          ▼
      END