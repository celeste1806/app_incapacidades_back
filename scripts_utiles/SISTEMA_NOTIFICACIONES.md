# Sistema de Notificaciones de Incapacidades

## Flujo Completo de Rechazo de Incapacidad

### 1. Administrador Rechaza Incapacidad

**Ubicación**: Páginas de administración (`AdminIncapacidadesPendientes.jsx`, `AdminIncapacidadesRechazadas.jsx`)

**Proceso**:
1. Admin hace clic en "❌ Rechazada" en el dropdown de acciones
2. Se ejecuta `handleCambiarEstado(incapacidadId, 50)`
3. Se muestra prompt: `"❌ RECHAZAR INCAPACIDAD\n\nIngrese el motivo del rechazo:\n(Este mensaje se enviará por correo al empleado)"`
4. Se valida que el motivo no esté vacío
5. Se llama `cambiarEstadoIncapacidad(incapacidadId, 50, mensajeRechazo)`

### 2. Backend Procesa el Rechazo

**Ubicación**: `incapacidad_service.py` → `cambiar_estado()`

**Proceso**:
1. Se actualiza el estado de la incapacidad a `50` (rechazada)
2. Se guarda el mensaje de rechazo en `mensaje_rechazo`
3. Se registra la auditoría del cambio
4. Se llama `notification_service.notify_incapacity_rejected()`

### 3. Envío de Notificación por Correo

**Ubicación**: `notification_service.py` → `notify_incapacity_rejected()`

**Proceso**:
1. Se obtiene la información de la incapacidad rechazada
2. Se obtiene la información del empleado propietario (`usuario_id`)
3. Se obtiene la información del administrador que rechazó
4. Se crea el contenido del correo con:
   - Detalles de la incapacidad
   - Motivo del rechazo
   - Información del administrador
   - Fecha del rechazo
5. Se envía el correo al empleado

### 4. Usuario Ve el Estado Actualizado

**Ubicación**: `InicioPage.jsx`

**Proceso**:
1. El usuario ve su página de inicio
2. En el cuadro "Rechazadas" aparece el número de incapacidades rechazadas
3. En la sección "Mis Incapacidades" puede ver:
   - Estado "Rechazada" con color rojo
   - Motivo del rechazo en un cuadro destacado
   - Botón "✏️ Corregir" para corregir la incapacidad

## Configuración de Correos

### Variables de Entorno Requeridas

```bash
# Configuración SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tu_email@gmail.com
SMTP_PASSWORD=tu_app_password
FROM_EMAIL=tu_email@gmail.com
```

### Contenido del Correo

**Asunto**: `❌ Incapacidad Rechazada - [Nombre del Empleado]`

**Contenido HTML**:
- Diseño profesional con colores corporativos
- Detalles de la incapacidad (ID, fechas, días)
- Motivo específico del rechazo
- Información del administrador
- Fecha y hora del rechazo

## Estados de Incapacidad

| Código | Estado | Color | Descripción |
|--------|--------|-------|-------------|
| 11 | Pendiente | 🟡 Amarillo | Esperando revisión |
| 12 | Realizada | 🟢 Verde | Revisada y aprobada |
| 40 | Pagas | 🟢 Verde | Pagada |
| 44 | No Pagas | 🟢 Verde | No pagada |
| 50 | Rechazada | 🔴 Rojo | Rechazada por admin |

## Logs del Sistema

### Backend Logs

```
📧 NOTIFICACIÓN DE RECHAZO - Datos del empleado:
   👤 ID: 123
   📧 Email: empleado@empresa.com
   👤 Nombre: Juan Pérez

📧 ENVIANDO NOTIFICACIÓN DE RECHAZO:
   📧 Para: empleado@empresa.com
   👤 Empleado: Juan Pérez
   🆔 Incapacidad ID: 456
   ❌ Motivo del rechazo: Documentación incompleta
   👨‍💼 Rechazado por: Admin Usuario
   📅 Fecha: 2024-01-15T10:30:00

✅ Correo de rechazo enviado exitosamente a empleado@empresa.com
```

### Frontend Logs

```
DEBUG: Enviando notificación de rechazo para incapacidad 456
```

## Funcionalidades del Usuario

### Ver Incapacidades Rechazadas

1. **Cuadro de estadísticas**: Muestra número de rechazadas
2. **Lista completa**: Todas las incapacidades con estados visuales
3. **Detalles del rechazo**: Motivo específico visible
4. **Corrección**: Botón para corregir incapacidades rechazadas

### Corregir Incapacidad Rechazada

1. Click en "✏️ Corregir"
2. Se abre modal con datos pre-llenados
3. Usuario modifica los campos necesarios
4. Se crea nueva incapacidad con estado "Pendiente" (11)
5. Se envía para nueva revisión

## Solución de Problemas

### Error de Foreign Key

**Problema**: `Cannot add or update a child row: a foreign key constraint fails`

**Solución**: Ejecutar script para crear estado 50 en `parametro_hijo`:
```bash
python fix_estados_simple.py
```

### Correos no se envían

**Verificar**:
1. Variables de entorno SMTP configuradas
2. Credenciales correctas
3. Puerto y servidor SMTP válidos
4. Logs del backend para errores específicos

### Usuario no ve cambios

**Verificar**:
1. Token de autenticación válido
2. Usuario correcto logueado
3. Recarga de la página
4. Estado actualizado en base de datos
