import os
import re
import json  # Necesario para procesar la estructura interactiva de WhatsApp
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# ID real de tu catálogo de WhatsApp verificado en Meta
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
    """
    Mapeo de palabras clave jerárquico. Las frases más largas y específicas
    deben evaluarse PRIMERO para evitar que palabras genéricas las intercepten.
    """
    texto_lower = texto.lower()
    
    # 1. Evaluamos términos compuestos y específicos primero
    if "cadena con nombre" in texto_lower: 
        return "CADENA CON NOMBRE"
    elif "pulseras para parejas" in texto_lower or "pulsera para pareja" in texto_lower: 
        return "Parejas.-Amig@s"
    elif "aretes en rodio" in texto_lower: 
        return "aretes Rddio"
    elif "aretes largos" in texto_lower: 
        return "aretes maxi-largos en acero"
    elif "marcacion laser" in texto_lower or "marcación laser" in texto_lower: 
        return "Acces.Marcacion en láser"
    elif "topos" in texto_lower: 
        return "Topos en set X2,X3"
    elif "set" in texto_lower: 
        return "set De Cadena y Topos"
    
    # 2. Evaluamos categorías generales individuales
    elif "cadena" in texto_lower: 
        return "CADENAS"
    elif "gargantilla" in texto_lower: 
        return "GARGANTILLAS"
    elif "anillo" in texto_lower: 
        return "ANILLOS"
    elif "llavero" in texto_lower: 
        return "Accesorios de protección"
    elif "relicario" in texto_lower: 
        return "RELICARIO"
    elif "joyero" in texto_lower: 
        return "JOYEROS"
    elif "pandora" in texto_lower: 
        return "PANDORAS"
    elif "brazalete" in texto_lower: 
        return "Brazaletes"
    elif "pulsera" in texto_lower: 
        return "Pulseras"
    elif "earcuff" in texto_lower: 
        return "Earcuffs"
    elif "tobillera" in texto_lower: 
        return "tobilleras Dama"
        
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
        
        resp = MessagingResponse()
        
        # 1. FLUJO DE BIENVENIDA O CONSULTA GENERAL
        if intencion == "saludo":
            msg = resp.message("¡Hola! ✨ Bienvenida a nuestra tienda de accesorios. 💖 Te invito a explorar todas nuestras piezas exclusivas directamente en nuestro catálogo:")
            payload_catalogo = {
                "type": "interactive",
                "interactive": {
                    "type": "catalog_message",
                    "action": {"name": "catalog_message"}
                }
            }
            # Sintaxis universal compatible con el árbol TwiML de Twilio
            msg.add_child('Parameter', name='wrapped_body', value=f"whatsapp:{json.dumps(payload_catalogo)}")
            return str(resp)

        # 2. FLUJO DE DETALLE (Productos del Catálogo)
        if intencion in ["precio", "foto", "consulta"]:
            product_retailer_id = obtener_id_producto_real(incoming_msg)
            
            if product_retailer_id:
                msg = resp.message("¡Por supuesto! Aquí tienes la información y la imagen directamente de nuestro catálogo de WhatsApp: ✨")
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
                msg.add_child('Parameter', name='wrapped_body', value=f"whatsapp:{json.dumps(payload_producto)}")
                return str(resp)
            else:
                resp.message("¡Con gusto te ayudo! 😊 ¿De qué accesorio te gustaría ver la foto o el precio? Recuerda que también puedes ver la tienda completa aquí: https://wa.me/c/176231148474470")
                return str(resp)

        # 3. FLUJO DE COMPRA
        if intencion == "compra":
            resp.message("¡Excelente elección! 🛍️ El artículo se añadirá a tu carrito. ¿Prefieres realizar el pago por transferencia bancaria o te genero un link de pago rápido?")
            return str(resp)

        # Fallback por defecto (Si no entiende la intención, envía texto plano estable)
        resp.message("¡Hola! ✨ Te invito a revisar nuestras piezas hechas a mano directamente en nuestro catálogo de WhatsApp aquí: https://wa.me/c/176231148474470 👇")
        return str(resp)

    except Exception as e:
        print(f"❌ ERROR EN WEBHOOK: {str(e)}")
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)