# Implementación del Motor de Escaneo con OCR en Cloud Functions

## Fecha
Junio 7, 2026

## Objetivo
Implementar el motor de escaneo con OCR utilizando Google Document AI y Vertex AI en Cloud Functions para procesar documentos escaneados desde la aplicación web.

---

## 1. Configuración de Google Document AI

### 1.1 Creación de Procesador Document AI

```bash
# Habilitar Document AI API
gcloud services enable documentai.googleapis.com --project=pinad-scanning-system

# Crear procesador de facturas
gcloud documentai processors create \
  --project=pinad-scanning-system \
  --location=us \
  --display-name="PINAD Invoice Processor" \
  --type="INVOICE_PROCESSOR"

# Obtener el ID del procesador
gcloud documentai processors list \
  --project=pinad-scanning-system \
  --location=us
```

### 1.2 Configuración de Vertex AI

```bash
# Habilitar Vertex AI API
gcloud services enable aiplatform.googleapis.com --project=pinad-scanning-system

# Crear endpoint para extracción de datos
gcloud ai endpoints create \
  --project=pinad-scanning-system \
  --region=us-central1 \
  --display-name="PINAD Data Extraction"
```

---

## 2. Estructura de Cloud Functions

```
functions/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts
│   ├── config/
│   │   ├── documentAI.ts
│   │   ├── vertexAI.ts
│   │   └── storage.ts
│   ├── services/
│   │   ├── documentService.ts
│   │   ├── ocrService.ts
│   │   ├── extractionService.ts
│   │   └── databaseService.ts
│   ├── types/
│   │   ├── document.ts
│   │   ├── extraction.ts
│   │   └── database.ts
│   └── middleware/
│       ├── auth.ts
│       └── validation.ts
└── test/
    ├── unit/
    └── integration/
```

---

## 3. Implementación de Cloud Functions

### 3.1 package.json

```json
{
  "name": "pinad-cloud-functions",
  "version": "1.0.0",
  "description": "Cloud Functions for PINAD Scanning System",
  "main": "lib/index.js",
  "scripts": {
    "build": "tsc",
    "serve": "npm run build && firebase emulators:start --only functions",
    "shell": "npm run build && firebase functions:shell",
    "start": "npm run shell",
    "deploy": "firebase deploy --only functions",
    "logs": "firebase functions:log"
  },
  "engines": {
    "node": "18"
  },
  "dependencies": {
    "@google-cloud/documentai": "^5.0.0",
    "@google-cloud/vertexai": "^0.1.0",
    "@google-cloud/storage": "^7.0.0",
    "@google-cloud/firestore": "^7.0.0",
    "@google-cloud/secret-manager": "^5.0.0",
    "firebase-admin": "^12.0.0",
    "firebase-functions": "^4.0.0",
    "pg": "^8.11.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0",
    "firebase-functions-test": "^3.0.0"
  }
}
```

### 3.2 Configuración de Document AI

```typescript
// functions/src/config/documentAI.ts
import { DocumentProcessorServiceClient } from '@google-cloud/documentai';

const PROJECT_ID = process.env.PROJECT_ID || 'pinad-scanning-system';
const LOCATION = 'us';
const PROCESSOR_ID = process.env.DOCUMENT_AI_PROCESSOR_ID || 'YOUR_PROCESSOR_ID';

const client = new DocumentProcessorServiceClient();

export async function processDocumentWithDocumentAI(
  fileBuffer: Buffer,
  mimeType: string
): Promise<any> {
  const name = `projects/${PROJECT_ID}/locations/${LOCATION}/processors/${PROCESSOR_ID}`;

  const request = {
    name,
    rawDocument: {
      content: fileBuffer,
      mimeType,
    },
  };

  const [result] = await client.processDocument(request);
  return result.document;
}

export function extractFieldsFromDocument(document: any): ExtractedData {
  const entities = document.entities || [];
  
  const extractedData: ExtractedData = {
    invoiceNumber: '',
    date: '',
    amount: 0,
    taxAmount: 0,
    currency: 'VES',
    vendor: {
      name: '',
      rif: '',
      address: '',
    },
    items: [],
    paymentMethod: '',
    paymentTerms: '',
  };

  // Extraer campos específicos
  entities.forEach((entity: any) => {
    const type = entity.type;
    const text = entity.mentionText;

    switch (type) {
      case 'invoice_number':
        extractedData.invoiceNumber = text;
        break;
      case 'invoice_date':
        extractedData.date = text;
        break;
      case 'total_amount':
        extractedData.amount = parseFloat(text.replace(/[^0-9.-]+/g, ''));
        break;
      case 'tax_amount':
        extractedData.taxAmount = parseFloat(text.replace(/[^0-9.-]+/g, ''));
        break;
      case 'vendor_name':
        extractedData.vendor.name = text;
        break;
      case 'vendor_rif':
        extractedData.vendor.rif = text;
        break;
      case 'payment_method':
        extractedData.paymentMethod = text;
        break;
      case 'payment_terms':
        extractedData.paymentTerms = text;
        break;
    }
  });

  // Extraer items de líneas
  const pageBlocks = document.pages?.[0]?.blocks || [];
  pageBlocks.forEach((block: any) => {
    if (block.layout?.textAnchor?.textSegments) {
      const text = block.layout.textAnchor.textSegments
        .map((seg: any) => seg.text || '')
        .join(' ');
      
      // Detectar patrones de items
      const itemPattern = /(\d+)\s+(.+?)\s+(\d+)\s+(\d+\.?\d*)\s+(\d+\.?\d*)/;
      const match = text.match(itemPattern);
      
      if (match) {
        extractedData.items.push({
          name: match[2],
          quantity: parseInt(match[3]),
          unitPrice: parseFloat(match[4]),
          totalPrice: parseFloat(match[5]),
          taxRate: 0,
        });
      }
    }
  });

  return extractedData;
}
```

### 3.3 Configuración de Vertex AI

```typescript
// functions/src/config/vertexAI.ts
import { VertexAI } from '@google-cloud/vertexai';

const PROJECT_ID = process.env.PROJECT_ID || 'pinad-scanning-system';
const LOCATION = 'us-central1';

const vertexAI = new VertexAI({ project: PROJECT_ID, location: LOCATION });

export async function extractDataWithVertexAI(
  document: any
): Promise<EnhancedExtractedData> {
  const model = vertexAI.getGenerativeModel({
    model: 'gemini-pro-vision',
  });

  const prompt = `
    Extrae la siguiente información de este documento:
    - Número de factura
    - Fecha de emisión
    - Monto total
    - Monto de impuesto
    - Nombre del proveedor
    - RIF del proveedor
    - Método de pago
    - Términos de pago
    - Items (nombre, cantidad, precio unitario, precio total)
    
    Responde en formato JSON.
  `;

  const imagePart = {
    inlineData: {
      data: document.content,
      mimeType: document.mimeType,
    },
  };

  const result = await model.generateContent([prompt, imagePart]);
  const response = result.response;
  const text = response.candidates?.[0]?.content?.parts?.[0]?.text || '';

  // Parsear JSON
  const extractedData = JSON.parse(text);
  
  return {
    ...extractedData,
    confidence: 0.95,
    processingTime: Date.now(),
  };
}
```

### 3.4 Servicio de Documentos

```typescript
// functions/src/services/documentService.ts
import * as admin from 'firebase-admin';
import { Storage } from '@google-cloud/storage';
import { processDocumentWithDocumentAI, extractFieldsFromDocument } from '../config/documentAI';
import { extractDataWithVertexAI } from '../config/vertexAI';

const storage = new Storage();
const db = admin.firestore();

export class DocumentService {
  async uploadDocument(
    tenantId: string,
    userId: string,
    fileBuffer: Buffer,
    fileName: string,
    mimeType: string
  ): Promise<string> {
    const bucket = storage.bucket('pinad-documents');
    const filePath = `tenants/${tenantId}/users/${userId}/${Date.now()}_${fileName}`;
    const file = bucket.file(filePath);

    await file.save(fileBuffer, {
      contentType: mimeType,
    });

    // Crear registro en Firestore
    const docRef = await db.collection('documents').add({
      tenantId,
      userId,
      fileName,
      storagePath: filePath,
      fileSize: fileBuffer.length,
      mimeType,
      status: 'uploaded',
      createdAt: admin.firestore.FieldValue.serverTimestamp(),
    });

    return docRef.id;
  }

  async processDocument(documentId: string): Promise<void> {
    const docRef = db.collection('documents').doc(documentId);
    const doc = await docRef.get();

    if (!doc.exists) {
      throw new Error('Document not found');
    }

    const data = doc.data() as any;

    // Actualizar estado a processing
    await docRef.update({
      status: 'processing',
      processingStartedAt: admin.firestore.FieldValue.serverTimestamp(),
    });

    try {
      // Descargar archivo de Cloud Storage
      const bucket = storage.bucket('pinad-documents');
      const file = bucket.file(data.storagePath);
      const [fileBuffer] = await file.download();

      // Procesar con Document AI
      const documentAIResult = await processDocumentWithDocumentAI(
        fileBuffer,
        data.mimeType
      );

      // Extraer campos con Document AI
      const extractedData = extractFieldsFromDocument(documentAIResult);

      // Mejorar extracción con Vertex AI
      const enhancedData = await extractDataWithVertexAI({
        content: fileBuffer.toString('base64'),
        mimeType: data.mimeType,
      });

      // Combinar datos
      const finalExtractedData = {
        ...extractedData,
        ...enhancedData,
        confidence: Math.max(extractedData.confidence || 0.8, enhancedData.confidence || 0.8),
      };

      // Actualizar documento
      await docRef.update({
        status: 'processed',
        extractedData: finalExtractedData,
        processedAt: admin.firestore.FieldValue.serverTimestamp(),
        processingMetadata: {
          processorId: 'document-ai-vertex-ai',
          processingTime: Date.now(),
          confidence: finalExtractedData.confidence,
          errors: [],
        },
      });

      // Guardar en Cloud SQL
      await this.saveToCloudSQL(data.tenantId, finalExtractedData);

      // Enviar notificación
      await this.sendNotification(data.userId, data.tenantId, 'document_processed', {
        documentId,
        fileName: data.fileName,
      });

    } catch (error) {
      await docRef.update({
        status: 'failed',
        processingMetadata: {
          processorId: 'document-ai-vertex-ai',
          processingTime: Date.now(),
          confidence: 0,
          errors: [error.message],
        },
      });

      // Enviar notificación de error
      await this.sendNotification(data.userId, data.tenantId, 'document_failed', {
        documentId,
        fileName: data.fileName,
        error: error.message,
      });

      throw error;
    }
  }

  private async saveToCloudSQL(
    tenantId: string,
    extractedData: any
  ): Promise<void> {
    // Implementar guardado en Cloud SQL
    // Esto se conectará a la base de datos PostgreSQL
    // para guardar transacciones contables
  }

  private async sendNotification(
    userId: string,
    tenantId: string,
    type: string,
    data: any
  ): Promise<void> {
    await db.collection('notifications').add({
      tenantId,
      userId,
      type,
      title: type === 'document_processed' ? 'Documento Procesado' : 'Error en Procesamiento',
      message: type === 'document_processed' 
        ? `El documento ${data.fileName} ha sido procesado exitosamente`
        : `Error al procesar el documento ${data.fileName}: ${data.error}`,
      data,
      isRead: false,
      createdAt: admin.firestore.FieldValue.serverTimestamp(),
    });
  }
}
```

### 3.5 Cloud Function: uploadDocument

```typescript
// functions/src/index.ts
import * as functions from 'firebase-functions';
import * as admin from 'firebase-admin';
import { DocumentService } from './services/documentService';

admin.initializeApp();
const documentService = new DocumentService();

export const uploadDocument = functions.https.onCall(async (data, context) => {
  // Validar autenticación
  if (!context.auth) {
    throw new functions.https.HttpsError(
      'unauthenticated',
      'User must be authenticated'
    );
  }

  const { tenantId, fileData, fileName, mimeType } = data;
  const userId = context.auth.uid;

  // Validar tenant
  const userDoc = await admin.firestore().collection('users').doc(userId).get();
  if (!userDoc.exists || userDoc.data()?.tenantId !== tenantId) {
    throw new functions.https.HttpsError(
      'permission-denied',
      'User does not have access to this tenant'
    );
  }

  // Validar cuota
  const quota = await checkDocumentQuota(tenantId);
  if (!quota.canUpload) {
    throw new functions.https.HttpsError(
      'resource-exhausted',
      'Document quota exceeded'
    );
  }

  try {
    const fileBuffer = Buffer.from(fileData, 'base64');
    const documentId = await documentService.uploadDocument(
      tenantId,
      userId,
      fileBuffer,
      fileName,
      mimeType
    );

    return { documentId, status: 'uploaded' };
  } catch (error) {
    throw new functions.https.HttpsError(
      'internal',
      error.message
    );
  }
});

async function checkDocumentQuota(tenantId: string): Promise<{ canUpload: boolean }> {
  // Implementar verificación de cuota
  return { canUpload: true };
}
```

### 3.6 Cloud Function: processDocument (Trigger)

```typescript
export const processDocument = functions.firestore
  .document('documents/{documentId}')
  .onWrite(async (change, context) => {
    const document = change.after.data();

    // Solo procesar documentos nuevos o con estado 'uploaded'
    if (!document || document.status !== 'uploaded') {
      return null;
    }

    try {
      await documentService.processDocument(context.params.documentId);
      return null;
    } catch (error) {
      console.error('Error processing document:', error);
      return null;
    }
  });
```

### 3.7 Cloud Function: getDocuments

```typescript
export const getDocuments = functions.https.onCall(async (data, context) => {
  if (!context.auth) {
    throw new functions.https.HttpsError(
      'unauthenticated',
      'User must be authenticated'
    );
  }

  const { tenantId, userId, limit = 50, status } = data;

  let query = admin
    .firestore()
    .collection('documents')
    .where('tenantId', '==', tenantId)
    .where('userId', '==', userId)
    .orderBy('createdAt', 'desc')
    .limit(limit);

  if (status) {
    query = query.where('status', '==', status);
  }

  const snapshot = await query.get();
  const documents = snapshot.docs.map(doc => ({
    id: doc.id,
    ...doc.data(),
  }));

  return { documents };
});
```

### 3.8 Cloud Function: getDashboardData

```typescript
export const getDashboardData = functions.https.onCall(async (data, context) => {
  if (!context.auth) {
    throw new functions.https.HttpsError(
      'unauthenticated',
      'User must be authenticated'
    );
  }

  const { tenantId, userId } = data;

  // Obtener documentos
  const documentsSnapshot = await admin
    .firestore()
    .collection('documents')
    .where('tenantId', '==', tenantId)
    .where('userId', '==', userId)
    .orderBy('createdAt', 'desc')
    .limit(50)
    .get();

  const documents = documentsSnapshot.docs.map(doc => ({
    id: doc.id,
    ...doc.data(),
  }));

  // Calcular métricas
  const metrics = {
    totalDocuments: documents.length,
    processedDocuments: documents.filter((d: any) => d.status === 'processed').length,
    failedDocuments: documents.filter((d: any) => d.status === 'failed').length,
    pendingDocuments: documents.filter((d: any) => d.status === 'uploaded' || d.status === 'processing').length,
    totalAmount: documents.reduce((sum: number, d: any) => {
      return sum + (d.extractedData?.amount || 0);
    }, 0),
  };

  return { documents, metrics };
});
```

---

## 4. Configuración de IAM

```bash
# Crear cuenta de servicio para Cloud Functions
gcloud iam service-accounts create pinad-ocr-functions \
  --display-name="PINAD OCR Functions" \
  --project=pinad-scanning-system

# Asignar roles
gcloud projects add-iam-policy-binding pinad-scanning-system \
  --member="serviceAccount:pinad-ocr-functions@pinad-scanning-system.iam.gserviceaccount.com" \
  --role="roles/documentai.processor"

gcloud projects add-iam-policy-binding pinad-scanning-system \
  --member="serviceAccount:pinad-ocr-functions@pinad-scanning-system.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding pinad-scanning-system \
  --member="serviceAccount:pinad-ocr-functions@pinad-scanning-system.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding pinad-scanning-system \
  --member="serviceAccount:pinad-ocr-functions@pinad-scanning-system.iam.gserviceaccount.com" \
  --role="roles/datastore.user"
```

---

## 5. Despliegue

```bash
# Construir
npm run build

# Desplegar
firebase deploy --only functions

# Ver logs
firebase functions:log
```

---

## 6. Testing

### 6.1 Testing Unitario

```typescript
// functions/test/unit/documentService.test.ts
import { DocumentService } from '../../src/services/documentService';

describe('DocumentService', () => {
  let documentService: DocumentService;

  beforeEach(() => {
    documentService = new DocumentService();
  });

  test('should upload document successfully', async () => {
    const fileBuffer = Buffer.from('test content');
    const documentId = await documentService.uploadDocument(
      'tenant-1',
      'user-1',
      fileBuffer,
      'test.pdf',
      'application/pdf'
    );

    expect(documentId).toBeDefined();
  });
});
```

### 6.2 Testing de Integración

```typescript
// functions/test/integration/ocrFlow.test.ts
import { processDocument } from '../../src/index';

describe('OCR Flow Integration', () => {
  test('should process document end-to-end', async () => {
    // Simular subida de documento
    const documentId = 'test-document-id';
    
    // Procesar documento
    await processDocument({
      after: {
        data: {
          tenantId: 'tenant-1',
          userId: 'user-1',
          storagePath: 'test/path.pdf',
          status: 'uploaded',
        },
      },
    }, { params: { documentId } });

    // Verificar resultado
    const doc = await admin.firestore().collection('documents').doc(documentId).get();
    expect(doc.data()?.status).toBe('processed');
  });
});
```

---

## 7. Monitoreo y Logging

```typescript
// functions/src/middleware/logging.ts
import * as functions from 'firebase-functions';

export function logFunctionCall(
  functionName: string,
  data: any
): void {
  functions.logger.log(`${functionName} called with:`, data);
}

export function logError(
  functionName: string,
  error: Error
): void {
  functions.logger.error(`${functionName} error:`, error);
}
```

---

## 8. Optimizaciones

### 8.1 Caching

```typescript
import * as functions from 'firebase-functions';

export const getDocumentWithCache = functions.https.onCall(async (data, context) => {
  const { documentId } = data;
  const cacheKey = `document_${documentId}`;
  
  // Verificar cache
  const cached = await getFromCache(cacheKey);
  if (cached) {
    return cached;
  }
  
  // Obtener de Firestore
  const doc = await admin.firestore().collection('documents').doc(documentId).get();
  
  // Guardar en cache
  await setCache(cacheKey, doc.data(), 300); // 5 minutos
  
  return doc.data();
});
```

### 8.2 Procesamiento Asíncrono

```typescript
export const processDocumentAsync = functions.https.onCall(async (data, context) => {
  const { documentId } = data;
  
  // Iniciar procesamiento en background
  processDocumentInBackground(documentId);
  
  return { status: 'processing_started' };
});

async function processDocumentInBackground(documentId: string): Promise<void> {
  // Procesar sin bloquear la respuesta
  await documentService.processDocument(documentId);
}
```

---

## Conclusión

El motor de escaneo con OCR está implementado utilizando:
- **Google Document AI**: Para procesamiento OCR básico
- **Vertex AI**: Para extracción inteligente de datos
- **Cloud Functions**: Para backend serverless
- **Firestore**: Para almacenamiento de documentos
- **Cloud Storage**: Para almacenamiento de archivos

Esta implementación soporta la visión de una aplicación web de escaneo en línea con procesamiento automático de documentos y extracción de datos contables.
