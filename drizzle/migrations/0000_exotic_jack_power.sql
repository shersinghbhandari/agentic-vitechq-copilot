CREATE TABLE "document_chunks" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"document_id" uuid NOT NULL,
	"tenant_id" varchar(100) NOT NULL,
	"chunk_index" integer NOT NULL,
	"chunk_text" text NOT NULL,
	"embedding" vector(384),
	"metadata" jsonb DEFAULT '{}'::jsonb,
	"created_at" timestamp with time zone DEFAULT now()
);
--> statement-breakpoint
CREATE TABLE "document_metadata" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"document_id" uuid NOT NULL,
	"tenant_id" varchar(100) NOT NULL,
	"metadata_key" varchar(150) NOT NULL,
	"metadata_value" text NOT NULL,
	"metadata_type" varchar(50) DEFAULT 'STRING' NOT NULL,
	"created_at" timestamp with time zone DEFAULT now()
);
--> statement-breakpoint
CREATE TABLE "documents" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tenant_id" varchar(100) NOT NULL,
	"source_type" varchar(50) NOT NULL,
	"source_uri" text NOT NULL,
	"file_name" varchar(500) NOT NULL,
	"file_type" varchar(50) NOT NULL,
	"checksum" varchar(128) NOT NULL,
	"uploaded_by" varchar(255),
	"status" varchar(50) DEFAULT 'UPLOADED' NOT NULL,
	"metadata" jsonb DEFAULT '{}'::jsonb,
	"created_at" timestamp with time zone DEFAULT now(),
	"updated_at" timestamp with time zone DEFAULT now()
);
--> statement-breakpoint
CREATE TABLE "ingestion_errors" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"job_id" uuid NOT NULL,
	"document_id" uuid NOT NULL,
	"tenant_id" varchar(100) NOT NULL,
	"correlation_id" varchar(255),
	"stage" varchar(100) NOT NULL,
	"error_message" text NOT NULL,
	"stack_trace" text,
	"retry_count" integer DEFAULT 0,
	"created_at" timestamp with time zone DEFAULT now()
);
--> statement-breakpoint
CREATE TABLE "ingestion_jobs" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"document_id" uuid NOT NULL,
	"tenant_id" varchar(100) NOT NULL,
	"uploaded_by" varchar(255),
	"correlation_id" varchar(255),
	"status" varchar(50) DEFAULT 'PENDING' NOT NULL,
	"stage" varchar(100) DEFAULT 'UPLOAD',
	"total_chunks" integer DEFAULT 0,
	"processed_chunks" integer DEFAULT 0,
	"error_count" integer DEFAULT 0,
	"retry_count" integer DEFAULT 0,
	"error_message" text,
	"started_at" timestamp with time zone DEFAULT now(),
	"completed_at" timestamp with time zone,
	"created_at" timestamp with time zone DEFAULT now(),
	"updated_at" timestamp with time zone DEFAULT now()
);
--> statement-breakpoint
ALTER TABLE "document_chunks" ADD CONSTRAINT "document_chunks_document_id_documents_id_fk" FOREIGN KEY ("document_id") REFERENCES "public"."documents"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "document_metadata" ADD CONSTRAINT "document_metadata_document_id_documents_id_fk" FOREIGN KEY ("document_id") REFERENCES "public"."documents"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "ingestion_errors" ADD CONSTRAINT "ingestion_errors_job_id_ingestion_jobs_id_fk" FOREIGN KEY ("job_id") REFERENCES "public"."ingestion_jobs"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "ingestion_errors" ADD CONSTRAINT "ingestion_errors_document_id_documents_id_fk" FOREIGN KEY ("document_id") REFERENCES "public"."documents"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "ingestion_jobs" ADD CONSTRAINT "ingestion_jobs_document_id_documents_id_fk" FOREIGN KEY ("document_id") REFERENCES "public"."documents"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "idx_chunks_document" ON "document_chunks" USING btree ("document_id");--> statement-breakpoint
CREATE INDEX "idx_chunks_tenant" ON "document_chunks" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "idx_document_metadata_document" ON "document_metadata" USING btree ("document_id");--> statement-breakpoint
CREATE INDEX "idx_document_metadata_tenant" ON "document_metadata" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "idx_document_metadata_key" ON "document_metadata" USING btree ("metadata_key");--> statement-breakpoint
CREATE INDEX "idx_document_metadata_tenant_key_value" ON "document_metadata" USING btree ("tenant_id","metadata_key","metadata_value");--> statement-breakpoint
CREATE UNIQUE INDEX "uq_documents_tenant_checksum" ON "documents" USING btree ("tenant_id","checksum");--> statement-breakpoint
CREATE INDEX "idx_documents_tenant" ON "documents" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "idx_documents_status" ON "documents" USING btree ("status");--> statement-breakpoint
CREATE INDEX "idx_errors_job" ON "ingestion_errors" USING btree ("job_id");--> statement-breakpoint
CREATE INDEX "idx_errors_document" ON "ingestion_errors" USING btree ("document_id");--> statement-breakpoint
CREATE INDEX "idx_errors_tenant" ON "ingestion_errors" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "idx_errors_correlation" ON "ingestion_errors" USING btree ("correlation_id");--> statement-breakpoint
CREATE INDEX "idx_errors_stage" ON "ingestion_errors" USING btree ("stage");--> statement-breakpoint
CREATE INDEX "idx_jobs_document" ON "ingestion_jobs" USING btree ("document_id");--> statement-breakpoint
CREATE INDEX "idx_jobs_tenant" ON "ingestion_jobs" USING btree ("tenant_id");--> statement-breakpoint
CREATE INDEX "idx_jobs_status" ON "ingestion_jobs" USING btree ("status");--> statement-breakpoint
CREATE INDEX "idx_jobs_stage" ON "ingestion_jobs" USING btree ("stage");--> statement-breakpoint
CREATE INDEX "idx_jobs_correlation" ON "ingestion_jobs" USING btree ("correlation_id");--> statement-breakpoint
CREATE INDEX "idx_jobs_uploaded_by" ON "ingestion_jobs" USING btree ("uploaded_by");