import os
from flask import Flask, request
from groq import Groq  # Importamos la librería oficial de Groq

app = Flask(__name__)

# Inicializamos el cliente de Groq leyendo la variable de entorno de Railway
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Enlace real de tu catálogo de WhatsApp Business
LINK_CATALOGO = "https://wa.me/c/573103632461"

# Inventario optimizado para ahorro de tokens
CATALOGO_PRODUCTOS = {
    "c_m_oso": {"n": "Cadena Maxi Oso Articulado", "p": "$28.000", "cat": "cad", "d": "Dije grande. Rodio."},
    "c_oso_e": {"n": "Cadena Oso Articulado Estándar", "p": "$28.000", "cat": "cad", "d": "Movimiento sutil. Rodio."},
    "c_m_cruz": {"n": "Maxi Cruz Brillante", "p": "$24.000", "cat": "cad", "d": "Modelo Maxi Cruz-Shine. Rodio."},
    "c_n_lisa": {"n": "Cadena Nombre Lisa", "p": "Consultar", "cat": "cad_p", "d": "Personalizada. Letra lisa."},
    "a_chunky": {"n": "Anillos Chunky Dorados", "p": "$15.000", "cat": "an", "d": "Gruesos de tendencia. Rodio."},
    "j_red": {"n": "Joyero Redondo", "p": "$25.000", "cat": "joy", "d": "Compacto. Negro o Verde Menta."}
    # Nota: Puedes expandir este JSON con los demás productos manteniendo esta estructura compacta
}

# MENSAJE DE BIENVENIDA ESTÁTICO (Evita gasto de tokens en saludos)
MENSAJE_BIENVENIDA = """¡Hola! 🌟 Bienvenidas a *Sofia Vasquez Accesorios* 💖. Estoy aquí para ayudarte a elegir tus joyas favoritas de forma rápida.

*¿Qué puedes hacer conmigo?*
1️⃣ *Consultar productos:* Escribe el tipo de accesorio que buscas (ej. cadenas, anillos, joyeros).
2️⃣ *Ver fotos y modelos:* Si quieres ver el catálogo visual con fotos detalladas, haz clic aquí: """ + LINK_CATALOGO + """ ✨.
3️⃣ *Comprar:* Cuando te decidas por algo, dime el nombre o número del producto y la cantidad.

📌 *Nota: Si tienes una duda muy específica, deseas personalizar una prenda o necesitas soporte, solo pídelo y te transferiré con un asesor humano. 🥰*"""

# SYSTEM PROMPT CORREGIDO (Sin F-String peligroso)
SYSTEM_PROMPT = """
Eres "Sofii", la asistente virtual experta en ventas de 'Sofia Vasquez Accesorios'. Tu objetivo es atender con amabilidad, naturalidad, entusiasmo y un tono muy femenino, usando emojis de forma estética (✨, 💖, 🛍️, 🥰).

Usa la siguiente base de datos (n=nombre, p=precio, cat=categoría, d=descripción):
""" + str(CATALOGO_PRODUCTOS) + """

REGLAS DE INTERACCIÓN:
1. Si el cliente pregunta por una categoría, lístale de forma muy ordenada los productos disponibles de esa categoría con sus precios y compártele SIEMPRE este link exacto para ver fotos: """ + LINK_CATALOGO + """
2. Si el cliente muestra interés en comprar o dice "quiero ordenar/llevar", acompáñalo con entusiasmo y pídele de forma clara los siguientes datos para el envío: Nombre completo, Ciudad, Dirección y Teléfono.
3. Explícale que para el pago puede hacer transferencia directa (Bancolombia, Nequi, Daviplata) o link de pago seguro. 💳
4. Si pide un producto con precio "Consultar" o requiere atención humana, confirma amablemente que un asesor tomará el caso y añade la etiqueta: [TRANSFERIR_A_HUMANO]
5. Mantén tus respuestas cortas y directas para WhatsApp. No inventes productos.
"""

@app.route("/", methods=["GET"])
def home():
    return "Bot de WhatsApp con IA (Groq) Activo y en Línea ✅", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        # Recuperamos y blindamos el mensaje contra valores nulos
        body_raw = request.form.get("Body", "")
        if body_raw is None:
            body_raw = ""
            
        incoming_msg = body_raw.strip()
        incoming_msg_lower = incoming_msg.lower()

        if not incoming_msg:
            return "No message body", 400

        print(f"--- MSG CLIENTE: {incoming_msg} ---")

        # Intercepción rápida de saludos comunes para ahorrar tokens
        SALUDOS = ["hola", "buenas", "buenos dias", "buenas tardes", "buenas noches", "hola!", "inicio"]
        if incoming_msg_lower in SALUDOS:
            xml_response = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{MENSAJE_BIENVENIDA}</Message></Response>'
            return xml_response, 200, {'Content-Type': 'text/xml'}

        # Llamamos a Groq usando el modelo correcto y vigente
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": incoming_msg}
            ],
            model="llama-3.1-8b-instant",  # <--- CAMBIO CLAVE: Modelo vigente
            temperature=0.6,
            max_tokens=300
        )

        bot_response = chat_completion.choices[0].message.content

        # Remover la bandera técnica si la IA la añade
        if "[TRANSFERIR_A_HUMANO]" in bot_response:
            bot_response = bot_response.replace("[TRANSFERIR_A_HUMANO]", "").strip()

        # Construimos el XML nativo de Twilio
        xml_response = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Response>'
            f'<Message>{bot_response}</Message>'
            '</Response>'
        )
        
        return xml_response, 200, {'Content-Type': 'text/xml'}

    except Exception as e:
        print(f"❌ ERROR EN WEBHOOK CON GROQ: {str(e)}")
        fallback_msg = "¡Hola! ✨ En este momento tengo un flujo muy alto de mensajes, pero déjame tu consulta y un asesor humano te atenderá de inmediato para ayudarte con tu pedido. 💖"
        return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{fallback_msg}</Message></Response>', 500, {'Content-Type': 'text/xml'}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)