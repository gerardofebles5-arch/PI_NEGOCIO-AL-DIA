# Arquitectura de Agentes de IA Independientes (Visión Futura)

## Fecha
Junio 7, 2026

## Objetivo
Diseñar una arquitectura de agentes de IA independientes donde cada proceso contable sea un agente autónomo, permitiendo cambios en el registro de ventas sin conflictos en el sistema, con modularidad completa y orquestación de procesos.

---

## 1. Visión General de la Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                    Orquestador de Agentes                        │
│  - Coordinar ejecución de agentes                              │
│  - Manejar dependencias entre agentes                          │
│  - Gestionar estado de procesos                                │
│  - Recuperación de errores                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Event Bus
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    Bus de Mensajes (Pub/Sub)                      │
│  - document.uploaded                                           │
│  - document.processed                                          │
│  - transaction.created                                         │
│  - transaction.updated                                         │
│  - invoice.verified                                            │
│  - report.generated                                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ Agente OCR    │     │ Agente        │     │ Agente       │
│               │     │ Extracción    │     │ Validación   │
│ - Procesar    │     │ - Extraer     │     │ - Validar    │
│   documentos  │     │   datos       │     │   datos      │
│ - Clasificar  │     │ - Normalizar  │     │ - Verificar  │
│   tipos       │     │ - Enrich      │     │   reglas     │
└───────────────┘     └───────────────┘     └───────────────┘
        │                     │                     │
        │                     │                     │
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ Agente        │     │ Agente        │     │ Agente       │
│ Clasificación │     │ Contabilidad  │     │ Reportes     │
│ - Clasificar  │     │ - Crear       │     │ - Generar    │
│   transacciones│    │   asientos    │     │   reportes   │
│ - Asignar     │     │ - Actualizar  │     │ - Calcular   │
│   categorías  │     │   balances    │     │   métricas   │
└───────────────┘     └───────────────┘     └───────────────┘
        │                     │                     │
        │                     │                     │
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ Agente        │     │ Agente        │     │ Agente       │
│ Anomalías     │     │ Predicción    │     │ Notificación │
│ - Detectar    │     │ - Predecir    │     │ - Enviar     │
│   anomalías   │     │   gastos      │     │   alertas    │
│ - Alertar     │     │ - Proyectar   │     │ - Notificar  │
│   riesgos     │     │   ingresos    │     │   usuarios   │
└───────────────┘     └───────────────┘     └───────────────┘
```

---

## 2. Principios de Diseño

### 2.1 Independencia de Agentes
- Cada agente es un microservicio independiente
- Los agentes se comunican a través de eventos (Pub/Sub)
- No hay dependencias directas entre agentes
- Cada agente tiene su propia base de datos o esquema

### 2.2 Modularidad
- Cada agente tiene una responsabilidad única
- Los agentes pueden ser agregados o removidos sin afectar otros
- Los agentes pueden ser actualizados independientemente
- Los agentes pueden ser escalados individualmente

### 2.3 Consistencia Eventual
- Los agentes trabajan con consistencia eventual
- Los eventos aseguran que todos los agentes estén sincronizados
- Los agentes pueden reprocesar eventos si es necesario
- Los agentes pueden manejar eventos fuera de orden

### 2.4 Resiliencia
- Los agentes pueden fallar sin afectar el sistema completo
- Los agentes pueden recuperarse automáticamente
- Los agentes tienen retry y backoff
- Los agentes tienen dead letter queues para eventos fallidos

---

## 3. Arquitectura Detallada

### 3.1 Orquestador de Agentes

```typescript
// agents/orchestrator/src/orchestrator.ts
import { PubSub } from '@google-cloud/pubsub';

export class AgentOrchestrator {
  private pubsub: PubSub;
  private agentRegistry: Map<string, Agent>;

  constructor() {
    this.pubsub = new PubSub();
    this.agentRegistry = new Map();
    this.registerAgents();
  }

  private registerAgents(): void {
    this.registerAgent(new OcrAgent());
    this.registerAgent(new ExtractionAgent());
    this.registerAgent(new ValidationAgent());
    this.registerAgent(new ClassificationAgent());
    this.registerAgent(new AccountingAgent());
    this.registerAgent(new ReportingAgent());
    this.registerAgent(new AnomalyDetectionAgent());
    this.registerAgent(new PredictionAgent());
    this.registerAgent(new NotificationAgent());
  }

  private registerAgent(agent: Agent): void {
    this.agentRegistry.set(agent.getName(), agent);
    agent.initialize(this.pubsub);
  }

  async orchestrateWorkflow(workflow: Workflow): Promise<void> {
    const steps = workflow.getSteps();
    
    for (const step of steps) {
      const agent = this.agentRegistry.get(step.agentName);
      
      if (!agent) {
        throw new Error(`Agent ${step.agentName} not found`);
      }

      try {
        await agent.execute(step.input);
      } catch (error) {
        await this.handleWorkflowError(workflow, step, error);
        throw error;
      }
    }
  }

  private async handleWorkflowError(
    workflow: Workflow,
    step: WorkflowStep,
    error: Error
  ): Promise<void> {
    // Publicar evento de error
    await this.pubsub.topic('workflow.errors').publishJSON({
      workflowId: workflow.getId(),
      step: step.name,
      error: error.message,
      timestamp: new Date().toISOString(),
    });

    // Ejecutar estrategia de recuperación
    const recoveryStrategy = step.recoveryStrategy || 'retry';
    
    switch (recoveryStrategy) {
      case 'retry':
        await this.retryStep(workflow, step);
        break;
      case 'skip':
        await this.skipStep(workflow, step);
        break;
      case 'abort':
        await this.abortWorkflow(workflow);
        break;
    }
  }

  private async retryStep(workflow: Workflow, step: WorkflowStep): Promise<void> {
    const agent = this.agentRegistry.get(step.agentName);
    await agent.execute(step.input);
  }

  private async skipStep(workflow: Workflow, step: WorkflowStep): Promise<void> {
    // Marcar paso como saltado
    await workflow.markStepAsSkipped(step.name);
  }

  private async abortWorkflow(workflow: Workflow): Promise<void> {
    await workflow.abort();
  }
}
```

### 3.2 Agente Base

```typescript
// agents/common/src/agent.ts
import { PubSub } from '@google-cloud/pubsub';

export abstract class Agent {
  protected pubsub: PubSub;
  protected subscriptions: Map<string, any>;

  constructor() {
    this.pubsub = new PubSub();
    this.subscriptions = new Map();
  }

  abstract getName(): string;
  abstract execute(input: any): Promise<any>;

  async initialize(pubsub: PubSub): Promise<void> {
    this.pubsub = pubsub;
    await this.subscribeToTopics();
  }

  protected abstract subscribeToTopics(): Promise<void>;

  protected async publishEvent(topic: string, data: any): Promise<void> {
    await this.pubsub.topic(topic).publishJSON({
      ...data,
      timestamp: new Date().toISOString(),
      agent: this.getName(),
    });
  }

  protected async handleEvent(message: any): Promise<void> {
    try {
      await this.execute(message.data);
      message.ack();
    } catch (error) {
      console.error(`Error in agent ${this.getName()}:`, error);
      message.nack();
    }
  }
}
```

### 3.3 Agente OCR

```typescript
// agents/ocr-agent/src/ocrAgent.ts
import { Agent } from '../../common/src/agent';
import { DocumentProcessorServiceClient } from '@google-cloud/documentai';

export class OcrAgent extends Agent {
  private documentAI: DocumentProcessorServiceClient;

  constructor() {
    super();
    this.documentAI = new DocumentProcessorServiceClient();
  }

  getName(): string {
    return 'ocr-agent';
  }

  async execute(input: any): Promise<any> {
    const { documentId, storagePath, mimeType } = input;

    console.log(`Processing document ${documentId} with OCR`);

    // Descargar documento
    const fileBuffer = await this.downloadFromStorage(storagePath);

    // Procesar con Document AI
    const result = await this.documentAI.processDocument({
      name: `projects/${PROJECT_ID}/locations/us/processors/PROCESSOR_ID`,
      rawDocument: {
        content: fileBuffer,
        mimeType,
      },
    });

    const document = result.document;

    // Clasificar tipo de documento
    const documentType = this.classifyDocumentType(document);

    // Publicar evento de documento procesado
    await this.publishEvent('document.processed', {
      documentId,
      documentType,
      ocrResult: document,
    });

    return {
      documentId,
      documentType,
      ocrResult: document,
    };
  }

  protected async subscribeToTopics(): Promise<void> {
    const subscription = await this.pubsub
      .topic('document.uploaded')
      .subscription('ocr-agent-subscription');

    subscription.on('message', (message) => this.handleEvent(message));
    this.subscriptions.set('document.uploaded', subscription);
  }

  private classifyDocumentType(document: any): string {
    const entities = document.entities || [];
    
    if (entities.some((e: any) => e.type === 'invoice_number')) {
      return 'invoice';
    } else if (entities.some((e: any) => e.type === 'receipt_number')) {
      return 'receipt';
    } else if (entities.some((e: any) => e.type === 'contract_date')) {
      return 'contract';
    }
    
    return 'other';
  }

  private async downloadFromStorage(storagePath: string): Promise<Buffer> {
    // Implementar descarga de Cloud Storage
    return Buffer.from('');
  }
}
```

### 3.4 Agente de Extracción

```typescript
// agents/extraction-agent/src/extractionAgent.ts
import { Agent } from '../../common/src/agent';
import { VertexAI } from '@google-cloud/vertexai';

export class ExtractionAgent extends Agent {
  private vertexAI: VertexAI;

  constructor() {
    super();
    this.vertexAI = new VertexAI({ project: PROJECT_ID, location: 'us-central1' });
  }

  getName(): string {
    return 'extraction-agent';
  }

  async execute(input: any): Promise<any> {
    const { documentId, ocrResult, documentType } = input;

    console.log(`Extracting data from document ${documentId}`);

    const model = this.vertexAI.getGenerativeModel({
      model: 'gemini-pro-vision',
    });

    const prompt = this.getExtractionPrompt(documentType);

    const extractedData = await this.extractWithModel(model, prompt, ocrResult);

    // Normalizar datos
    const normalizedData = this.normalizeData(extractedData, documentType);

    // Publicar evento de datos extraídos
    await this.publishEvent('data.extracted', {
      documentId,
      documentType,
      extractedData: normalizedData,
    });

    return {
      documentId,
      extractedData: normalizedData,
    };
  }

  protected async subscribeToTopics(): Promise<void> {
    const subscription = await this.pubsub
      .topic('document.processed')
      .subscription('extraction-agent-subscription');

    subscription.on('message', (message) => this.handleEvent(message));
    this.subscriptions.set('document.processed', subscription);
  }

  private getExtractionPrompt(documentType: string): string {
    switch (documentType) {
      case 'invoice':
        return `
          Extrae la siguiente información de esta factura:
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
      case 'receipt':
        return `
          Extrae la siguiente información de este recibo:
          - Número de recibo
          - Fecha de emisión
          - Monto total
          - Nombre del establecimiento
          - Items (nombre, cantidad, precio unitario, precio total)
          
          Responde en formato JSON.
        `;
      default:
        return `
          Extrae toda la información relevante de este documento.
          Responde en formato JSON.
        `;
    }
  }

  private async extractWithModel(
    model: any,
    prompt: string,
    ocrResult: any
  ): Promise<any> {
    const result = await model.generateContent([prompt, ocrResult]);
    const response = result.response;
    const text = response.candidates?.[0]?.content?.parts?.[0]?.text || '';
    return JSON.parse(text);
  }

  private normalizeData(data: any, documentType: string): any {
    // Implementar normalización de datos
    return {
      ...data,
      normalized: true,
      documentType,
    };
  }
}
```

### 3.5 Agente de Validación

```typescript
// agents/validation-agent/src/validationAgent.ts
import { Agent } from '../../common/src/agent';

export class ValidationAgent extends Agent {
  private validationRules: Map<string, ValidationRule[]>;

  constructor() {
    super();
    this.validationRules = new Map();
    this.loadValidationRules();
  }

  getName(): string {
    return 'validation-agent';
  }

  async execute(input: any): Promise<any> {
    const { documentId, extractedData, documentType } = input;

    console.log(`Validating data from document ${documentId}`);

    const rules = this.validationRules.get(documentType) || [];
    const validationResults: ValidationResult[] = [];

    for (const rule of rules) {
      const result = await rule.validate(extractedData);
      validationResults.push(result);
    }

    const isValid = validationResults.every(r => r.isValid);

    // Publicar evento de validación
    await this.publishEvent('data.validated', {
      documentId,
      isValid,
      validationResults,
    });

    if (!isValid) {
      await this.publishEvent('validation.failed', {
        documentId,
        validationResults,
      });
    }

    return {
      documentId,
      isValid,
      validationResults,
    };
  }

  protected async subscribeToTopics(): Promise<void> {
    const subscription = await this.pubsub
      .topic('data.extracted')
      .subscription('validation-agent-subscription');

    subscription.on('message', (message) => this.handleEvent(message));
    this.subscriptions.set('data.extracted', subscription);
  }

  private loadValidationRules(): void {
    this.validationRules.set('invoice', [
      new RequiredFieldRule('invoiceNumber'),
      new RequiredFieldRule('date'),
      new RequiredFieldRule('amount'),
      new ValidDateRule('date'),
      new PositiveAmountRule('amount'),
      new ValidRifRule('vendor.rif'),
    ]);

    this.validationRules.set('receipt', [
      new RequiredFieldRule('receiptNumber'),
      new RequiredFieldRule('date'),
      new RequiredFieldRule('amount'),
      new ValidDateRule('date'),
      new PositiveAmountRule('amount'),
    ]);
  }
}

interface ValidationRule {
  validate(data: any): Promise<ValidationResult>;
}

class RequiredFieldRule implements ValidationRule {
  constructor(private fieldName: string) {}

  async validate(data: any): Promise<ValidationResult> {
    const value = this.getFieldValue(data, this.fieldName);
    const isValid = value !== null && value !== undefined && value !== '';

    return {
      rule: `required_field_${this.fieldName}`,
      isValid,
      message: isValid ? '' : `Field ${this.fieldName} is required`,
    };
  }

  private getFieldValue(data: any, path: string): any {
    return path.split('.').reduce((obj, key) => obj?.[key], data);
  }
}

class ValidDateRule implements ValidationRule {
  constructor(private fieldName: string) {}

  async validate(data: any): Promise<ValidationResult> {
    const value = this.getFieldValue(data, this.fieldName);
    const isValid = !isNaN(Date.parse(value));

    return {
      rule: `valid_date_${this.fieldName}`,
      isValid,
      message: isValid ? '' : `Field ${this.fieldName} is not a valid date`,
    };
  }

  private getFieldValue(data: any, path: string): any {
    return path.split('.').reduce((obj, key) => obj?.[key], data);
  }
}

class PositiveAmountRule implements ValidationRule {
  constructor(private fieldName: string) {}

  async validate(data: any): Promise<ValidationResult> {
    const value = this.getFieldValue(data, this.fieldName);
    const isValid = value > 0;

    return {
      rule: `positive_amount_${this.fieldName}`,
      isValid,
      message: isValid ? '' : `Field ${this.fieldName} must be positive`,
    };
  }

  private getFieldValue(data: any, path: string): any {
    return path.split('.').reduce((obj, key) => obj?.[key], data);
  }
}

class ValidRifRule implements ValidationRule {
  constructor(private fieldName: string) {}

  async validate(data: any): Promise<ValidationResult> {
    const value = this.getFieldValue(data, this.fieldName);
    const rifRegex = /^[VEJPG]-\d{9}-\d$/;
    const isValid = rifRegex.test(value);

    return {
      rule: `valid_rif_${this.fieldName}`,
      isValid,
      message: isValid ? '' : `Field ${this.fieldName} is not a valid RIF`,
    };
  }

  private getFieldValue(data: any, path: string): any {
    return path.split('.').reduce((obj, key) => obj?.[key], data);
  }
}
```

### 3.6 Agente de Contabilidad

```typescript
// agents/accounting-agent/src/accountingAgent.ts
import { Agent } from '../../common/src/agent';
import { getPool } from '../config/database';

export class AccountingAgent extends Agent {
  getName(): string {
    return 'accounting-agent';
  }

  async execute(input: any): Promise<any> {
    const { documentId, extractedData, isValid, tenantId } = input;

    if (!isValid) {
      console.log(`Skipping accounting for invalid document ${documentId}`);
      return { documentId, skipped: true };
    }

    console.log(`Creating accounting entries for document ${documentId}`);

    const pool = await getPool();
    const client = await pool.connect();

    try {
      await client.query('BEGIN');

      // Crear transacción
      const transactionId = await this.createTransaction(client, tenantId, extractedData);

      // Crear asiento contable
      const entryId = await this.createJournalEntry(client, tenantId, extractedData);

      // Crear líneas del asiento
      await this.createJournalEntryLines(client, entryId, extractedData);

      await client.query('COMMIT');

      // Publicar evento de transacción creada
      await this.publishEvent('transaction.created', {
        documentId,
        transactionId,
        entryId,
        tenantId,
      });

      return {
        documentId,
        transactionId,
        entryId,
      };
    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  }

  protected async subscribeToTopics(): Promise<void> {
    const subscription = await this.pubsub
      .topic('data.validated')
      .subscription('accounting-agent-subscription');

    subscription.on('message', (message) => this.handleEvent(message));
    this.subscriptions.set('data.validated', subscription);
  }

  private async createTransaction(
    client: any,
    tenantId: string,
    extractedData: any
  ): Promise<number> {
    const result = await client.query(
      `INSERT INTO transactions (tenant_id, document_id, type, amount, tax_amount, date, description)
       VALUES ($1, $2, $3, $4, $5, $6, $7)
       RETURNING transaction_id`,
      [
        tenantId,
        extractedData.documentId,
        'expense',
        extractedData.amount,
        extractedData.taxAmount,
        extractedData.date,
        `Factura ${extractedData.invoiceNumber} - ${extractedData.vendor.name}`,
      ]
    );

    return result.rows[0].transaction_id;
  }

  private async createJournalEntry(
    client: any,
    tenantId: string,
    extractedData: any
  ): Promise<number> {
    const entryNumber = await this.generateEntryNumber(client, tenantId);

    const result = await client.query(
      `INSERT INTO journal_entries (tenant_id, entry_number, entry_date, description, status)
       VALUES ($1, $2, $3, $4, 'posted')
       RETURNING entry_id`,
      [
        tenantId,
        entryNumber,
        extractedData.date,
        `Factura ${extractedData.invoiceNumber} - ${extractedData.vendor.name}`,
      ]
    );

    return result.rows[0].entry_id;
  }

  private async createJournalEntryLines(
    client: any,
    entryId: number,
    extractedData: any
  ): Promise<void> {
    // Línea de débito (Gasto)
    await client.query(
      `INSERT INTO journal_entry_lines (entry_id, account_id, transaction_type, amount)
       VALUES ($1, (SELECT account_id FROM accounts WHERE account_code = '6.1.1.01'), 'debit', $2)`,
      [entryId, extractedData.amount]
    );

    // Línea de crédito (IVA por pagar)
    if (extractedData.taxAmount > 0) {
      await client.query(
        `INSERT INTO journal_entry_lines (entry_id, account_id, transaction_type, amount)
         VALUES ($1, (SELECT account_id FROM accounts WHERE account_code = '2.1.3.01'), 'credit', $2)`,
        [entryId, extractedData.taxAmount]
      );
    }

    // Línea de crédito (Cuentas por pagar)
    const creditAmount = extractedData.amount - extractedData.taxAmount;
    await client.query(
      `INSERT INTO journal_entry_lines (entry_id, account_id, transaction_type, amount)
       VALUES ($1, (SELECT account_id FROM accounts WHERE account_code = '2.1.1.01'), 'credit', $2)`,
      [entryId, creditAmount]
    );
  }

  private async generateEntryNumber(client: any, tenantId: string): Promise<string> {
    const result = await client.query(
      `SELECT COUNT(*) as count FROM journal_entries WHERE tenant_id = $1`,
      [tenantId]
    );

    const count = parseInt(result.rows[0].count) + 1;
    return `AS-${new Date().getFullYear()}-${count.toString().padStart(6, '0')}`;
  }
}
```

### 3.7 Agente de Detección de Anomalías

```typescript
// agents/anomaly-detection-agent/src/anomalyDetectionAgent.ts
import { Agent } from '../../common/src/agent';
import { VertexAI } from '@google-cloud/vertexai';

export class AnomalyDetectionAgent extends Agent {
  private vertexAI: VertexAI;

  constructor() {
    super();
    this.vertexAI = new VertexAI({ project: PROJECT_ID, location: 'us-central1' });
  }

  getName(): string {
    return 'anomaly-detection-agent';
  }

  async execute(input: any): Promise<any> {
    const { transactionId, tenantId, amount, category } = input;

    console.log(`Detecting anomalies for transaction ${transactionId}`);

    // Obtener histórico de transacciones
    const historicalData = await this.getHistoricalData(tenantId, category);

    // Detectar anomalías con ML
    const anomalies = await this.detectAnomalies(amount, historicalData);

    if (anomalies.length > 0) {
      // Publicar evento de anomalía detectada
      await this.publishEvent('anomaly.detected', {
        transactionId,
        tenantId,
        anomalies,
      });
    }

    return {
      transactionId,
      anomalies,
    };
  }

  protected async subscribeToTopics(): Promise<void> {
    const subscription = await this.pubsub
      .topic('transaction.created')
      .subscription('anomaly-detection-agent-subscription');

    subscription.on('message', (message) => this.handleEvent(message));
    this.subscriptions.set('transaction.created', subscription);
  }

  private async getHistoricalData(tenantId: string, category: string): Promise<number[]> {
    const pool = await getPool();
    const result = await pool.query(
      `SELECT amount FROM transactions 
       WHERE tenant_id = $1 AND category = $2 
       AND created_at >= NOW() - INTERVAL '6 months'
       ORDER BY created_at DESC`,
      [tenantId, category]
    );

    return result.rows.map(row => row.amount);
  }

  private async detectAnomalies(
    currentAmount: number,
    historicalData: number[]
  ): Promise<Anomaly[]> {
    const anomalies: Anomaly[] = [];

    if (historicalData.length < 10) {
      return anomalies;
    }

    const mean = historicalData.reduce((a, b) => a + b, 0) / historicalData.length;
    const stdDev = Math.sqrt(
      historicalData.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / historicalData.length
    );

    const zScore = Math.abs((currentAmount - mean) / stdDev);

    if (zScore > 3) {
      anomalies.push({
        type: 'statistical',
        severity: 'high',
        message: `Amount is ${zScore.toFixed(2)} standard deviations from mean`,
        value: currentAmount,
        expected: mean,
        zScore,
      });
    } else if (zScore > 2) {
      anomalies.push({
        type: 'statistical',
        severity: 'medium',
        message: `Amount is ${zScore.toFixed(2)} standard deviations from mean`,
        value: currentAmount,
        expected: mean,
        zScore,
      });
    }

    return anomalies;
  }
}
```

### 3.8 Agente de Predicción

```typescript
// agents/prediction-agent/src/predictionAgent.ts
import { Agent } from '../../common/src/agent';
import { VertexAI } from '@google-cloud/vertexai';

export class PredictionAgent extends Agent {
  private vertexAI: VertexAI;

  constructor() {
    super();
    this.vertexAI = new VertexAI({ project: PROJECT_ID, location: 'us-central1' });
  }

  getName(): string {
    return 'prediction-agent';
  }

  async execute(input: any): Promise<any> {
    const { tenantId, predictionType } = input;

    console.log(`Generating ${predictionType} prediction for tenant ${tenantId}`);

    switch (predictionType) {
      case 'expenses':
        return await this.predictExpenses(tenantId);
      case 'revenue':
        return await this.predictRevenue(tenantId);
      case 'cash_flow':
        return await this.predictCashFlow(tenantId);
      default:
        throw new Error(`Unknown prediction type: ${predictionType}`);
    }
  }

  protected async subscribeToTopics(): Promise<void> {
    const subscription = await this.pubsub
      .topic('prediction.requested')
      .subscription('prediction-agent-subscription');

    subscription.on('message', (message) => this.handleEvent(message));
    this.subscriptions.set('prediction.requested', subscription);
  }

  private async predictExpenses(tenantId: string): Promise<PredictionResult> {
    const pool = await getPool();
    const result = await pool.query(
      `SELECT 
         EXTRACT(MONTH FROM date) as month,
         EXTRACT(YEAR FROM date) as year,
         SUM(amount) as total
       FROM transactions
       WHERE tenant_id = $1 AND type = 'expense'
       GROUP BY month, year
       ORDER BY year DESC, month DESC
       LIMIT 12`,
      [tenantId]
    );

    const historicalData = result.rows.map(row => ({
      month: row.month,
      year: row.year,
      total: parseFloat(row.total),
    }));

    // Usar Vertex AI para predecir
    const model = this.vertexAI.getGenerativeModel({
      model: 'gemini-pro',
    });

    const prompt = `
      Based on the following historical expense data, predict the expenses for the next 3 months:
      ${JSON.stringify(historicalData)}
      
      Provide the prediction in JSON format with the following structure:
      {
        "predictions": [
          { "month": 1, "year": 2024, "predicted_amount": 10000 },
          { "month": 2, "year": 2024, "predicted_amount": 10500 },
          { "month": 3, "year": 2024, "predicted_amount": 11000 }
        ],
        "confidence": 0.85
      }
    `;

    const response = await model.generateContent(prompt);
    const text = response.response.candidates?.[0]?.content?.parts?.[0]?.text || '';
    const prediction = JSON.parse(text);

    return {
      type: 'expenses',
      predictions: prediction.predictions,
      confidence: prediction.confidence,
    };
  }

  private async predictRevenue(tenantId: string): Promise<PredictionResult> {
    // Implementación similar para ingresos
    return {
      type: 'revenue',
      predictions: [],
      confidence: 0,
    };
  }

  private async predictCashFlow(tenantId: string): Promise<PredictionResult> {
    // Implementación similar para flujo de caja
    return {
      type: 'cash_flow',
      predictions: [],
      confidence: 0,
    };
  }
}
```

---

## 4. Workflow de Procesamiento

### 4.1 Definición de Workflow

```typescript
// agents/orchestrator/src/workflow.ts
export class Workflow {
  private id: string;
  private name: string;
  private steps: WorkflowStep[];
  private status: 'pending' | 'running' | 'completed' | 'failed' | 'aborted';

  constructor(name: string, steps: WorkflowStep[]) {
    this.id = generateUUID();
    this.name = name;
    this.steps = steps;
    this.status = 'pending';
  }

  getId(): string {
    return this.id;
  }

  getName(): string {
    return this.name;
  }

  getSteps(): WorkflowStep[] {
    return this.steps;
  }

  getStatus(): string {
    return this.status;
  }

  async markStepAsCompleted(stepName: string): Promise<void> {
    const step = this.steps.find(s => s.name === stepName);
    if (step) {
      step.status = 'completed';
    }
  }

  async markStepAsSkipped(stepName: string): Promise<void> {
    const step = this.steps.find(s => s.name === stepName);
    if (step) {
      step.status = 'skipped';
    }
  }

  async abort(): Promise<void> {
    this.status = 'aborted';
  }
}

export class WorkflowStep {
  name: string;
  agentName: string;
  input: any;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
  recoveryStrategy: 'retry' | 'skip' | 'abort';

  constructor(
    name: string,
    agentName: string,
    input: any,
    recoveryStrategy: 'retry' | 'skip' | 'abort' = 'retry'
  ) {
    this.name = name;
    this.agentName = agentName;
    this.input = input;
    this.status = 'pending';
    this.recoveryStrategy = recoveryStrategy;
  }
}
```

### 4.2 Workflow de Procesamiento de Documentos

```typescript
// agents/orchestrator/src/workflows/documentProcessingWorkflow.ts
import { Workflow, WorkflowStep } from '../workflow';

export function createDocumentProcessingWorkflow(
  documentId: string,
  storagePath: string,
  mimeType: string,
  tenantId: string
): Workflow {
  const steps = [
    new WorkflowStep(
      'ocr',
      'ocr-agent',
      { documentId, storagePath, mimeType },
      'retry'
    ),
    new WorkflowStep(
      'extraction',
      'extraction-agent',
      { documentId }, // Se llenará con el resultado del paso anterior
      'retry'
    ),
    new WorkflowStep(
      'validation',
      'validation-agent',
      { documentId }, // Se llenará con el resultado del paso anterior
      'skip' // Si falla, continuar con el siguiente paso
    ),
    new WorkflowStep(
      'accounting',
      'accounting-agent',
      { documentId, tenantId }, // Se llenará con el resultado del paso anterior
      'abort' // Si falla, abortar el workflow
    ),
    new WorkflowStep(
      'anomaly_detection',
      'anomaly-detection-agent',
      { tenantId }, // Se llenará con el resultado del paso anterior
      'skip' // Si falla, continuar
    ),
  ];

  return new Workflow('document-processing', steps);
}
```

---

## 5. Manejo de Conflictos

### 5.1 Sistema de Versionamiento de Eventos

```typescript
// agents/common/src/eventVersioning.ts
export class EventVersioning {
  private eventStore: Map<string, EventVersion[]>;

  constructor() {
    this.eventStore = new Map();
  }

  async saveEvent(event: any): Promise<void> {
    const eventId = event.id;
    const version = this.getNextVersion(eventId);

    const eventVersion: EventVersion = {
      eventId,
      version,
      eventType: event.type,
      data: event.data,
      timestamp: new Date(),
    };

    if (!this.eventStore.has(eventId)) {
      this.eventStore.set(eventId, []);
    }

    this.eventStore.get(eventId)!.push(eventVersion);
  }

  async getEventHistory(eventId: string): Promise<EventVersion[]> {
    return this.eventStore.get(eventId) || [];
  }

  async resolveConflict(
    eventId: string,
    strategy: 'last-write-wins' | 'merge' | 'manual'
  ): Promise<any> {
    const history = await this.getEventHistory(eventId);

    switch (strategy) {
      case 'last-write-wins':
        return history[history.length - 1].data;
      case 'merge':
        return this.mergeEvents(history);
      case 'manual':
        throw new Error('Manual resolution required');
    }
  }

  private getNextVersion(eventId: string): number {
    const history = this.eventStore.get(eventId) || [];
    return history.length + 1;
  }

  private mergeEvents(history: EventVersion[]): any {
    // Implementar lógica de merge
    return history[history.length - 1].data;
  }
}
```

### 5.2 Sistema de Compensación

```typescript
// agents/common/src/compensation.ts
export class CompensationManager {
  private compensations: Map<string, CompensationAction[]>;

  constructor() {
    this.compensations = new Map();
  }

  registerCompensation(workflowId: string, action: CompensationAction): void {
    if (!this.compensations.has(workflowId)) {
      this.compensations.set(workflowId, []);
    }

    this.compensations.get(workflowId)!.push(action);
  }

  async executeCompensation(workflowId: string): Promise<void> {
    const actions = this.compensations.get(workflowId) || [];

    // Ejecutar en orden inverso
    for (let i = actions.length - 1; i >= 0; i--) {
      try {
        await actions[i].execute();
      } catch (error) {
        console.error(`Compensation action failed:`, error);
      }
    }

    this.compensations.delete(workflowId);
  }
}

export interface CompensationAction {
  execute(): Promise<void>;
}

export class DeleteTransactionCompensation implements CompensationAction {
  constructor(private transactionId: number) {}

  async execute(): Promise<void> {
    const pool = await getPool();
    await pool.query('DELETE FROM transactions WHERE transaction_id = $1', [this.transactionId]);
  }
}

export class DeleteJournalEntryCompensation implements CompensationAction {
  constructor(private entryId: number) {}

  async execute(): Promise<void> {
    const pool = await getPool();
    await pool.query('DELETE FROM journal_entries WHERE entry_id = $1', [this.entryId]);
  }
}
```

---

## 6. Monitoreo y Observabilidad

### 6.1 Sistema de Métricas

```typescript
// agents/common/src/metrics.ts
import { MetricService } from '@google-cloud/monitoring';

export class AgentMetrics {
  private metricService: MetricService;

  constructor() {
    this.metricService = new MetricService();
  }

  async recordAgentExecution(
    agentName: string,
    duration: number,
    success: boolean
  ): Promise<void> {
    await this.metricService.writeTimeSeries({
      name: `custom.googleapis.com/pinad/agent/execution_duration`,
      resource: {
        type: 'cloud_function',
        labels: {
          function_name: agentName,
        },
      },
      metric: {
        labels: {
          agent_name: agentName,
          success: success.toString(),
        },
      },
      points: [
        {
          interval: {
            endTime: new Date(),
          },
          value: {
            doubleValue: duration,
          },
        },
      ],
    });
  }

  async recordEventProcessed(eventType: string): Promise<void> {
    await this.metricService.writeTimeSeries({
      name: `custom.googleapis.io/pinad/events/processed`,
      resource: {
        type: 'global',
      },
      metric: {
        labels: {
          event_type: eventType,
        },
      },
      points: [
        {
          interval: {
            endTime: new Date(),
          },
          value: {
            intValue: 1,
          },
        },
      ],
    });
  }
}
```

---

## 7. Despliegue

### 7.1 Configuración de Kubernetes

```yaml
# k8s/agents/ocr-agent-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ocr-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ocr-agent
  template:
    metadata:
      labels:
        app: ocr-agent
    spec:
      containers:
      - name: ocr-agent
        image: gcr.io/pinad-scanning-system/ocr-agent:latest
        ports:
        - containerPort: 8080
        env:
        - name: PROJECT_ID
          value: "pinad-scanning-system"
        - name: PUBSUB_EMULATOR_HOST
          value: "pubsub-emulator:8085"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
```

---

## Conclusión

La arquitectura de agentes de IA independientes incluye:
- **Orquestador de agentes** para coordinar workflows
- **Bus de mensajes (Pub/Sub)** para comunicación entre agentes
- **Agentes independientes** para cada proceso contable
- **Sistema de versionamiento de eventos** para manejar conflictos
- **Sistema de compensación** para revertir cambios
- **Monitoreo y métricas** para observabilidad
- **Despliegue en Kubernetes** para escalabilidad

Esta arquitectura permite cambios en el registro de ventas sin conflictos en el sistema, con modularidad completa y resiliencia ante fallos. Cada agente es independiente y puede ser actualizado o escalado sin afectar otros agentes.
