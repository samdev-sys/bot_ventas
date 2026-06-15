import os
import json
from flask import Flask, request
from groq import Groq  # Importamos la librería oficial de Groq

app = Flask(__name__)

# Inicializamos el cliente de Groq leyendo la variable de entorno de Railway
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Enlace real de tu catálogo de WhatsApp Business
LINK_CATALOGO = "https://wa.me/c/176231148474470"

# El System Prompt le da la personalidad, las reglas y el inventario a la IA
SYSTEM_PROMPT = f"""
Eres "Sofi", la asistente virtual experta en ventas de 'Sofia Vasquez Accesorios'. Tu objetivo es atender con amabilidad, naturalidad, entusiasmo y un tono muy femenino, usando emojis de forma estética (✨, 💖, 🛍️, 🥰).

CONOCIMIENTO DE INVENTARIO Y PRECIOS:
- Cadenas: Cadena con Nombre Personalizada (Plata/Oro Lam) - $75.000 | Set de Cadena y Topos clásicos - $45.000 | Gargantillas tejidas a mano - $38.000.
- Aretes: Aretes Maxi-Largos en Acero - $28.000 | Aretes en Rodio antialérgico - $22.000 | Set de Topos X2 y X3 - $18.000.
- Anillos: Anillos ajustables minimalistas - $15.000 | Anillos con incrustaciones de strass - $24.000.
- Pulseras: Pulseras para Parejas y Amigos (Set x2) - $25.000 | Brazaletes rígidos en Rodio - $32.000.

REGLAS DE INTERACCIÓN:
1. Si el cliente saluda, dale una cálida bienvenida e infórmale que todo es hecho a mano con amor. Pregúntale qué accesorio busca hoy.
2. Si pregunta por una categoría (ej. Cadenas), lístale de forma muy ordenada los productos disponibles de esa categoría con sus precios y compártele SIEMPRE este link exacto para ver fotos: {LINK_CATALOGO}
3. Si el cliente muestra interés en comprar o dice "quiero ordenar/llevar", acompáñalo con entusiasmo y pídele de forma clara los siguientes datos para el envío:
   - Nombre completo
   - Ciudad y dirección de entrega
   - Teléfono
4. Explícale que para el pago puede hacer transferencia directa (Bancolombia, Nequi, Daviplata) o que le puedes generar un link de pago seguro para tarjeta de crédito. 💳
5. Mantén tus respuestas relativamente cortas y directas, ideales para leer en WhatsApp. No inventes productos que no estén en la lista.
"""

@app.route("/", methods=["GET"])
def home():
    return "Bot de WhatsApp con IA (Groq) Activo y en Línea ✅", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        # Recuperamos el mensaje de WhatsApp enviado por el cliente
        incoming_msg = request.form.get("Body", "").strip()
        
        if not incoming_msg:
            return "No message body", 400

        print(f"--- MSG CLIENTE: {incoming_msg} ---")

        # Llamamos a Groq usando un modelo ultra rápido y económico (Llama 3 8B)
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": incoming_msg}
            ],
            model="llama3-8b-8192",  # Un modelo veloz y excelente para seguir instrucciones
            temperature=0.6,          # Balance ideal entre creatividad y apego a las reglas
            max_tokens=300            # Evita respuestas innecesariamente largas para WhatsApp
        )

        # Extraemos la respuesta generada por la Inteligencia Artificial
        bot_response = chat_completion.choices[0].message.content

        # Construimos el XML nativo de Twilio con la respuesta de la IA
        xml_response = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Response>'
            f'<Message>{bot_response}</Message>'
            '</Response>'
        )
        
        return xml_response, 200, {'Content-Type': 'text/xml'}

    except Exception as e:
        print(f"❌ ERROR EN WEBHOOK CON GROQ: {str(e)}")
        # Fallback amigable por si la API de Groq llega a tardar o fallar
        return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>¡Hola! ✨ En este momento tengo un flujo muy alto de mensajes, pero déjame tu consulta y un asesor humano te atenderá de inmediato para ayudarte con tu pedido. 💖</Message></Response>', 500, {'Content-Type': 'text/xml'}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)