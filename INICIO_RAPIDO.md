# (π)NAD V6.0 - Inicio Rápido (Modo Local)

## 🚀 Inicio en 3 Pasos

### Paso 1: Ejecutar el Backend
```bash
cd D:\NAD
venv\Scripts\python.exe main.py
```

El backend se iniciará en modo local sin Google Cloud.
Verás: "🏠 MODO LOCAL ACTIVADO"

### Paso 2: Ejecutar la App Flutter (Opcional)
```bash
cd D:\NAD\pinad_app
flutter run
```

**Nota:** Flutter se está descargando automáticamente. Espera a que termine la descarga.

### Paso 3: Usar el Sistema
- Backend API: http://localhost:5000
- App Flutter: Se abrirá en tu dispositivo/emulador

## 📁 Archivos Importantes

- `.env` - Configuración local
- `data/pinad_local.db` - Base de datos SQLite
- `logs/pinad_local.log` - Logs del sistema
- `README_LOCAL.md` - Documentación completa

## 🔧 Scripts Automatizados

```bash
# Configurar todo automáticamente
scripts\setup_local.bat

# Ejecutar backend
scripts\run_backend_local.bat

# Ejecutar Flutter
scripts\run_flutter_local.bat
```

## ✅ Verificación

### Backend
- Abre http://localhost:5000 en tu navegador
- Deberías ver el estado del sistema

### Flutter
- La app se abrirá en tu dispositivo
- Deberías ver la pantalla de inicio de (π)NAD

## 🆘 Problemas

### Backend no inicia
- Verifica que Python 3.11+ esté instalado
- Verifica que el virtual environment exista
- Revisa `logs/pinad_local.log`

### Flutter no inicia
- Espera a que termine la descarga de Flutter
- Verifica que Flutter esté instalado en `C:\flutter`
- Ejecuta `flutter doctor` para verificar

### Base de datos no funciona
- Verifica que `data/pinad_local.db` exista
- Verifica que los directorios `data/` existan
- Ejecuta el script `setup_local.bat` nuevamente

## 📞 Soporte

Para más información, revisa:
- `README_LOCAL.md` - Documentación completa
- `logs/pinad_local.log` - Logs del sistema
- `scripts/` - Scripts automatizados
