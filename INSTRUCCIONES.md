# Instrucciones del Bot de WhatsApp - Sofiaccesorios

## Qué es este bot

Un asistente virtual ("Sofi") que atiende clientes por WhatsApp las 24 horas, mostrando el catálogo de bisutería artesanal, precios, y ayudando a cerrar ventas.

---

## Para el equipo (configuración)

### 1. Variables de entorno (`.env`)

```
GROQ_API_KEY=gsk_tu_api_key_aqui      # Obtener en https://console.groq.com
TWILIO_ACCOUNT_SID= tu_sid             # Obtener en https://console.twilio.com
TWILIO_AUTH_TOKEN= tu_token            # Mismo lugar
PORT=5000
```

### 2. Deploy en Railway

1. Subir el código a un repositorio GitHub
2. Conectar el repositorio en [Railway](https://railway.app)
3. Agregar las variables de entorno en Railway → Variables
4. Railway desplegará automáticamente usando el `Procfile`

### 3. Configurar Twilio

1. Ir a [Twilio Console](https://console.twilio.com)
2. Activar WhatsApp Sandbox
3. En **Sandbox Configuration** configurar:
   - `When a message comes in`: `https://botventas-production-72ae.up.railway.app/webhook` (POST)
   - `Status callback URL`: `https://botventas-production-72ae.up.railway.app/status` (POST)
4. Guardar cambios

### 4. Unirse al Sandbox

Los clientes (y tú para pruebas) deben enviar al número de Twilio (+14155238886):
```
join upper-section
```

---

## Para los clientes (uso)

### Cómo empezar

1. Enviar un mensaje al número de WhatsApp del bot
2. El bot responde automáticamente como "Sofi"
3. Preguntar por los productos que te interesan

### Qué puedes preguntar

| Ejemplo de mensaje | Qué hace el bot |
|---|---|
| `Hola` | Saluda y te da la bienvenida |
| `¿Qué accesorios tienen?` | Lista todas las categorías disponibles |
| `Muéstrame las cadenas` | Muestra cadenas con precios |
| `¿Cuánto cuestan los aretes?` | Da precios de aretes |
| `Quiero comprar una pulsera` | Te guía para hacer el pedido |
| `¿Tienen foto de los collares?` | Te envía el link del catálogo |

### Productos disponibles

- **Cadenas**: Oso articulado, cruz, chokers, gargantillas, camándulas, nombres personalizados
- **Anillos**: Chunky dorados, serpiente, geométricos
- **Tobilleras**: San Benito, 7 nudos, amuleto
- **Relicarios**: En acero para fotos
- **Aretes**: Candongas, earcuffs, topos, aretes de mano
- **Joyeros**: Cuadrados, redondos, corazón, con espejo
- **Pulseras**: Pandora, brazalete Cartier, parejas, neopreno

### Formas de pago

- Transferencia directa: Bancolombia, Nequi, Daviplata
- Link de pago para tarjeta de crédito

### Datos que te pedirá el bot para el envío

1. Nombre completo
2. Ciudad
3. Dirección de entrega
4. Teléfono

### Catálogo con fotos

En cualquier momento puedes ver fotos y precios en el catálogo oficial:
https://wa.me/c/573103632461

---

## Comandos útiles

| Comando | Acción |
|---|---|
| `!limpiar <cantidad>` | Elimina mensajes del canal (requiere permisos) |
| `!expulsar @miembro` | Expulsa a un miembro (requiere permisos) |
| `!banear @miembro` |banea a un miembro (requiere permisos) |

---

## Solución de problemas

### El bot no responde
1. Verificar que el webhook en Twilio apunte a la URL correcta de Railway
2. Revisar los logs de Railway para errores
3. Asegurarse de haber enviado `join upper-section` al número de Twilio

### El bot responde lento
- El bot usa Groq API que generalmente responde en 1-3 segundos
- Si tarda más, verificar el estado de Groq en https://status.groq.com

### Error de API Key
1. Ir a https://console.groq.com
2. Crear una API key nueva
3. Copiarla al archivo `.env` como `GROQ_API_KEY`
