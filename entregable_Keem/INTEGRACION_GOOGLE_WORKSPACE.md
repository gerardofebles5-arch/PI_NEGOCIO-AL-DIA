# Integración de Google Workspace en el Proyecto

## Fecha
Junio 7, 2026

## Objetivo
Integrar Google Workspace de manera significativa en el sistema de escaneo contable para agregar valor y funcionalidad.

---

## Arquitectura de Integración

```
┌─────────────────────────────────────────────────────────────────┐
│                    Firebase (Principal)                          │
│  - Authentication                                               │
│  - Firestore (Base de datos)                                   │
│  - Storage (Documentos)                                         │
│  - Functions (Backend)                                          │
│  - Hosting (Web app)                                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Integración vía Google Workspace API
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    Google Workspace (Integrado)                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Gmail API                                                │  │
│  │  - Notificaciones automáticas                              │  │
│  │  - Envío de reportes por email                            │  │
│  │  - Alertas de documentos pendientes                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Google Drive API                                         │  │
│  │  - Backup automático de documentos                        │  │
│  │  - Sincronización con clientes                            │  │
│  │  - Almacenamiento de documentos legales                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Google Sheets API                                        │  │
│  │  - Exportación automática de reportes                     │  │
│  │  - Hojas de cálculo en tiempo real                        │  │
│  │  - Análisis de datos financieros                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Google Calendar API                                      │  │
│  │  - Recordatorios de fechas de impuestos                   │  │
│  │  - Agendamiento de reuniones con clientes                 │  │
│  │  - Alertas de vencimientos                               │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Integración con Gmail API

### 1.1 Funcionalidades

**Notificaciones Automáticas:**
- Cuando un documento es procesado → Email al cliente
- Cuando una transacción es creada → Email al contador
- Cuando hay una anomalía detectada → Email de alerta
- Reportes semanales/mensuales → Email resumen

**Envío de Reportes:**
- Reporte de IVA → Email con PDF adjunto
- Reporte de ISLR → Email con PDF adjunto
- Estado de resultados → Email con PDF adjunto
- Balance general → Email con PDF adjunto

**Alertas de Documentos Pendientes:**
- Documentos sin procesar → Email recordatorio
- Documentos con errores → Email de corrección
- Cuotas excedidas → Email de alerta

### 1.2 Implementación

```typescript
// functions/src/services/gmailService.ts
import { google } from 'googleapis';
import { OAuth2Client } from 'google-auth-library';

export class GmailService {
  private gmail: any;

  constructor(auth: OAuth2Client) {
    this.gmail = google.gmail({ version: 'v1', auth });
  }

  async sendNotification(
    to: string,
    subject: string,
    body: string,
    attachments?: any[]
  ): Promise<void> {
    const message = this.createEmail(to, subject, body, attachments);
    await this.gmail.users.messages.send({
      userId: 'me',
      requestBody: { raw: message },
    });
  }

  async sendReport(
    to: string,
    reportType: string,
    reportData: any,
    pdfBuffer: Buffer
  ): Promise<void> {
    const subject = `Reporte ${reportType} - PINAD`;
    const body = this.createReportBody(reportType, reportData);
    
    const attachments = [
      {
        filename: `${reportType}_${new Date().toISOString().split('T')[0]}.pdf`,
        content: pdfBuffer.toString('base64'),
        encoding: 'base64',
      },
    ];

    await this.sendNotification(to, subject, body, attachments);
  }

  private createEmail(
    to: string,
    subject: string,
    body: string,
    attachments?: any[]
  ): string {
    const email = [
      `To: ${to}`,
      `Subject: ${subject}`,
      'MIME-Version: 1.0',
      'Content-Type: multipart/mixed; boundary="boundary"',
      '',
      '--boundary',
      'Content-Type: text/plain; charset="UTF-8"',
      '',
      body,
    ];

    if (attachments && attachments.length > 0) {
      attachments.forEach((attachment) => {
        email.push(
          '--boundary',
          `Content-Type: application/octet-stream; name="${attachment.filename}"`,
          'Content-Transfer-Encoding: base64',
          `Content-Disposition: attachment; filename="${attachment.filename}"`,
          '',
          attachment.content
        );
      });
    }

    email.push('--boundary--');
    return Buffer.from(email.join('\r\n')).toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  }

  private createReportBody(reportType: string, reportData: any): string {
    return `
Reporte ${reportType}
===================

Fecha: ${new Date().toLocaleDateString('es-VE')}

Resumen:
--------
${JSON.stringify(reportData, null, 2)}

Este reporte fue generado automáticamente por el sistema PINAD.
Para más información, contacte a soporte@pinad.com.
    `;
  }
}
```

### 1.3 Cloud Function para Notificaciones

```typescript
// functions/src/index.ts
import { GmailService } from './services/gmailService';

export const onDocumentProcessed = functions.firestore
  .document('documents/{documentId}')
  .onUpdate(async (change, context) => {
    const before = change.before.data();
    const after = change.after.data();

    if (before.status === 'processing' && after.status === 'processed') {
      // Documento procesado, enviar notificación
      const gmailService = new GmailService(auth);
      await gmailService.sendNotification(
        after.clientEmail,
        'Documento Procesado - PINAD',
        `Tu documento "${after.fileName}" ha sido procesado exitosamente.\n\nPuedes ver los resultados en tu dashboard.`
      );
    }
  });
```

---

## 2. Integración con Google Drive API

### 2.1 Funcionalidades

**Backup Automático de Documentos:**
- Cuando un documento se sube a Firebase Storage → Copia a Google Drive
- Organización por cliente y fecha
- Versión automática de documentos

**Sincronización con Clientes:**
- Carpetas compartidas con cada cliente
- Acceso controlado por permisos
- Historial de cambios

**Almacenamiento de Documentos Legales:**
- Contratos con clientes
- Documentos fiscales
- Reportes oficiales

### 2.2 Implementación

```typescript
// functions/src/services/driveService.ts
import { google } from 'googleapis';
import { OAuth2Client } from 'google-auth-library';

export class DriveService {
  private drive: any;

  constructor(auth: OAuth2Client) {
    this.drive = google.drive({ version: 'v3', auth });
  }

  async createClientFolder(clientId: string, clientName: string): Promise<string> {
    const folderMetadata = {
      name: `Cliente: ${clientName}`,
      mimeType: 'application/vnd.google-apps.folder',
      parents: [await this.getOrCreateRootFolder()],
    };

    const folder = await this.drive.files.create({
      requestBody: folderMetadata,
      fields: 'id',
    });

    return folder.data.id;
  }

  async backupDocument(
    documentId: string,
    fileName: string,
    fileBuffer: Buffer,
    clientId: string
  ): Promise<string> {
    const clientFolderId = await this.getClientFolder(clientId);
    const dateFolderId = await this.getOrCreateDateFolder(clientFolderId);

    const fileMetadata = {
      name: fileName,
      parents: [dateFolderId],
    };

    const media = {
      mimeType: 'application/pdf',
      body: fileBuffer,
    };

    const file = await this.drive.files.create({
      requestBody: fileMetadata,
      media: media,
      fields: 'id',
    });

    return file.data.id;
  }

  async shareFolderWithClient(folderId: string, clientEmail: string): Promise<void> {
    await this.drive.permissions.create({
      fileId: folderId,
      requestBody: {
        role: 'writer',
        type: 'user',
        emailAddress: clientEmail,
      },
    });
  }

  private async getOrCreateRootFolder(): Promise<string> {
    // Buscar o crear carpeta raíz "PINAD Documentos"
    const query = `name='PINAD Documentos' and mimeType='application/vnd.google-apps.folder' and trashed=false`;
    const response = await this.drive.files.list({ q: query });

    if (response.data.files.length > 0) {
      return response.data.files[0].id;
    }

    const folder = await this.drive.files.create({
      requestBody: {
        name: 'PINAD Documentos',
        mimeType: 'application/vnd.google-apps.folder',
      },
      fields: 'id',
    });

    return folder.data.id;
  }

  private async getClientFolder(clientId: string): Promise<string> {
    // Buscar o crear carpeta del cliente
    const query = `name='${clientId}' and mimeType='application/vnd.google-apps.folder' and trashed=false`;
    const response = await this.drive.files.list({ q: query });

    if (response.data.files.length > 0) {
      return response.data.files[0].id;
    }

    // Crear carpeta del cliente
    const clientData = await admin.firestore().collection('clients').doc(clientId).get();
    const clientName = clientData.data()?.name || clientId;

    return await this.createClientFolder(clientId, clientName);
  }

  private async getOrCreateDateFolder(parentFolderId: string): Promise<string> {
    const date = new Date().toISOString().split('T')[0];
    const query = `name='${date}' and mimeType='application/vnd.google-apps.folder' and '${parentFolderId}' in parents and trashed=false`;
    const response = await this.drive.files.list({ q: query });

    if (response.data.files.length > 0) {
      return response.data.files[0].id;
    }

    const folder = await this.drive.files.create({
      requestBody: {
        name: date,
        mimeType: 'application/vnd.google-apps.folder',
        parents: [parentFolderId],
      },
      fields: 'id',
    });

    return folder.data.id;
  }
}
```

### 2.3 Cloud Function para Backup

```typescript
// functions/src/index.ts
import { DriveService } from './services/driveService';

export const onDocumentUploaded = functions.storage
  .object()
  .onFinalize(async (object) => {
    const driveService = new DriveService(auth);
    
    // Descargar documento de Firebase Storage
    const fileBuffer = await admin.storage().bucket(object.bucket).file(object.name).download();
    
    // Extraer metadata
    const metadata = await admin.storage().bucket(object.bucket).file(object.name).getMetadata();
    const clientId = metadata.metadata?.clientId;
    
    // Backup a Google Drive
    await driveService.backupDocument(
      object.name,
      object.name.split('/').pop() || object.name,
      fileBuffer[0],
      clientId
    );
  });
```

---

## 3. Integración con Google Sheets API

### 3.1 Funcionalidades

**Exportación Automática de Reportes:**
- Reporte de IVA → Hoja de cálculo en tiempo real
- Reporte de ISLR → Hoja de cálculo en tiempo real
- Estado de resultados → Hoja de cálculo en tiempo real
- Balance general → Hoja de cálculo en tiempo real

**Hojas de Cálculo en Tiempo Real:**
- Actualización automática cuando hay nuevos datos
- Gráficos automáticos
- Fórmulas personalizadas

**Análisis de Datos Financieros:**
- Tendencias de ingresos/gastos
- Comparación de períodos
- Proyecciones

### 3.2 Implementación

```typescript
// functions/src/services/sheetsService.ts
import { google } from 'googleapis';
import { OAuth2Client } from 'google-auth-library';

export class SheetsService {
  private sheets: any;

  constructor(auth: OAuth2Client) {
    this.sheets = google.sheets({ version: 'v4', auth });
  }

  async createReportSheet(
    reportType: string,
    clientId: string,
    data: any[]
  ): Promise<string> {
    const spreadsheet = await this.sheets.spreadsheets.create({
      requestBody: {
        properties: {
          title: `Reporte ${reportType} - ${new Date().toLocaleDateString('es-VE')}`,
        },
      },
    });

    const spreadsheetId = spreadsheet.data.spreadsheetId;

    // Agregar datos
    await this.sheets.spreadsheets.values.update({
      spreadsheetId,
      range: 'A1',
      valueInputOption: 'USER_ENTERED',
      requestBody: {
        values: this.formatDataForSheet(data),
      },
    });

    // Compartir con el cliente
    await this.shareSpreadsheet(spreadsheetId, clientId);

    return spreadsheetId;
  }

  async updateSheetData(spreadsheetId: string, data: any[]): Promise<void> {
    await this.sheets.spreadsheets.values.update({
      spreadsheetId,
      range: 'A1',
      valueInputOption: 'USER_ENTERED',
      requestBody: {
        values: this.formatDataForSheet(data),
      },
    });
  }

  async addChart(spreadsheetId: string, chartType: string): Promise<void> {
    // Agregar gráfico a la hoja de cálculo
    await this.sheets.spreadsheets.batchUpdate({
      spreadsheetId,
      requestBody: {
        requests: [
          {
            addChart: {
              chart: {
                spec: {
                  title: chartType,
                  basicChart: {
                    chartType: 'LINE',
                    domains: [{ domain: { sourceRange: { sources: [{ sheetId: 0, startRowIndex: 0, endRowIndex: 1, startColumnIndex: 0, endColumnIndex: 1 }] } } }],
                    series: [
                      {
                        series: {
                          sourceRange: { sources: [{ sheetId: 0, startRowIndex: 1, endRowIndex: 10, startColumnIndex: 1, endColumnIndex: 2 }] },
                        },
                      },
                    ],
                  },
                },
                position: {
                  overlayPosition: {
                    anchorRow: 3,
                    anchorColumn: 5,
                  },
                },
              },
            },
          },
        ],
      },
    });
  }

  private formatDataForSheet(data: any[]): any[][] {
    if (data.length === 0) return [];

    const headers = Object.keys(data[0]);
    const rows = data.map(item => Object.values(item));
    
    return [headers, ...rows];
  }

  private async shareSpreadsheet(spreadsheetId: string, clientId: string): Promise<void> {
    const driveService = new DriveService(auth);
    await driveService.shareFolderWithClient(spreadsheetId, clientId);
  }
}
```

### 3.3 Cloud Function para Reportes

```typescript
// functions/src/index.ts
import { SheetsService } from './services/sheetsService';

export const generateMonthlyReport = functions.pubsub
  .schedule('0 0 1 * *') // Primer día de cada mes a las 00:00
  .onRun(async (context) => {
    const sheetsService = new SheetsService(auth);

    // Obtener todos los clientes
    const clientsSnapshot = await admin.firestore().collection('clients').get();

    for (const clientDoc of clientsSnapshot.docs) {
      const clientId = clientDoc.id;
      
      // Generar reporte de IVA
      const ivaData = await getIVAData(clientId);
      await sheetsService.createReportSheet('IVA', clientId, ivaData);

      // Generar reporte de ISLR
      const islrData = await getISLRData(clientId);
      await sheetsService.createReportSheet('ISLR', clientId, islrData);
    }
  });
```

---

## 4. Integración con Google Calendar API

### 4.1 Funcionalidades

**Recordatorios de Fechas de Impuestos:**
- IVA mensual → Evento en calendario
- ISLR trimestral → Evento en calendario
- Declaraciones anuales → Evento en calendario

**Agendamiento de Reuniones con Clientes:**
- Citas de revisión
- Entrega de reportes
- Consultas

**Alertas de Vencimientos:**
- 7 días antes → Email de recordatorio
- 1 día antes → Email de urgencia
- Día del vencimiento → Email de alerta

### 4.2 Implementación

```typescript
// functions/src/services/calendarService.ts
import { google } from 'googleapis';
import { OAuth2Client } from 'google-auth-library';

export class CalendarService {
  private calendar: any;

  constructor(auth: OAuth2Client) {
    this.calendar = google.calendar({ version: 'v3', auth });
  }

  async createTaxReminder(
    taxType: string,
    dueDate: Date,
    clientId: string
  ): Promise<string> {
    const event = {
      summary: `Vencimiento ${taxType}`,
      description: `Recordatorio de vencimiento de ${taxType}`,
      start: {
        date: dueDate.toISOString().split('T')[0],
      },
      end: {
        date: dueDate.toISOString().split('T')[0],
      },
      reminders: {
        useDefault: false,
        overrides: [
          { method: 'email', minutes: 60 * 24 * 7 }, // 7 días antes
          { method: 'email', minutes: 60 * 24 }, // 1 día antes
          { method: 'popup', minutes: 0 }, // El mismo día
        ],
      },
    };

    const createdEvent = await this.calendar.events.insert({
      calendarId: 'primary',
      requestBody: event,
    });

    return createdEvent.data.id;
  }

  async scheduleMeeting(
    clientEmail: string,
    title: string,
    description: string,
    startTime: Date,
    duration: number
  ): Promise<string> {
    const endTime = new Date(startTime.getTime() + duration * 60 * 1000);

    const event = {
      summary: title,
      description: description,
      start: {
        dateTime: startTime.toISOString(),
      },
      end: {
        dateTime: endTime.toISOString(),
      },
      attendees: [{ email: clientEmail }],
      conferenceData: {
        createRequest: {
          requestId: Date.now().toString(),
        },
      },
    };

    const createdEvent = await this.calendar.events.insert({
      calendarId: 'primary',
      requestBody: event,
      conferenceDataVersion: 1,
    });

    return createdEvent.data.hangoutLink;
  }

  async createAnnualTaxCalendar(clientId: string): Promise<void> {
    const currentYear = new Date().getFullYear();

    // IVA mensual (día 15 de cada mes)
    for (let month = 1; month <= 12; month++) {
      const dueDate = new Date(currentYear, month, 15);
      await this.createTaxReminder('IVA Mensual', dueDate, clientId);
    }

    // ISLR trimestral (marzo, junio, septiembre, diciembre)
    const islrMonths = [2, 5, 8, 11];
    for (const month of islrMonths) {
      const dueDate = new Date(currentYear, month, 15);
      await this.createTaxReminder('ISLR Trimestral', dueDate, clientId);
    }

    // Declaración anual ISLR (marzo)
    const annualDueDate = new Date(currentYear, 2, 31);
    await this.createTaxReminder('Declaración ISLR Anual', annualDueDate, clientId);
  }
}
```

### 4.3 Cloud Function para Calendario

```typescript
// functions/src/index.ts
import { CalendarService } from './services/calendarService';

export const onClientCreated = functions.firestore
  .document('clients/{clientId}')
  .onCreate(async (snapshot, context) => {
    const client = snapshot.data();
    const calendarService = new CalendarService(auth);

    // Crear calendario de impuestos anual
    await calendarService.createAnnualTaxCalendar(context.params.clientId);
  });
```

---

## 5. Configuración de Google Workspace API

### 5.1 Habilitar APIs en Google Cloud Console

1. Ve a https://console.cloud.google.com/apis/library
2. Habilita las siguientes APIs:
   - Gmail API
   - Google Drive API
   - Google Sheets API
   - Google Calendar API

### 5.2 Crear Cuenta de Servicio

1. Ve a IAM y administrador > Cuentas de servicio
2. Crea una cuenta de servicio: `pinad-workspace@pinad-scanning-system.iam.gserviceaccount.com`
3. Asigna roles:
   - Editor de Google Drive
   - Editor de Google Sheets
   - Editor de Google Calendar
   - Usuario de Gmail

### 5.3 Configurar OAuth 2.0

1. Ve a APIs y servicios > Credenciales
2. Crea credenciales OAuth 2.0
3. Configura pantalla de consentimiento
4. Obtén client ID y client secret

### 5.4 Configurar Dominio de Verificación

1. En Google Workspace, configura tu dominio
2. Verifica el dominio con DNS
3. Habilita API access para la cuenta de servicio

---

## 6. Flujo de Integración Completo

```
1. Cliente sube documento
   ↓
2. Firebase Storage recibe documento
   ↓
3. Cloud Function procesa documento con motor OCR
   ↓
4. Firestore guarda datos extraídos
   ↓
5. Gmail envía notificación al cliente
   ↓
6. Google Drive hace backup del documento
   ↓
7. Google Sheets actualiza reporte
   ↓
8. Google Calendar agenda recordatorio
   ↓
9. Cliente ve resultados en dashboard
```

---

## Conclusión

Google Workspace se integra de manera significativa en el proyecto:

- **Gmail:** Notificaciones automáticas y envío de reportes
- **Google Drive:** Backup automático de documentos
- **Google Sheets:** Reportes en tiempo real
- **Google Calendar:** Recordatorios de fechas de impuestos

Esta integración agrega valor al sistema, mejora la comunicación con clientes, y proporciona herramientas de productividad integradas.
