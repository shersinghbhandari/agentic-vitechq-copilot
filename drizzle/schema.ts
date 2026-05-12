import {
  pgTable,
  uuid,
  varchar,
  text,
  timestamp,
  integer,
  jsonb,
  index,
  uniqueIndex,
} from "drizzle-orm/pg-core";

import { vector } from "drizzle-orm/pg-core";

export const documents = pgTable(
  "documents",
  {
    id: uuid("id").defaultRandom().primaryKey(),

    tenantId: varchar("tenant_id", { length: 100 }).notNull(),

    sourceType: varchar("source_type", {
      length: 50,
    }).notNull(),

    sourceUri: text("source_uri").notNull(),

    fileName: varchar("file_name", {
      length: 500,
    }).notNull(),

    fileType: varchar("file_type", {
      length: 50,
    }).notNull(),

    checksum: varchar("checksum", {
      length: 128,
    }).notNull(),

    uploadedBy: varchar("uploaded_by", {
      length: 255,
    }),

    status: varchar("status", {
      length: 50,
    })
      .notNull()
      .default("UPLOADED"),

    metadata: jsonb("metadata").default({}),

    createdAt: timestamp("created_at", {
      withTimezone: true,
    }).defaultNow(),

    updatedAt: timestamp("updated_at", {
      withTimezone: true,
    }).defaultNow(),
  },
  (table) => ({
    tenantChecksumUnique: uniqueIndex(
      "uq_documents_tenant_checksum"
    ).on(table.tenantId, table.checksum),

    documentTenantIdx: index(
      "idx_documents_tenant"
    ).on(table.tenantId),

    documentStatusIdx: index(
      "idx_documents_status"
    ).on(table.status),
  })
);

export const documentMetadata = pgTable(
  "document_metadata",
  {
    id: uuid("id").defaultRandom().primaryKey(),

    documentId: uuid("document_id")
      .notNull()
      .references(() => documents.id, {
        onDelete: "cascade",
      }),

    tenantId: varchar("tenant_id", {
      length: 100,
    }).notNull(),

    metadataKey: varchar("metadata_key", {
      length: 150,
    }).notNull(),

    metadataValue: text("metadata_value").notNull(),

    metadataType: varchar("metadata_type", {
      length: 50,
    })
      .notNull()
      .default("STRING"),

    createdAt: timestamp("created_at", {
      withTimezone: true,
    }).defaultNow(),
  },
  (table) => ({
    documentMetadataDocumentIdx: index(
      "idx_document_metadata_document"
    ).on(table.documentId),

    documentMetadataTenantIdx: index(
      "idx_document_metadata_tenant"
    ).on(table.tenantId),

    documentMetadataKeyIdx: index(
      "idx_document_metadata_key"
    ).on(table.metadataKey),

    documentMetadataTenantKeyValueIdx: index(
      "idx_document_metadata_tenant_key_value"
    ).on(
      table.tenantId,
      table.metadataKey,
      table.metadataValue
    ),
  })
);

export const documentChunks = pgTable(
  "document_chunks",
  {
    id: uuid("id").defaultRandom().primaryKey(),

    documentId: uuid("document_id")
      .notNull()
      .references(() => documents.id, {
        onDelete: "cascade",
      }),

    tenantId: varchar("tenant_id", {
      length: 100,
    }).notNull(),

    chunkIndex: integer("chunk_index").notNull(),

    chunkText: text("chunk_text").notNull(),

    embedding: vector("embedding", {
      dimensions: 1536,
    }),

    metadata: jsonb("metadata").default({}),

    createdAt: timestamp("created_at", {
      withTimezone: true,
    }).defaultNow(),
  },
  (table) => ({
    chunkDocumentIdx: index(
      "idx_chunks_document"
    ).on(table.documentId),

    chunkTenantIdx: index(
      "idx_chunks_tenant"
    ).on(table.tenantId),
  })
);

export const ingestionJobs = pgTable(
  "ingestion_jobs",
  {
    id: uuid("id").defaultRandom().primaryKey(),

    documentId: uuid("document_id")
      .notNull()
      .references(() => documents.id, {
        onDelete: "cascade",
      }),

    tenantId: varchar("tenant_id", {
      length: 100,
    }).notNull(),

    uploadedBy: varchar("uploaded_by", {
      length: 255,
    }),

    correlationId: varchar("correlation_id", {
      length: 255,
    }),

    status: varchar("status", {
      length: 50,
    })
      .notNull()
      .default("PENDING"),

    stage: varchar("stage", {
      length: 100,
    }).default("UPLOAD"),

    totalChunks: integer("total_chunks").default(0),

    processedChunks: integer(
      "processed_chunks"
    ).default(0),

    errorCount: integer("error_count").default(0),

    retryCount: integer("retry_count").default(0),

    errorMessage: text("error_message"),

    startedAt: timestamp("started_at", {
      withTimezone: true,
    }).defaultNow(),

    completedAt: timestamp("completed_at", {
      withTimezone: true,
    }),

    createdAt: timestamp("created_at", {
      withTimezone: true,
    }).defaultNow(),

    updatedAt: timestamp("updated_at", {
      withTimezone: true,
    }).defaultNow(),
  },
  (table) => ({
    jobDocumentIdx: index(
      "idx_jobs_document"
    ).on(table.documentId),

    jobTenantIdx: index(
      "idx_jobs_tenant"
    ).on(table.tenantId),

    jobStatusIdx: index(
      "idx_jobs_status"
    ).on(table.status),

    jobStageIdx: index(
      "idx_jobs_stage"
    ).on(table.stage),

    jobCorrelationIdx: index(
      "idx_jobs_correlation"
    ).on(table.correlationId),

    jobUploadedByIdx: index(
      "idx_jobs_uploaded_by"
    ).on(table.uploadedBy),
  })
);

export const ingestionErrors = pgTable(
  "ingestion_errors",
  {
    id: uuid("id").defaultRandom().primaryKey(),

    jobId: uuid("job_id")
      .notNull()
      .references(() => ingestionJobs.id, {
        onDelete: "cascade",
      }),

    documentId: uuid("document_id")
      .notNull()
      .references(() => documents.id, {
        onDelete: "cascade",
      }),

    tenantId: varchar("tenant_id", {
      length: 100,
    }).notNull(),

    correlationId: varchar("correlation_id", {
      length: 255,
    }),

    stage: varchar("stage", {
      length: 100,
    }).notNull(),

    errorMessage: text("error_message").notNull(),

    stackTrace: text("stack_trace"),

    retryCount: integer("retry_count").default(0),

    createdAt: timestamp("created_at", {
      withTimezone: true,
    }).defaultNow(),
  },
  (table) => ({
    errorJobIdx: index("idx_errors_job").on(
      table.jobId
    ),

    errorDocumentIdx: index(
      "idx_errors_document"
    ).on(table.documentId),

    errorTenantIdx: index(
      "idx_errors_tenant"
    ).on(table.tenantId),

    errorCorrelationIdx: index(
      "idx_errors_correlation"
    ).on(table.correlationId),

    errorStageIdx: index(
      "idx_errors_stage"
    ).on(table.stage),
  })
);