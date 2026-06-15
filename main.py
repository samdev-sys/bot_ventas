import os
import re
import json
from flask import Flask, request

app = Flask(__name__)

# ⚠️ REEMPLAZA ESTE LINK CON EL LINK REAL DE TU WHATSAPP BUSINESS DE COLOMBIA (Ej: https://wa.me/c/573XXXXXXXXX)
LINK_CATALOGO = "https://wa.me/c/176231148474470"

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
    texto_lower = texto.lower()
    if "cadena" in texto_lower or "gargantilla" in texto_lower: return "cadenas"
    if "arete" in texto_lower or "topo" in texto_lower or "earcuff" in texto_lower: return "aretes"
    if "anillo" in texto_lower: return "anillos"
    if "pulsera" in texto_lower or "brazalete" in texto_lower: return "pulseras"
    if "relicario" in texto_lower: return "relicarios"
    return None

# Base de datos local simulada con el inventario real para mostrar en texto natural
INVENTARIO = {
    "cadenas": [
        "✨ Cadena con Nombre Personalizada (Plata/Oro Lam) - $75.000",
        "✨ Set de Cadena y Topos clásicos - $45.000",
        "✨ Gargantillas tejidas a mano - $38.000"
    ],
    "aretes": [
        "✨ Aretes Maxi-Largos en Acero - $28.000",
        "✨ Aretes en Rodio antialérgico - $22.000",
        "✨ Set de Topos X2 y X3 - $18.000"
    ],
    "anillos": [
        "✨ Anillos ajustables minimalistas - $15.000",
        "✨ Anillos con incrustaciones de strass - $24.000"
    ],
    "pulseras": [
        "✨ Pulseras para Parejas y Amigos (Set x2) - $25.000",
        "✨ Brazaletes rígidos en Rodio - $32.000"
    ]
}

@app.route("/", methods=["GET"])
def home():
    return "Bot de WhatsApp Activo y en Línea ✅", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        incoming_msg = request.form.get("Body", "").strip()
        intencion = detectar_intencion(incoming_msg)
        
        print(f"--- MSG CLIENTE: {incoming_msg} | INTENCION: {intencion} ---")
        
        xml_response = '<?xml version="1.0" encoding="UTF-8"?><Response>'
        
        # 1. FLUJO DE BIENVENIDA / SALUDO
        if intencion == "saludo":
            xml_response += (
                f'<Message>'
                f'¡Hola! ✨ Bienvenido a Sofia Vasquez Accesorios. 💖 '
                f'Es un placer saludarte. Todas nuestras piezas son hechas a mano con mucho amor.\n\n'
                f'Cuéntame, ¿qué tipo de accesorio estás buscando hoy? (Cadenas, Aretes, Anillos, Pulseras...) '
                f'Si lo prefieres, puedes mirar todos los diseños con sus fotos en nuestro catálogo aquí: {LINK_CATALOGO}'
                f'</Message>'
            )

        # 2. FLUJO DE DETALLE: TRAER LOS ARTÍCULOS CONSULTADOS
        elif intencion in ["precio", "foto", "consulta"]:
            categoria = obtener_id_producto_real(incoming_msg)
            
            if categoria and categoria in INVENTARIO:
                lista_articulos = "\n".join(INVENTARIO[categoria])
                xml_response += (
                    f'<Message>'
                    f'¡Por supuesto! 😍 Aquí tienes los artículos disponibles en la categoría de *{categoria.capitalize()}* con sus precios:\n\n'
                    f'{lista_articulos}\n\n'
                    f'Puedes ver las fotos detalladas de cada referencia en nuestro catálogo ingresando aquí: {LINK_CATALOGO}\n\n'
                    f'¿Cuál de estos te enamoró? Escríbeme el nombre o pon *"Quiero comprar"* para reservártelo de inmediato. ✨'
                    f'</Message>'
                )
            else:
                xml_response += (
                    f'<Message>'
                    f'¡Con muchísimo gusto te ayudo! 😊 ¿De qué tipo de accesorio te gustaría conocer las referencias? '
                    f'Manejamos Cadenas, Aretes, Anillos y Pulseras. '
                    f'También puedes explorar toda la tienda completa ingresando aquí: {LINK_CATALOGO}'
                    f'</Message>'
                )

        # 3. FLUJO DE COMPRA Y PROCESO DE PAGO
        elif intencion == "compra":
            xml_response += (
                f'<Message>'
                f'¡Excelente elección! 🛍️ Me encargaré de separar tus piezas de inmediato para asegurar tu pedido.\n\n'
                f'Para organizar tu envío el día de hoy, por favor ayúdame con estos datos básicos:\n'
                f'1. Nombre completo\n'
                f'2. Ciudad y Dirección de entrega\n'
                f'3. Teléfono de contacto\n\n'
                f'Respecto al pago, ¿cómo te queda más fácil? Aceptamos transferencias directas (*Bancolombia, Nequi o Daviplata*) o si prefieres, te puedo generar un *link de pago seguro* para tarjeta de crédito. 💳'
                f'</Message>'
            )

        # FALLBACK SEGURO
        else:
            xml_response += (
                f'<Message>'
                f'¡Hola! ✨ Te invito a conocer todos nuestros diseños exclusivos con sus respectivos precios en nuestro catálogo de WhatsApp: {LINK_CATALOGO}\n\n'
                f'Escríbeme qué accesorio buscas o avísame si deseas concretar tu compra para ayudarte con gusto. 💖'
                f'</Message>'
            )

        xml_response += '</Response>'
        return xml_response, 200, {'Content-Type': 'text/xml'}

    except Exception as e:
        print(f"❌ ERROR EN WEBHOOK: {str(e)}")
        return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>Hola, estamos presentando un breve inconveniente técnico. En un momento un asesor humano te guiará con tu compra.</Message></Response>', 500, {'Content-Type': 'text/xml'}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)