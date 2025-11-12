# 📧 Configuración de Notificaciones por Correo Automáticas

## 🎯 Objetivo

Configurar el envío automático de correos electrónicos cuando un administrador rechace una incapacidad, notificando al empleado sobre el motivo del rechazo.

## 🚀 Configuración Rápida

### Paso 1: Ejecutar el Configurador

```bash
cd incapacidades-backend-main
python configurar_correos.py
```

Siga las instrucciones en pantalla para configurar su proveedor de correo.

### Paso 2: Probar la Configuración

```bash
python probar_correos.py
```

Ingrese un email de prueba para verificar que el sistema funciona.

### Paso 3: Reiniciar el Servidor

```bash
python run_server.py
```

## 📋 Configuración Manual

Si prefiere configurar manualmente, cree un archivo `.env` en la carpeta `incapacidades-backend-main`:

```bash
# Configuración SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tu_email@gmail.com
SMTP_PASSWORD=tu_app_password
FROM_EMAIL=tu_email@gmail.com
```

## 🔧 Configuración por Proveedor

### Gmail (Recomendado)

1. **Habilitar autenticación de 2 factores** en tu cuenta de Gmail
2. **Generar contraseña de aplicación**:
   - Ve a [Configuración de Google](https://myaccount.google.com/)
   - Seguridad → Contraseñas de aplicaciones
   - Selecciona "Correo" y genera una nueva contraseña
   - Usa esta contraseña como `SMTP_PASSWORD`

```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tu_email@gmail.com
SMTP_PASSWORD=tu_app_password_de_16_caracteres
FROM_EMAIL=tu_email@gmail.com
```

### Outlook/Hotmail

```bash
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=tu_email@outlook.com
SMTP_PASSWORD=tu_password_normal
FROM_EMAIL=tu_email@outlook.com
```

### Yahoo

1. **Habilitar autenticación de 2 factores**
2. **Generar contraseña de aplicación**

```bash
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USERNAME=tu_email@yahoo.com
SMTP_PASSWORD=tu_app_password
FROM_EMAIL=tu_email@yahoo.com
```

### Servidor SMTP Personalizado

```bash
SMTP_SERVER=tu_servidor_smtp.com
SMTP_PORT=587
SMTP_USERNAME=tu_usuario_smtp
SMTP_PASSWORD=tu_password_smtp
FROM_EMAIL=noreply@tu_empresa.com
```

## 🔄 Flujo de Notificación

### 1. Administrador Rechaza Incapacidad

1. Admin va a "Incapacidades Pendientes"
2. Hace clic en "❌ Rechazada" en el dropdown
3. Ingresa el motivo del rechazo
4. Confirma el rechazo

### 2. Sistema Envía Correo Automático

1. Se actualiza el estado de la incapacidad a 50 (rechazada)
2. Se guarda el motivo del rechazo
3. Se envía correo automático al empleado con:
   - Detalles de la incapacidad rechazada
   - Motivo específico del rechazo
   - Información del administrador
   - Fecha y hora del rechazo

### 3. Empleado Recibe Notificación

El empleado recibe un correo con:
- **Asunto**: "❌ Incapacidad Rechazada - [Nombre del Empleado]"
- **Contenido HTML** profesional con diseño corporativo
- **Información completa** del rechazo
- **Instrucciones** para contactar recursos humanos

## 📊 Monitoreo y Logs

### Logs del Servidor

El sistema registra todas las notificaciones:

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

### Verificar Estado

Para verificar que las notificaciones están funcionando:

1. Revise los logs del servidor backend
2. Busque mensajes que contengan "📧 ENVIANDO NOTIFICACIÓN"
3. Verifique que aparezca "✅ Correo enviado exitosamente"

## 🛠️ Solución de Problemas

### Error: "Authentication failed"

**Causa**: Credenciales incorrectas o configuración de seguridad

**Solución**:
- Para Gmail: Use contraseñas de aplicación, no su contraseña normal
- Verifique que la autenticación de 2 factores esté habilitada
- Confirme que el usuario y contraseña sean correctos

### Error: "Connection refused"

**Causa**: Problemas de red o configuración SMTP

**Solución**:
- Verifique que el servidor SMTP y puerto sean correctos
- Confirme que no haya firewall bloqueando la conexión
- Pruebe con un servidor SMTP diferente

### Correos van a Spam

**Causa**: Configuración de reputación del correo

**Solución**:
- Use un correo corporativo en lugar de Gmail personal
- Configure SPF, DKIM y DMARC en su dominio
- Incluya información de contacto válida en el correo

### Correos no se envían

**Causa**: Configuración SMTP incorrecta o problemas del servidor

**Solución**:
1. Ejecute `python probar_correos.py` para diagnosticar
2. Revise los logs del servidor para errores específicos
3. Verifique la configuración en el archivo `.env`
4. Confirme que el servidor backend esté ejecutándose

## 📱 Funcionalidades del Usuario

### Ver Incapacidades Rechazadas

1. **Página de inicio**: Cuadro "Rechazadas" muestra el número
2. **Página específica**: "Incapacidades rechazadas" en el sidebar
3. **Detalles**: Motivo del rechazo visible
4. **Documentos**: Acceso a documentos originales

### Corregir Incapacidad Rechazada

1. Click en "✏️ Corregir" en la incapacidad rechazada
2. Se abre modal con datos pre-llenados
3. Usuario modifica los campos necesarios
4. Se crea nueva incapacidad con estado "Pendiente" (11)
5. Se envía para nueva revisión

## 🔒 Seguridad

### Variables de Entorno

- **Nunca** incluya credenciales en el código fuente
- Use el archivo `.env` para configuración local
- En producción, use variables de entorno del servidor
- Mantenga el archivo `.env` fuera del control de versiones

### Contraseñas de Aplicación

- Use contraseñas de aplicación para Gmail/Yahoo
- No use contraseñas principales de la cuenta
- Revise y rote las contraseñas periódicamente

## 📞 Soporte

Si tiene problemas con la configuración:

1. Revise los logs del servidor
2. Ejecute `python probar_correos.py` para diagnosticar
3. Verifique la configuración SMTP con su proveedor
4. Consulte la documentación de su proveedor de correo

## 🎉 ¡Listo!

Una vez configurado correctamente, el sistema enviará automáticamente correos de notificación cada vez que un administrador rechace una incapacidad, manteniendo a los empleados informados sobre el estado de sus solicitudes.
