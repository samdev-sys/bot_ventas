import os
import re
import json
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

ID_CATALOGO_REAL = "281899983118355"

SALUDOS = ["hola", "buenas", "buen día", "buenas tardes", "buenos días", "qué tal", "hey"]
PRECIO_KEYWORDS = ["precio", "cuánto", "costo", "vale", "cuesta", "precios"]
FOTO_KEYWORDS = ["foto", "imagen", "ver", "muestra", "diseño", "referencia", "cómo son", "fotos"]
COMPRA_KEYWORDS = ["comprar", "quiero", "ordenar", "pedido", "compro", "llevo"]

def detectar_intencion(texto):
    texto_lower = texto.lower()
    if any(p in texto_lower for p in PRECIO_KEYWORDS): return "precio"
    if any(f in texto_lower for f in FOTO_KEYWORDS): return "foto"
    if any(c in texto_lower for c in COMPRA_KEYWORDS): return "compra"
    if any(s in texto_lower for s in SALUDOS): return "saludo"
    return "consulta"

def obtener_id_producto_real(texto):
    texto_lower = texto.lower()
    if "cadena con nombre" in texto_lower: return "CADENA CON NOMBRE"
    elif "pulseras para parejas" in texto_lower or "pulsera para pareja" in texto_lower: return "Parejas.-Amig@s"
    elif "aretes en rodio" in texto_lower: return "aretes Rddio"
    elif "aretes largos" in texto_lower: return "aretes maxi-largos en acero"
    elif "marcacion laser" in texto_lower or "marcación laser" in texto_lower: return "Acces.Marcacion en láser"
    elif "topos" in texto_lower: return "Topos en set X2,X3"
    elif "set" in texto_lower: return "set De Cadena y Topos"
    elif "cadena" in texto_lower: return "CADENAS"
    elif "gargantilla" in texto_lower: return "GARGANTILLAS"
    elif "anillo" in texto_lower: return "ANILLOS"
    elif "llavero" in texto_lower: return "Accesorios de protección"
    elif "relicario" in texto_lower: return "RELICARIO"
    elif "joyero" in texto_lower: return "JOYEROS"
    elif "pandora" in texto_lower: return "PANDORAS"
    elif "brazalete" in texto_lower: return "Brazaletes"
    elif "pulsera" in texto_lower: return "Pulseras"
    elif "earcuff" in texto_lower: return "Earcuffs"
    elif "tobillera" in texto_lower: return "tobilleras Dama"
    return None

@app.route("/", methods=["GET"])
def home():
    return "Bot de WhatsApp Activo y en Línea ✅", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        incoming_msg = request.form.get("Body", "").strip()
        intencion = detectar_intencion(incoming_msg)
        
        print(f"--- MSG: {incoming_msg} | INTENCION: {intencion} ---")
        
        # Construiremos la respuesta de forma manual para evitar limitaciones de la librería
        xml_response = '<?xml version="1.0" encoding="UTF-8"?><Response>'
        
        # 1. FLUJO DE BIENVENIDA O CONSULTA GENERAL
        if intencion == "saludo":
            payload_catalogo = {
                "type": "interactive",
                "interactive": {
                    "type": "catalog_message",
                    "action": {"name": "catalog_message"}
                }
            }
            xml_response += (
                f'<Message>'
                f'¡Hola! ✨ Bienvenida a nuestra tienda de accesorios. 💖 Te invito a explorar todas nuestras piezas exclusivas directamente en nuestro catálogo:'
                f'<Parameter name="wrapped_body" value="whatsapp:{json.dumps(payload_catalogo)}"/>'
                f'</Message>'
            )

        # 2. FLUJO DE DETALLE (Productos del Catálogo)
        elif intencion in ["precio", "foto", "consulta"]:
            product_retailer_id = obtener_id_producto_real(incoming_msg)
            
            if product_retailer_id:
                payload_producto = {
                    "type": "interactive",
                    "interactive": {
                        "type": "product",
                        "action": {
                            "catalog_id": ID_CATALOGO_REAL,
                            "product_retailer_id": product_retailer_id
                        }
                    }
                }
                xml_response += (
                    f'<Message>'
                    f'¡Por supuesto! Aquí tienes la información y la imagen directamente de nuestro catálogo de WhatsApp: ✨'
                    f'<Parameter name="wrapped_body" value="whatsapp:{json.dumps(payload_producto)}"/>'
                    f'</Message>'
                )
            else:
                xml_response += '<Message>¡Con gusto te ayudo! 😊 ¿De qué accesorio te gustaría ver la foto o el precio? Recuerda que también puedes ver la tienda completa aquí: https://wa.me/c/176231148474470</Message>'

        # 3. FLUJO DE COMPRA
        elif intencion == "compra":
            xml_response += '<Message>¡Excelente elección! 🛍️ El artículo se añadirá a tu carrito. ¿Prefieres realizar el pago por transferencia bancaria o te genero un link de pago rápido?</Message>'

        # Fallback seguro por defecto si no entiende nada
        else:
            xml_response += '<Message>¡Hola! ✨ Te invito a revisar nuestras piezas hechas a mano directamente en nuestro catálogo de WhatsApp aquí: https://wa.me/c/176231148474470 👇</Message>'

        xml_response += '</Response>'
        
        # Retornamos la respuesta XML con el tipo de contenido correcto para Twilio
        return xml_response, 200, {'Content-Type': 'text/xml'}

    except Exception as e:
        print(f"❌ ERROR EN WEBHOOK: {str(e)}")
        return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>Error interno del servidor</Message></Response>', 500, {'Content-Type': 'text/xml'}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)