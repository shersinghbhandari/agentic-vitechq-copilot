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