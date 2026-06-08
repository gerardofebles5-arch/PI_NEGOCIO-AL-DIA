# Configuración de Supabase

## Fecha
Junio 8, 2026

## Información del Proyecto

### Dashboard URL
https://supabase.com/dashboard/project/rteuftlsbglpgcawsdqz

### Project URL
https://rteuftlsbglpgcawsdqz.supabase.co

### Project Reference
rteuftlsbglpgcawsdqz

### API Keys

#### Publishable Key (Anon)
```
sb_publishable_eUlKRfeFNvqdURtW_abbIA_N8Qte0l3
```

#### Service Role Key (Secret)
```
[OBTENER DESDE DASHBOARD > Settings > API]
```

### Database Connection String
```
postgresql://postgres:[YOUR-PASSWORD]@db.rteuftlsbglpgcawsdqz.supabase.co:5432/postgres
```

**IMPORTANTE:** Reemplaza `[YOUR-PASSWORD]` con la contraseña que configuraste al crear el proyecto.

---

## Comandos CLI

### Instalar Supabase CLI
```bash
npm install -g supabase
```

### Login
```bash
supabase login
```

### Inicializar proyecto local
```bash
supabase init
```

### Vincular con proyecto remoto
```bash
supabase link --project-ref rteuftlsbglpgcawsdqz
```

### Ejecutar migraciones
```bash
supabase db push
```

### Generar tipos TypeScript
```bash
supabase gen types typescript --project-id rteuftlsbglpgcawsdqz > types/supabase.ts
```

---

## Estructura de Base de Datos

### Tablas Principales

#### tenants
```sql
CREATE TABLE tenants (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  plan VARCHAR(50) DEFAULT 'free',
  status VARCHAR(50) DEFAULT 'active',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### users
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  firebase_uid VARCHAR(255) UNIQUE NOT NULL,
  tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255),
  role VARCHAR(50) DEFAULT 'client', -- 'super_admin', 'tenant_admin', 'client', 'viewer'
  status VARCHAR(50) DEFAULT 'active',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### documents
```sql
CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  file_name VARCHAR(255) NOT NULL,
  file_url TEXT NOT NULL,
  file_type VARCHAR(50),
  file_size INTEGER,
  status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'processing', 'processed', 'error'
  extracted_data JSONB,
  ocr_confidence DECIMAL(5,2),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### transactions
```sql
CREATE TABLE transactions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
  document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
  type VARCHAR(50) NOT NULL, -- 'income', 'expense'
  amount DECIMAL(15,2) NOT NULL,
  description TEXT,
  category VARCHAR(100),
  date DATE NOT NULL,
  rif VARCHAR(20),
  invoice_number VARCHAR(100),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## Row Level Security (RLS)

### Habilitar RLS
```sql
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
```

### Políticas de Seguridad

#### tenants
```sql
-- Solo super admin puede ver todos los tenants
CREATE POLICY "Super admin can view all tenants" ON tenants
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE firebase_uid = auth.uid() AND role = 'super_admin'
    )
  );

-- Tenant admin puede ver su propio tenant
CREATE POLICY "Tenant admin can view own tenant" ON tenants
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE firebase_uid = auth.uid() AND tenant_id = tenants.id
    )
  );
```

#### users
```sql
-- Usuarios pueden ver usuarios de su tenant
CREATE POLICY "Users can view tenant users" ON users
  FOR SELECT USING (
    tenant_id IN (
      SELECT tenant_id FROM users WHERE firebase_uid = auth.uid()
    )
  );
```

#### documents
```sql
-- Usuarios pueden ver documentos de su tenant
CREATE POLICY "Users can view tenant documents" ON documents
  FOR SELECT USING (
    tenant_id IN (
      SELECT tenant_id FROM users WHERE firebase_uid = auth.uid()
    )
  );

-- Usuarios pueden crear documentos en su tenant
CREATE POLICY "Users can create documents" ON documents
  FOR INSERT WITH CHECK (
    tenant_id IN (
      SELECT tenant_id FROM users WHERE firebase_uid = auth.uid()
    )
  );
```

#### transactions
```sql
-- Usuarios pueden ver transacciones de su tenant
CREATE POLICY "Users can view tenant transactions" ON transactions
  FOR SELECT USING (
    tenant_id IN (
      SELECT tenant_id FROM users WHERE firebase_uid = auth.uid()
    )
  );
```

---

## Índices

```sql
-- Índices para mejor rendimiento
CREATE INDEX idx_users_tenant_id ON users(tenant_id);
CREATE INDEX idx_users_firebase_uid ON users(firebase_uid);
CREATE INDEX idx_documents_tenant_id ON documents(tenant_id);
CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_transactions_tenant_id ON transactions(tenant_id);
CREATE INDEX idx_transactions_document_id ON transactions(document_id);
CREATE INDEX idx_transactions_date ON transactions(date);
```

---

## Triggers

```sql
-- Trigger para actualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tenants_updated_at BEFORE UPDATE ON tenants
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

## Integración con Firebase Authentication

Supabase puede usar Firebase Authentication mediante:

1. **JWT de Firebase:** Usar el token de Firebase para autenticación en Supabase
2. **Custom Auth:** Implementar autenticación personalizada
3. **Firebase Auth + Supabase:** Usar Firebase Auth para login, Supabase para datos

**Para este proyecto:** Usaremos Firebase Auth para login y pasaremos el Firebase UID a Supabase para autorización.

---

## Próximos Pasos

1. Crear las tablas en Supabase
2. Configurar Row Level Security
3. Crear índices
4. Configurar triggers
5. Probar la conexión desde Flutter
