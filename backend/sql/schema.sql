-- RAG Document Intelligence System Database Schema
-- This schema creates the necessary tables and functions in the public schema

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- Documents table - stores metadata about uploaded documents
CREATE TABLE IF NOT EXISTS documents (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT NOT NULL,
    file_count INTEGER NOT NULL DEFAULT 0,
    page_count INTEGER NOT NULL DEFAULT 0,
    meta JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Document chunks table - stores individual pages/chunks with embeddings
CREATE TABLE IF NOT EXISTS doc_chunks (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    doc_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    source_path TEXT NOT NULL,
    page_number INTEGER NOT NULL,
    content JSONB NOT NULL, -- {title: string, text: string, page_meta: object}
    embedding VECTOR(1536), -- OpenAI text-embedding-3-small dimensions
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_doc_chunks_doc_id ON doc_chunks(doc_id);
CREATE INDEX IF NOT EXISTS idx_doc_chunks_page_number ON doc_chunks(page_number);
CREATE INDEX IF NOT EXISTS idx_doc_chunks_source_path ON doc_chunks(source_path);

-- Create vector similarity index for embeddings (using cosine distance)
CREATE INDEX IF NOT EXISTS idx_doc_chunks_embedding_cosine 
ON doc_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Function to match document chunks using vector similarity
-- First drop the existing function if it exists
DROP FUNCTION IF EXISTS match_doc_chunks(vector, integer, uuid, jsonb);
DROP FUNCTION IF EXISTS match_doc_chunks(vector(1536), integer, uuid, jsonb);

CREATE OR REPLACE FUNCTION match_doc_chunks(
    query_embedding VECTOR(1536),
    match_count INTEGER DEFAULT 5,
    filter_doc UUID DEFAULT NULL,
    filter_meta JSONB DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    doc_id UUID,
    source_path TEXT,
    page_number INTEGER,
    content JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        dc.id,
        dc.doc_id,
        dc.source_path,
        dc.page_number,
        dc.content,
        1 - (dc.embedding <=> query_embedding) AS similarity
    FROM doc_chunks dc
    INNER JOIN documents d ON dc.doc_id = d.id
    WHERE
        (filter_doc IS NULL OR dc.doc_id = filter_doc)
        AND (filter_meta IS NULL OR d.meta @> filter_meta)
        AND dc.embedding IS NOT NULL
    ORDER BY dc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Function to update document timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers to automatically update timestamps
DROP TRIGGER IF EXISTS update_documents_updated_at ON documents;
CREATE TRIGGER update_documents_updated_at 
    BEFORE UPDATE ON documents 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create RLS (Row Level Security) policies if needed
-- These can be customized based on your authentication requirements
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE doc_chunks ENABLE ROW LEVEL SECURITY;

-- Allow all operations for service role (adjust as needed)
DROP POLICY IF EXISTS "Allow all for service role" ON documents;
CREATE POLICY "Allow all for service role" ON documents 
FOR ALL USING (auth.role() = 'service_role');

DROP POLICY IF EXISTS "Allow all for service role" ON doc_chunks;
CREATE POLICY "Allow all for service role" ON doc_chunks 
FOR ALL USING (auth.role() = 'service_role');

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO anon, authenticated, service_role;

-- Insert a test document to verify schema works
INSERT INTO documents (name, file_count, page_count, meta) 
VALUES ('test-schema.txt', 1, 1, '{"test": true}')
ON CONFLICT DO NOTHING;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'RAG Database Schema created successfully in public schema!';
    RAISE NOTICE 'Tables created: documents, doc_chunks';
    RAISE NOTICE 'Functions created: match_doc_chunks';
    RAISE NOTICE 'Ready for document processing and vector search';
END $$;
