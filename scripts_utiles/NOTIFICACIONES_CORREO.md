# Configuración de Notificaciones por Correo

## Variables de Entorno Requeridas

Para habilitar el envío de correos cuando se rechace una incapacidad, configure las siguientes variables de entorno:

### Configuración SMTP

```bash
# Servidor SMTP (ejemplo para Gmail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Credenciales de correo
SMTP_USERNAME=tu_email@gmail.com
SMTP_PASSWORD=tu_app_password
FROM_EMAIL=tu_email@gmail.com
```

### Configuración para Gmail

1. **Habilitar autenticación de 2 factores** en tu cuenta de Gmail
2. **Generar una contraseña de aplicación**:
   - Ve a Configuración de Google → Seguridad
   - Selecciona "Contraseñas de aplicaciones"
   - Genera una nueva contraseña para "Correo"
   - Usa esta contraseña como `SMTP_PASSWORD`

### Configuración para otros proveedores

#### Outlook/Hotmail
```bash
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

#### Yahoo
```bash
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
```

#### Servidor SMTP personalizado
```bash
SMTP_SERVER=tu_servidor_smtp.com
SMTP_PORT=587  # o 465 para SSL
```

## Funcionamiento

Cuando un administrador rechace una incapacidad:

1. **Se actualiza el estado** de la incapacidad a 50 (rechazada)
2. **Se guarda el motivo** del rechazo en la base de datos
3. **Se envía automáticamente un correo** al empleado con:
   - Detalles de la incapacidad rechazada
   - Motivo del rechazo
   - Información del administrador que rechazó
   - Fecha y hora del rechazo

## Formato del Correo

El correo incluye:
- **Asunto**: "❌ Incapacidad Rechazada - [Nombre del Empleado]"
- **Contenido HTML** con diseño profesional
- **Versión de texto plano** para compatibilidad
- **Información completa** de la incapacidad y motivo del rechazo

## Logs

Todas las notificaciones se registran en los logs del servidor con el formato:
```
📧 ENVIANDO NOTIFICACIÓN DE RECHAZO:
   📧 Para: empleado@empresa.com
   👤 Empleado: Juan Pérez
   🆔 Incapacidad ID: 123
   ❌ Motivo del rechazo: Documentación incompleta
   👨‍💼 Rechazado por: Admin Usuario
   📅 Fecha: 2024-01-15T10:30:00
```

## Solución de Problemas

### Error de autenticación SMTP
- Verifica que las credenciales sean correctas
- Para Gmail, usa contraseñas de aplicación, no tu contraseña normal
- Asegúrate de que la autenticación de 2 factores esté habilitada

### Correos no se envían
- Revisa los logs del servidor para errores específicos
- Verifica la configuración de firewall/proxy
- Confirma que el puerto SMTP esté abierto

### Correos van a spam
- Configura SPF, DKIM y DMARC en tu dominio
- Usa un correo corporativo en lugar de Gmail personal
- Incluye información de contacto válida en el correo
