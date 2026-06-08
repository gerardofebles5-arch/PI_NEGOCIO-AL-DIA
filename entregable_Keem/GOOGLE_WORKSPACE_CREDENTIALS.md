# Credenciales de Google Workspace

## Fecha
Junio 8, 2026

## Clave de API
```
AIzaSyAG0gM9rUHowL14Aig5KrMtfdeSxnkYQik
```

## ID de Cliente OAuth 2.0
```
531174220363-3aeog10kkqkmbbgo21nsinf110u3qcin.apps.googleusercontent.com
```

## Secreto del Cliente
```
[OBTENER DESDE DASHBOARD > APIs & Services > Credentials > OAuth 2.0 Client IDs]
```

## URLs de Configuración

### Pantalla de Consentimiento
https://console.cloud.google.com/apis/credentials/consent?project=pinad-scanning-system

### Credenciales
https://console.cloud.google.com/apis/credentials?project=pinad-scanning-system

## APIs Habilitadas
- Gmail API
- Google Drive API
- Google Sheets API
- Google Calendar API

## Alcances (Scopes) Requeridos

### Gmail
- `https://www.googleapis.com/auth/gmail.send` - Enviar emails

### Drive
- `https://www.googleapis.com/auth/drive` - Acceso completo a Drive

### Sheets
- `https://www.googleapis.com/auth/spreadsheets` - Acceso completo a Sheets

### Calendar
- `https://www.googleapis.com/auth/calendar` - Acceso completo a Calendar

## Uso en el Proyecto

### Flutter Web
```dart
import 'package:googleapis/gmail/v1.dart';
import 'package:googleapis/drive/v3.dart';
import 'package:googleapis/sheets/v4.dart';
import 'package:googleapis/calendar/v3.dart';
import 'package:google_sign_in/google_sign_in.dart';

final GoogleSignIn _googleSignIn = GoogleSignIn(
  clientId: '531174220363-3aeog10kkqkmbbgo21nsinf110u3qcin.apps.googleusercontent.com',
  scopes: [
    GmailApi.gmailSendScope,
    DriveApi.driveScope,
    SheetsApi.spreadsheetsScope,
    CalendarApi.calendarScope,
  ],
);
```

### Cloud Functions
```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

credentials = Credentials(
    token='YOUR_ACCESS_TOKEN',
    client_id='531174220363-3aeog10kkqkmbbgo21nsinf110u3qcin.apps.googleusercontent.com',
    client_secret='YOUR_CLIENT_SECRET',
    token_uri='https://oauth2.googleapis.com/token',
)

gmail_service = build('gmail', 'v1', credentials=credentials)
drive_service = build('drive', 'v3', credentials=credentials)
sheets_service = build('sheets', 'v4', credentials=credentials)
calendar_service = build('calendar', 'v3', credentials=credentials)
```

## Seguridad

⚠️ **IMPORTANTE:** No compartas estas credenciales públicamente.
- No las subas a repositorios públicos
- Usa variables de entorno en producción
- Revoca las credenciales si se comprometen

## Próximos Pasos

1. Verificar que la pantalla de consentimiento esté configurada
2. Probar la autenticación OAuth
3. Implementar integración con cada API
