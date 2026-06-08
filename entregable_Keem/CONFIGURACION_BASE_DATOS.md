# Configuración de Base de Datos en Google Cloud

## Fecha
Junio 7, 2026

## Objetivo
Configurar Firestore (NoSQL) y Cloud SQL (PostgreSQL) para almacenar documentos, transacciones contables, y datos multi-tenant del sistema de escaneo en línea.

---

## 1. Firestore (NoSQL)

### 1.1 Creación del Proyecto Firestore

```bash
# Crear proyecto en Google Cloud
gcloud projects create pinad-scanning-system --name="PINAD Scanning System"

# Habilitar Firestore API
gcloud services enable firestore.googleapis.com --project=pinad-scanning-system

# Crear base de datos Firestore
gcloud firestore databases create --region=us-central1 --project=pinad-scanning-system
```

### 1.2 Esquema de Firestore

#### Colección: tenants
```javascript
{
  tenantId: string (document ID),
  name: string,
  rif: string,
  email: string,
  phone: string,
  address: string,
  plan: 'basic' | 'pro' | 'enterprise',
  maxUsers: number,
  maxDocuments: number,
  maxStorage: number (en GB),
  createdAt: Timestamp,
  updatedAt: Timestamp,
  isActive: boolean,
}
```

**Reglas de Firestore:**
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Solo admins pueden crear/eliminar tenants
    match /tenants/{tenantId} {
      allow read: if request.auth != null;
      allow write: if request.auth.token.admin == true;
    }
    
    // Usuarios solo pueden acceder a su tenant
    match /tenants/{tenantId}/users/{userId} {
      allow read, write: if request.auth != null 
                        && request.auth.token.tenantId == tenantId
                        && (request.auth.token.userId == userId 
                            || request.auth.token.role == 'admin');
    }
    
    // Documentos aislados por tenant
    match /tenants/{tenantId}/documents/{documentId} {
      allow read: if request.auth != null 
                   && request.auth.token.tenantId == tenantId;
      allow write: if request.auth != null 
                    && request.auth.token.tenantId == tenantId
                    && (request.auth.token.userId == resource.data.userId
                        || request.auth.token.role == 'admin');
    }
  }
}
```

#### Colección: users
```javascript
{
  userId: string (document ID),
  tenantId: string,
  email: string,
  displayName: string,
  role: 'admin' | 'client' | 'viewer',
  phoneNumber: string,
  photoURL: string,
  createdAt: Timestamp,
  updatedAt: Timestamp,
  lastLoginAt: Timestamp,
  isActive: boolean,
}
```

#### Colección: documents
```javascript
{
  documentId: string (document ID),
  tenantId: string,
  userId: string,
  fileName: string,
  fileType: 'invoice' | 'receipt' | 'contract' | 'other',
  storagePath: string,
  fileSize: number,
  status: 'uploaded' | 'processing' | 'processed' | 'failed' | 'archived',
  extractedData: {
    invoiceNumber: string,
    date: string,
    amount: number,
    taxAmount: number,
    currency: string,
    vendor: {
      name: string,
      rif: string,
      address: string,
    },
    items: Array<{
      name: string,
      quantity: number,
      unitPrice: number,
      totalPrice: number,
      taxRate: number,
    }>,
    paymentMethod: string,
    paymentTerms: string,
  },
  processingMetadata: {
    processorId: string,
    processingTime: number,
    confidence: number,
    errors: Array<string>,
  },
  createdAt: Timestamp,
  processedAt: Timestamp,
  archivedAt: Timestamp,
}
```

#### Colección: document_history
```javascript
{
  historyId: string (document ID),
  tenantId: string,
  documentId: string,
  action: 'created' | 'updated' | 'deleted' | 'processed' | 'archived',
  userId: string,
  oldData: object,
  newData: object,
  timestamp: Timestamp,
}
```

#### Colección: notifications
```javascript
{
  notificationId: string (document ID),
  tenantId: string,
  userId: string,
  type: 'document_processed' | 'document_failed' | 'system_alert' | 'quota_exceeded',
  title: string,
  message: string,
  data: object,
  isRead: boolean,
  createdAt: Timestamp,
  readAt: Timestamp,
}
```

### 1.3 Índices de Firestore

```bash
# Crear índices compuestos
gcloud firestore indexes composite create \
  --collection-group=documents \
  --query-field-config=order-by=tenantId,asc \
  --query-field-config=order-by=userId,asc \
  --query-field-config=order-by=createdAt,desc \
  --project=pinad-scanning-system

gcloud firestore indexes composite create \
  --collection-group=documents \
  --query-field-config=order-by=tenantId,asc \
  --query-field-config=order-by=status,asc \
  --query-field-config=order-by=createdAt,desc \
  --project=pinad-scanning-system

gcloud firestore indexes composite create \
  --collection-group=notifications \
  --query-field-config=order-by=tenantId,asc \
  --query-field-config=order-by=userId,asc \
  --query-field-config=order-by=isRead,asc \
  --query-field-config=order-by=createdAt,desc \
  --project=pinad-scanning-system
```

---

## 2. Cloud SQL (PostgreSQL)

### 2.1 Creación de Instancia Cloud SQL

```bash
# Habilitar Cloud SQL API
gcloud services enable sqladmin.googleapis.com --project=pinad-scanning-system

# Crear instancia de Cloud SQL
gcloud sql instances create pinad-postgres \
  --project=pinad-scanning-system \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --storage-auto-increase \
  --storage-size=10GB \
  --backup-start-time=02:00 \
  --enable-bin-log \
  --retention-period=7

# Crear base de datos
gcloud sql databases create pinad_db \
  --instance=pinad-postgres \
  --project=pinad-scanning-system

# Crear usuario
gcloud sql users create pinad_user \
  --instance=pinad-postgres \
  --password=YOUR_SECURE_PASSWORD \
  --project=pinad-scanning-system
```

### 2.2 Esquema de Base de Datos

#### Tabla: tenants
```sql
CREATE TABLE tenants (
  tenant_id VARCHAR(255) PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  rif VARCHAR(50) UNIQUE,
  email VARCHAR(255) UNIQUE NOT NULL,
  phone VARCHAR(50),
  address TEXT,
  plan VARCHAR(50) DEFAULT 'basic' CHECK (plan IN ('basic', 'pro', 'enterprise')),
  max_users INTEGER DEFAULT 5,
  max_documents INTEGER DEFAULT 1000,
  max_storage_gb INTEGER DEFAULT 10,
  current_users INTEGER DEFAULT 0,
  current_documents INTEGER DEFAULT 0,
  current_storage_gb DECIMAL(10, 2) DEFAULT 0,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tenants_email ON tenants(email);
CREATE INDEX idx_tenants_rif ON tenants(rif);
CREATE INDEX idx_tenants_plan ON tenants(plan);
```

#### Tabla: users
```sql
CREATE TABLE users (
  user_id VARCHAR(255) PRIMARY KEY,
  tenant_id VARCHAR(255) NOT NULL,
  firebase_uid VARCHAR(255) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  display_name VARCHAR(255),
  role VARCHAR(50) DEFAULT 'client' CHECK (role IN ('admin', 'client', 'viewer')),
  phone VARCHAR(50),
  photo_url TEXT,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_login_at TIMESTAMP,
  FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id) ON DELETE CASCADE
);

CREATE INDEX idx_users_tenant_id ON users(tenant_id);
CREATE INDEX idx_users_firebase_uid ON users(firebase_uid);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

#### Tabla: clients
```sql
CREATE TABLE clients (
  client_id SERIAL PRIMARY KEY,
  tenant_id VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  rif VARCHAR(50),
  email VARCHAR(255),
  phone VARCHAR(50),
  address TEXT,
  tax_id VARCHAR(50),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id) ON DELETE CASCADE
);

CREATE INDEX idx_clients_tenant_id ON clients(tenant_id);
CREATE INDEX idx_clients_rif ON clients(rif);
CREATE INDEX idx_clients_name ON clients(name);
```

#### Tabla: accounts (Plan de Cuentas)
```sql
CREATE TABLE accounts (
  account_id SERIAL PRIMARY KEY,
  tenant_id VARCHAR(255) NOT NULL,
  account_code VARCHAR(50) NOT NULL,
  account_name VARCHAR(255) NOT NULL,
  account_type VARCHAR(50) NOT NULL CHECK (account_type IN ('asset', 'liability', 'equity', 'income', 'expense')),
  parent_account_id INTEGER,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id) ON DELETE CASCADE,
  FOREIGN KEY (parent_account_id) REFERENCES accounts(account_id),
  UNIQUE (tenant_id, account_code)
);

CREATE INDEX idx_accounts_tenant_id ON accounts(tenant_id);
CREATE INDEX idx_accounts_code ON accounts(account_code);
CREATE INDEX idx_accounts_type ON accounts(account_type);
```

#### Tabla: transactions
```sql
CREATE TABLE transactions (
  transaction_id SERIAL PRIMARY KEY,
  tenant_id VARCHAR(255) NOT NULL,
  document_id VARCHAR(255),
  client_id INTEGER,
  account_id INTEGER NOT NULL,
  transaction_type VARCHAR(50) NOT NULL CHECK (transaction_type IN ('debit', 'credit')),
  amount DECIMAL(15, 2) NOT NULL,
  tax_amount DECIMAL(15, 2) DEFAULT 0,
  currency VARCHAR(10) DEFAULT 'VES',
  exchange_rate DECIMAL(10, 4) DEFAULT 1,
  date DATE NOT NULL,
  description TEXT,
  reference VARCHAR(255),
  category VARCHAR(100),
  status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'verified', 'reconciled')),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  verified_at TIMESTAMP,
  verified_by VARCHAR(255),
  FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id) ON DELETE CASCADE,
  FOREIGN KEY (client_id) REFERENCES clients(client_id),
  FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);

CREATE INDEX idx_transactions_tenant_id ON transactions(tenant_id);
CREATE INDEX idx_transactions_document_id ON transactions(document_id);
CREATE INDEX idx_transactions_client_id ON transactions(client_id);
CREATE INDEX idx_transactions_account_id ON transactions(account_id);
CREATE INDEX idx_transactions_date ON transactions(date);
CREATE INDEX idx_transactions_type ON transactions(transaction_type);
CREATE INDEX idx_transactions_status ON transactions(status);
```

#### Tabla: journal_entries (Asientos Contables)
```sql
CREATE TABLE journal_entries (
  entry_id SERIAL PRIMARY KEY,
  tenant_id VARCHAR(255) NOT NULL,
  entry_number VARCHAR(50) NOT NULL,
  entry_date DATE NOT NULL,
  description TEXT,
  reference VARCHAR(255),
  status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'posted', 'void')),
  total_debit DECIMAL(15, 2) DEFAULT 0,
  total_credit DECIMAL(15, 2) DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  posted_at TIMESTAMP,
  posted_by VARCHAR(255),
  FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id) ON DELETE CASCADE,
  UNIQUE (tenant_id, entry_number)
);

CREATE INDEX idx_journal_entries_tenant_id ON journal_entries(tenant_id);
CREATE INDEX idx_journal_entries_date ON journal_entries(entry_date);
CREATE INDEX idx_journal_entries_number ON journal_entries(entry_number);
CREATE INDEX idx_journal_entries_status ON journal_entries(status);
```

#### Tabla: journal_entry_lines (Líneas de Asiento)
```sql
CREATE TABLE journal_entry_lines (
  line_id SERIAL PRIMARY KEY,
  entry_id INTEGER NOT NULL,
  account_id INTEGER NOT NULL,
  transaction_type VARCHAR(50) NOT NULL CHECK (transaction_type IN ('debit', 'credit')),
  amount DECIMAL(15, 2) NOT NULL,
  description TEXT,
  FOREIGN KEY (entry_id) REFERENCES journal_entries(entry_id) ON DELETE CASCADE,
  FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);

CREATE INDEX idx_journal_entry_lines_entry_id ON journal_entry_lines(entry_id);
CREATE INDEX idx_journal_entry_lines_account_id ON journal_entry_lines(account_id);
```

#### Tabla: audit_log
```sql
CREATE TABLE audit_log (
  log_id SERIAL PRIMARY KEY,
  tenant_id VARCHAR(255) NOT NULL,
  user_id VARCHAR(255) NOT NULL,
  action VARCHAR(100) NOT NULL,
  entity_type VARCHAR(100),
  entity_id VARCHAR(255),
  old_data JSONB,
  new_data JSONB,
  ip_address VARCHAR(50),
  user_agent TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id) ON DELETE CASCADE
);

CREATE INDEX idx_audit_log_tenant_id ON audit_log(tenant_id);
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_action ON audit_log(action);
CREATE INDEX idx_audit_log_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);
```

#### Tabla: quotas (Límites de Uso)
```sql
CREATE TABLE quotas (
  quota_id SERIAL PRIMARY KEY,
  tenant_id VARCHAR(255) NOT NULL,
  resource_type VARCHAR(50) NOT NULL CHECK (resource_type IN ('documents', 'storage', 'api_calls', 'users')),
  current_usage INTEGER DEFAULT 0,
  max_limit INTEGER NOT NULL,
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id) ON DELETE CASCADE,
  UNIQUE (tenant_id, resource_type, period_start, period_end)
);

CREATE INDEX idx_quotas_tenant_id ON quotas(tenant_id);
CREATE INDEX idx_quotas_period ON quotas(period_start, period_end);
```

### 2.3 Triggers y Funciones

#### Función: Actualizar timestamp
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';
```

#### Triggers para actualizar timestamps
```sql
CREATE TRIGGER update_tenants_updated_at BEFORE UPDATE ON tenants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_clients_updated_at BEFORE UPDATE ON clients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_accounts_updated_at BEFORE UPDATE ON accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_journal_entries_updated_at BEFORE UPDATE ON journal_entries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

#### Función: Verificar balance de asiento
```sql
CREATE OR REPLACE FUNCTION verify_journal_entry_balance()
RETURNS TRIGGER AS $$
DECLARE
    total_debit DECIMAL(15, 2);
    total_credit DECIMAL(15, 2);
BEGIN
    SELECT COALESCE(SUM(amount), 0) INTO total_debit
    FROM journal_entry_lines
    WHERE entry_id = NEW.entry_id AND transaction_type = 'debit';
    
    SELECT COALESCE(SUM(amount), 0) INTO total_credit
    FROM journal_entry_lines
    WHERE entry_id = NEW.entry_id AND transaction_type = 'credit';
    
    NEW.total_debit = total_debit;
    NEW.total_credit = total_credit;
    
    IF ABS(total_debit - total_credit) > 0.01 THEN
        RAISE EXCEPTION 'Journal entry must balance (debit: %, credit: %)', total_debit, total_credit;
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';
```

#### Trigger para verificar balance
```sql
CREATE TRIGGER verify_journal_entry_balance_trigger
    BEFORE INSERT OR UPDATE ON journal_entries
    FOR EACH ROW EXECUTE FUNCTION verify_journal_entry_balance();
```

---

## 3. Conexión desde Cloud Functions

### 3.1 Configuración de Conexión Cloud SQL

```typescript
// functions/src/config/database.ts
import { Pool } from 'pg';
import { SecretManagerServiceClient } from '@google-cloud/secret-manager';

const secretManager = new SecretManagerServiceClient();

async function getDatabaseConfig() {
  const [version] = await secretManager.accessSecretVersion({
    name: `projects/${PROJECT_ID}/secrets/cloud-sql-credentials/versions/latest`,
  });
  
  const credentials = JSON.parse(version.payload.data.toString());
  
  return {
    host: credentials.host,
    port: credentials.port,
    database: credentials.database,
    user: credentials.user,
    password: credentials.password,
  };
}

let pool: Pool | null = null;

export async function getPool(): Promise<Pool> {
  if (!pool) {
    const config = await getDatabaseConfig();
    pool = new Pool({
      ...config,
      max: 20,
      idleTimeoutMillis: 30000,
      connectionTimeoutMillis: 2000,
    });
  }
  return pool;
}
```

### 3.2 Ejemplo de Uso

```typescript
// functions/src/services/transactionService.ts
import { getPool } from '../config/database';

export class TransactionService {
  async createTransaction(data: TransactionData): Promise<Transaction> {
    const pool = await getPool();
    const client = await pool.connect();
    
    try {
      await client.query('BEGIN');
      
      const result = await client.query(
        `INSERT INTO transactions 
         (tenant_id, document_id, client_id, account_id, transaction_type, amount, tax_amount, date, description)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
         RETURNING *`,
        [
          data.tenantId,
          data.documentId,
          data.clientId,
          data.accountId,
          data.transactionType,
          data.amount,
          data.taxAmount,
          data.date,
          data.description,
        ]
      );
      
      await client.query('COMMIT');
      
      return result.rows[0];
    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  }
  
  async getTransactionsByTenant(tenantId: string): Promise<Transaction[]> {
    const pool = await getPool();
    const result = await pool.query(
      'SELECT * FROM transactions WHERE tenant_id = $1 ORDER BY date DESC',
      [tenantId]
    );
    return result.rows;
  }
}
```

---

## 4. Backup y Restore

### 4.1 Configuración de Backup Automático

```bash
# Cloud SQL ya tiene backup automático configurado
# Backup diario a las 2 AM
# Retención de 7 días
```

### 4.2 Backup Manual

```bash
# Exportar base de datos
gcloud sql export sql pinad-postgres \
  --project=pinad-scanning-system \
  --database=pinad_db \
  --gs-uri=gs://pinad-backups/manual-backup-$(date +%Y%m%d).sql
```

### 4.3 Restore desde Backup

```bash
# Importar base de datos
gcloud sql import sql pinad-postgres \
  --project=pinad-scanning-system \
  --database=pinad_db \
  --gs-uri=gs://pinad-backups/manual-backup-20240607.sql
```

---

## 5. Monitoreo y Alertas

### 5.1 Configuración de Monitoreo

```bash
# Habilitar Cloud Monitoring
gcloud services enable monitoring.googleapis.com --project=pinad-scanning-system

# Crear alerta para uso de CPU
gcloud monitoring policies create \
  --project=pinad-scanning-system \
  --policy-from-file=cpu-alert-policy.yaml
```

### 5.2 Política de Alerta (cpu-alert-policy.yaml)
```yaml
displayName: "High CPU Usage Alert"
conditions:
  - displayName: "CPU > 80%"
    conditionThreshold:
      filter: 'resource.type = "cloudsql_database" AND resource.labels.database_id = "pinad-postgres"'
      comparison: COMPARISON_GT
      thresholdValue: 80
      duration: 300s
      aggregations:
        - alignmentPeriod: 60s
          perSeriesAligner: ALIGN_MEAN
          crossSeriesReducer: REDUCE_MEAN
          groupByFields:
            - resource.label.database_id
alertStrategy:
  notificationRateLimit:
    period: 3600s
    count: 1
notificationChannels:
  - projects/pinad-scanning-system/notificationChannels/1
```

---

## 6. Seguridad

### 6.1 Configuración de Secret Manager

```bash
# Crear secreto para credenciales de base de datos
echo '{"host":"localhost","port":5432,"database":"pinad_db","user":"pinad_user","password":"YOUR_PASSWORD"}' | \
  gcloud secrets create cloud-sql-credentials --data-file=- \
  --project=pinad-scanning-system

# Dar acceso a Cloud Functions
gcloud secrets add-iam-policy-binding cloud-sql-credentials \
  --member="serviceAccount:pinad-scanning-system@appspot.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=pinad-scanning-system
```

### 6.2 Configuración de IAM

```bash
# Crear cuenta de servicio para Cloud Functions
gcloud iam service-accounts create pinad-cloud-functions \
  --display-name="PINAD Cloud Functions" \
  --project=pinad-scanning-system

# Asignar roles
gcloud projects add-iam-policy-binding pinad-scanning-system \
  --member="serviceAccount:pinad-cloud-functions@pinad-scanning-system.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding pinad-scanning-system \
  --member="serviceAccount:pinad-cloud-functions@pinad-scanning-system.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding pinad-scanning-system \
  --member="serviceAccount:pinad-cloud-functions@pinad-scanning-system.iam.gserviceaccount.com" \
  --role="roles/firestore.admin"

gcloud projects add-iam-policy-binding pinad-scanning-system \
  --member="serviceAccount:pinad-cloud-functions@pinad-scanning-system.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"
```

---

## 7. Migración de Datos

### 7.1 Script de Migración Inicial

```typescript
// functions/migrations/001_initial_schema.ts
import { getPool } from '../config/database';

export async function up() {
  const pool = await getPool();
  
  // Crear tablas
  await pool.query(`
    CREATE TABLE IF NOT EXISTS tenants (
      tenant_id VARCHAR(255) PRIMARY KEY,
      name VARCHAR(255) NOT NULL,
      rif VARCHAR(50) UNIQUE,
      email VARCHAR(255) UNIQUE NOT NULL,
      phone VARCHAR(50),
      address TEXT,
      plan VARCHAR(50) DEFAULT 'basic',
      max_users INTEGER DEFAULT 5,
      max_documents INTEGER DEFAULT 1000,
      max_storage_gb INTEGER DEFAULT 10,
      current_users INTEGER DEFAULT 0,
      current_documents INTEGER DEFAULT 0,
      current_storage_gb DECIMAL(10, 2) DEFAULT 0,
      is_active BOOLEAN DEFAULT true,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `);
  
  // Crear índices
  await pool.query('CREATE INDEX IF NOT EXISTS idx_tenants_email ON tenants(email)');
  await pool.query('CREATE INDEX IF NOT EXISTS idx_tenants_rif ON tenants(rif)');
  
  console.log('Migration 001 completed');
}

export async function down() {
  const pool = await getPool();
  
  await pool.query('DROP INDEX IF EXISTS idx_tenants_email');
  await pool.query('DROP INDEX IF EXISTS idx_tenants_rif');
  await pool.query('DROP TABLE IF EXISTS tenants');
  
  console.log('Migration 001 rolled back');
}
```

---

## Conclusión

La configuración de base de datos está diseñada para soportar:
- **Multi-tenancy**: Aislamiento completo de datos por tenant
- **Escalabilidad**: Firestore para documentos NoSQL, Cloud SQL para datos estructurados
- **Seguridad**: Secret Manager para credenciales, IAM para permisos
- **Monitoreo**: Cloud Monitoring para alertas y métricas
- **Backup**: Backup automático y manual de Cloud SQL
- **Auditoría**: Audit log para rastrear cambios

Esta configuración soporta la visión de una aplicación web de escaneo en línea con dashboard inteligente y multi-tenancy para vender a otros contadores.
