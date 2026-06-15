import os
import re
import json
from flask import Flask, request

app = Flask(__name__)

# Enlace directo al catálogo general de WhatsApp Business de tu marca
LINK_CATALOGO = "https://wa.me/c/573103632461"

# Diccionarios de palabras clave para el Procesamiento de Lenguaje Natural básico
SALUDOS = ["hola", "buenas", "buen día", "buenas tardes", "buenos días", "qué tal", "hey", "info", "información"]
PRECIO_KEYWORDS = ["precio", "cuánto", "costo", "vale", "cuesta", "precios", "valor"]
FOTO_KEYWORDS = ["foto", "imagen", "ver", "muestra", "diseño", "referencia", "cómo son", "fotos", "catálogo", "catalogo"]
COMPRA_KEYWORDS = ["comprar", "quiero", "ordenar", "pedido", "compro", "llevo", "me interesa", "separar", "pago"]

def detectar_intencion(texto):
    texto_lower = texto.lower()
    if any(p in texto_lower for p in PRECIO_KEYWORDS): return "precio"
    if any(f in texto_lower for f in FOTO_KEYWORDS): return "foto"
    if any(c in texto_lower for c in COMPRA_KEYWORDS): return "compra"
    if any(s in texto_lower for s in SALUDOS): return "saludo"
    return "consulta"

def obtener_id_producto_real(texto):
    """
    Mapea el mensaje del cliente con el nombre exacto de la sección/producto
    en tu catálogo de WhatsApp.
    """
    texto_lower = texto.lower()
    
    # Búsquedas específicas primero
    if "cadena con nombre" in texto_lower: return "Cadena con Nombre Personalizada"
    if "pulseras para parejas" in texto_lower or "pulsera para pareja" in texto_lower: return "Pulseras para Parejas y Amigos"
    if "aretes en rodio" in texto_lower: return "Aretes en Rodio"
    if "aretes largos" in texto_lower: return "Aretes Maxi-Largos en Acero"
    if "marcacion laser" in texto_lower or "marcación laser" in texto_lower: return "Accesorios con Marcación en Láser"
    if "topos" in texto_lower: return "Set de Topos (X2 / X3)"
    if "set" in texto_lower: return "Set de Cadena y Topos"
    
    # Categorías generales individuales
    if "cadena" in texto_lower: return "Cadenas"
    if "gargantilla" in texto_lower: return "Gargantillas"
    if "anillo" in texto_lower: return "Anillos"
    if "llavero" in texto_lower: return "Accesorios de Protección y Llaveros"
    if "relicario" in texto_lower: return "Relicarios"
    if "joyero" in texto_lower: return "Joyeros"
    if "pandora" in texto_lower: return "Estilo Pandoras"
    if "brazalete" in texto_lower: return "Brazaletes"
    if "pulsera" in texto_lower: return "Pulseras"
    if "earcuff" in texto_lower: return "Earcuffs"
    if "tobillera" in texto_lower: return "Tobilleras para Dama"
    
    return None

@app.route("/", methods=["GET"])
def home():
    return "Bot de WhatsApp Activo y en Línea ✅", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        incoming_msg = request.form.get("Body", "").strip()
        intencion = detectar_intencion(incoming_msg)
        
        print(f"--- MSG CLIENTE: {incoming_msg} | INTENCION: {intencion} ---")
        
        # Iniciamos la respuesta nativa XML de Twilio
        xml_response = '<?xml version="1.0" encoding="UTF-8"?><Response>'
        
        # 1. PASO: EL CLIENTE SALUDA ("Hola")
        if intencion == "saludo":
            xml_response += (
                f'<Message>'
                f'¡Hola! ✨ Bienvenida a Sofia Vasquez Accesorios. 💖 '
                f'Es un placer saludarte. Todas nuestras piezas son hechas a mano con mucho amor. '
                f'¿Qué tipo de accesorio estás buscando hoy? '
                f'Si deseas, puedes explorar toda nuestra colección disponible directamente en nuestro catálogo de WhatsApp aquí: 👇\n\n'
                f'{LINK_CATALOGO}'
                f'</Message>'
            )

        # 2. PASO: EL CLIENTE CONSULTA UN PRODUCTO (Ej: "Cadenas", "Aretes en rodio")
        elif intencion in ["precio", "foto", "consulta"]:
            producto_detectado = obtener_id_producto_real(incoming_msg)
            
            if producto_detectado:
                xml_response += (
                    f'<Message>'
                    f'¡Por supuesto! ✨ Toda nuestra variedad de *{producto_detectado}* (con fotos, precios detallados y disponibilidad para entrega inmediata) '
                    f'la puedes ver organizada directamente en nuestra tienda de WhatsApp haciendo clic en este enlace: 👇\n\n'
                    f'{LINK_CATALOGO}\n\n'
                    f'Cuando encuentres el diseño que te enamore, agrégalo al carrito o envíamelo por aquí para prepararte el pedido. 🥰'
                    f'</Message>'
                )
            else:
                # Respuesta de ayuda si menciona algo general o no registrado explícitamente
                xml_response += (
                    f'<Message>'
                    f'¡Con muchísimo gusto te ayudo! 😊 ¿De qué accesorio en específico te gustaría ver fotos o precios? '
                    f'Recuerda que puedes ver todas nuestras categorías completas en cualquier momento entrando a nuestra tienda aquí: 👇\n\n'
                    f'{LINK_CATALOGO}'
                    f'</Message>'
                )

        # 3. PASO: ACOMPAÑAR EL PROCESO DE COMPRA HASTA EL PAGO
        elif intencion == "compra":
            xml_response += (
                f'<Message>'
                f'¡Excelente elección! 🛍️ Me encargaré de separar tus piezas de inmediato para que nadie más las lleve. '
                f'Para proceder con el despacho de tu pedido, por favor confírmame:\n\n'
                f'1. ¿Cuál es tu nombre completo?\n'
                f'2. ¿A qué ciudad y dirección realizamos el envío?\n\n'
                f'Con respecto al pago, ¿prefieres realizar una transferencia directa (Bancolombia/Nequi/Daviplata) o prefieres que te genere un link de pago rápido para tarjeta? 💳'
                f'</Message>'
            )

        # FALLBACK SEGURO (Por si escribe algo fuera del contexto para guiarlo con amabilidad)
        else:
            xml_response += (
                f'<Message>'
                f'¡Hola! ✨ Para brindarte una mejor asesoría sobre nuestras joyas hechas a mano, '
                f'te invito a conocer todos los diseños disponibles con sus respectivos precios en nuestro catálogo de WhatsApp: 👇\n\n'
                f'{LINK_CATALOGO}\n\n'
                f'Escríbeme el nombre del accesorio que te gusta o avísame si deseas concretar tu compra. 💖'
                f'</Message>'
            )

        xml_response += '</Response>'
        return xml_response, 200, {'Content-Type': 'text/xml'}

    except Exception as e:
        print(f"❌ ERROR EN WEBHOOK: {str(e)}")
        return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>Hola, estamos presentando un breve inconveniente. En un momento te atenderá un asesor humano.</Message></Response>', 500, {'Content-Type': 'text/xml'}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)