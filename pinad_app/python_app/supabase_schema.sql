-- Script SQL para crear tablas en Supabase para el sistema (π)NAD

-- Tabla de documentos
CREATE TABLE IF NOT EXISTS documents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    file_name TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER,
    status TEXT DEFAULT 'pending',
    document_type TEXT,
    date TEXT,
    vendor TEXT,
    invoice_number TEXT,
    subtotal DECIMAL(15,2) DEFAULT 0,
    tax DECIMAL(15,2) DEFAULT 0,
    total DECIMAL(15,2) DEFAULT 0,
    confidence DECIMAL(5,4) DEFAULT 0,
    language TEXT DEFAULT 'es',
    processing_time DECIMAL(10,4) DEFAULT 0,
    raw_text TEXT,
    layout JSONB,
    tables_count INTEGER DEFAULT 0,
    signatures_count INTEGER DEFAULT 0,
    qr_codes_count INTEGER DEFAULT 0,
    barcodes_count INTEGER DEFAULT 0,
    transaction_count INTEGER DEFAULT 0,
    needs_attention BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de items/transacciones
CREATE TABLE IF NOT EXISTS transactions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    description TEXT,
    quantity DECIMAL(10,2) DEFAULT 1,
    unit_price DECIMAL(15,2) DEFAULT 0,
    amount DECIMAL(15,2) DEFAULT 0,
    type TEXT DEFAULT 'item',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de tablas extraídas
CREATE TABLE IF NOT EXISTS extracted_tables (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    table_index INTEGER,
    table_data JSONB,
    row_count INTEGER,
    column_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de firmas detectadas
CREATE TABLE IF NOT EXISTS signatures (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    location TEXT,
    confidence DECIMAL(5,4),
    bounding_box JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de códigos QR
CREATE TABLE IF NOT EXISTS qr_codes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    qr_data TEXT,
    location TEXT,
    confidence DECIMAL(5,4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de códigos de barras
CREATE TABLE IF NOT EXISTS barcodes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    barcode_data TEXT,
    barcode_type TEXT,
    location TEXT,
    confidence DECIMAL(5,4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_document_id ON transactions(document_id);
CREATE INDEX IF NOT EXISTS idx_extracted_tables_document_id ON extracted_tables(document_id);
CREATE INDEX IF NOT EXISTS idx_signatures_document_id ON signatures(document_id);
CREATE INDEX IF NOT EXISTS idx_qr_codes_document_id ON qr_codes(document_id);
CREATE INDEX IF NOT EXISTS idx_barcodes_document_id ON barcodes(document_id);

-- Trigger para actualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
