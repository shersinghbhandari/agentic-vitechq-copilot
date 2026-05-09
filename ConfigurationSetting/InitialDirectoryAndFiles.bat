@echo off
SET ROOT=agentic-vitechq-copilot

REM Root
mkdir %ROOT%
cd %ROOT%

REM =========================
REM apps
REM =========================
mkdir apps
mkdir apps\api
mkdir apps\web
mkdir apps\worker

REM =========================
REM rag
REM =========================
mkdir rag

mkdir rag\ingestion
type nul > rag\ingestion\ingestion_service.py
type nul > rag\ingestion\ingestion_pipeline.py
type nul > rag\ingestion\ingestion_models.py

mkdir rag\loaders
type nul > rag\loaders\s3_loader.py
type nul > rag\loaders\local_loader.py
type nul > rag\loaders\jira_loader.py

mkdir rag\parsing
type nul > rag\parsing\pdf_parser.py
type nul > rag\parsing\image_parser.py
type nul > rag\parsing\text_parser.py
type nul > rag\parsing\html_parser.py

mkdir rag\preprocessing
type nul > rag\preprocessing\cleaner.py
type nul > rag\preprocessing\normalizer.py
type nul > rag\preprocessing\metadata_enricher.py

mkdir rag\chunking
type nul > rag\chunking\recursive_chunker.py
type nul > rag\chunking\semantic_chunker.py
type nul > rag\chunking\chunk_models.py

mkdir rag\embeddings
type nul > rag\embeddings\base_embedding_provider.py
type nul > rag\embeddings\bedrock_embeddings.py
type nul > rag\embeddings\openai_embeddings.py
type nul > rag\embeddings\embedding_models.py

mkdir rag\vectorstore
type nul > rag\vectorstore\base_vectorstore.py
type nul > rag\vectorstore\opensearch_store.py
type nul > rag\vectorstore\pgvector_store.py
type nul > rag\vectorstore\pinecone_store.py

mkdir rag\indexing
type nul > rag\indexing\indexing_service.py
type nul > rag\indexing\indexing_models.py

mkdir rag\retrieval
type nul > rag\retrieval\semantic_retriever.py
type nul > rag\retrieval\metadata_filter_retriever.py
type nul > rag\retrieval\retrieval_models.py

mkdir rag\hybrid_search
type nul > rag\hybrid_search\hybrid_search_service.py
type nul > rag\hybrid_search\bm25_search.py

mkdir rag\reranking
type nul > rag\reranking\reranker.py
type nul > rag\reranking\cross_encoder_reranker.py

mkdir rag\context_building
type nul > rag\context_building\context_builder.py
type nul > rag\context_building\token_manager.py
type nul > rag\context_building\citation_builder.py

mkdir rag\generation
type nul > rag\generation\base_llm_provider.py
type nul > rag\generation\bedrock_generation.py
type nul > rag\generation\prompt_builder.py
type nul > rag\generation\response_models.py

mkdir rag\citations
type nul > rag\citations\citation_service.py

mkdir rag\memory
type nul > rag\memory\conversation_memory.py
type nul > rag\memory\session_memory.py

mkdir rag\caching
type nul > rag\caching\redis_cache.py
type nul > rag\caching\semantic_cache.py

mkdir rag\filtering
type nul > rag\filtering\tenant_filter.py
type nul > rag\filtering\security_filter.py

mkdir rag\observability
type nul > rag\observability\logger.py
type nul > rag\observability\tracing.py
type nul > rag\observability\metrics.py
type nul > rag\observability\token_usage.py

mkdir rag\evaluation
type nul > rag\evaluation\ragas_evaluator.py
type nul > rag\evaluation\retrieval_eval.py

mkdir rag\guardrails
type nul > rag\guardrails\hallucination_guard.py
type nul > rag\guardrails\pii_guard.py

mkdir rag\prompts
type nul > rag\prompts\retrieval_prompt.txt
type nul > rag\prompts\system_prompt.txt
type nul > rag\prompts\citation_prompt.txt

REM =========================
REM agents
REM =========================
mkdir agents

mkdir agents\orchestrator
type nul > agents\orchestrator\agent_router.py
type nul > agents\orchestrator\workflow_engine.py
type nul > agents\orchestrator\orchestration_models.py

mkdir agents\retrieval_agent
type nul > agents\retrieval_agent\retrieval_agent.py

mkdir agents\web_search_agent
type nul > agents\web_search_agent\web_search_agent.py

mkdir agents\summarizer_agent
type nul > agents\summarizer_agent\summarizer_agent.py

mkdir agents\tools
type nul > agents\tools\search_tool.py
type nul > agents\tools\retrieval_tool.py
type nul > agents\tools\calculator_tool.py

mkdir agents\memory_agent
type nul > agents\memory_agent\memory_agent.py

REM =========================
REM infrastructure
REM =========================
mkdir infrastructure
mkdir infrastructure\aws
mkdir infrastructure\aws\api_gateway
mkdir infrastructure\aws\lambda
mkdir infrastructure\aws\opensearch
mkdir infrastructure\aws\dynamodb
mkdir infrastructure\aws\s3
mkdir infrastructure\aws\cognito

mkdir infrastructure\docker
mkdir infrastructure\terraform

REM =========================
REM tests
REM =========================
mkdir tests
mkdir tests\unit
mkdir tests\integration
mkdir tests\evaluation

REM =========================
REM scripts
REM =========================
mkdir scripts
type nul > scripts\local_ingest.py
type nul > scripts\reindex.py
type nul > scripts\load_sample_data.py

REM =========================
REM docs
REM =========================
mkdir docs
mkdir docs\architecture
mkdir docs\api
mkdir docs\diagrams

REM =========================
REM config
REM =========================
mkdir config
type nul > config\dev.yaml
type nul > config\prod.yaml
type nul > config\logging.yaml

REM =========================
REM shared
REM =========================
mkdir shared
type nul > shared\constants.py
type nul > shared\exceptions.py
type nul > shared\models.py
type nul > shared\utils.py

REM =========================
REM root files
REM =========================
type nul > .env
type nul > docker-compose.yml
type nul > requirements.txt
type nul > README.md
type nul > pyproject.toml

echo.
echo ==========================================
echo Project structure created successfully!
echo ==========================================
pause