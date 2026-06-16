import os
import time
import html
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from groq import Groq

app = Flask(__name__)

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# CATÁLOGO ULTRA-COMPACTADO PARA AHORRO DE TOKENS
CATALOGO_PRODUCTOS = {
    # Cadenas
    "c_m_oso": {"n": "Cadena Maxi Oso Articulado", "p": "$28.000", "cat": "cad", "d": "Dije grande. Rodio."},
    "c_oso_e": {"n": "Cadena Oso Articulado Estándar", "p": "$28.000", "cat": "cad", "d": "Movimiento sutil. Rodio."},
    "c_m_cruz": {"n": "Maxi Cruz Brillante", "p": "$24.000", "cat": "cad", "d": "Modelo Maxi Cruz-Shine. Rodio."},
    "c_chok1": {"n": "Chokers #1 (unidad)", "p": "$15.000", "cat": "cad", "d": "Gargantilla corta ajustable. Rodio."},
    "c_g_lazo": {"n": "Gargantilla Lazo Mediana", "p": "$28.000", "cat": "cad", "d": "Tejido tipo lazo. Rodio."},
    "c_g_cub": {"n": "Gargantilla Cubana", "p": "$20.000", "cat": "cad", "d": "Eslabón clásico brillante. Rodio."},
    "c_cam_cr": {"n": "Camándula en Cristal", "p": "$18.000", "cat": "cad", "d": "Cuentas de cristal y dijes religiosos."},
    "c_cam_ac": {"n": "Camándula en Acero", "p": "$25.000", "cat": "cad", "d": "Medalla San Benito y cruz. Acero Inox."},
    "c_n_lisa": {"n": "Cadena Nombre Lisa", "p": "Consultar", "cat": "cad_p", "d": "Personalizada. Letra lisa."},
    "c_n_bril": {"n": "Cadena Nombre Brillante", "p": "Consultar", "cat": "cad_p", "d": "Personalizada. Letra brillante."},

    # Anillos
    "a_chunky": {"n": "Anillos Chunky Dorados (unidad)", "p": "$15.000", "cat": "an", "d": "Gruesos de tendencia. Rodio."},
    "a_serp": {"n": "Anillos Serpiente (unidad)", "p": "$18.000", "cat": "an", "d": "Forma de serpiente. Rodio."},
    "a_3grad": {"n": "Anillos 3° (unidad)", "p": "$15.000", "cat": "an", "d": "Diseño geométrico sutil. Rodio."},

    # Tobilleras
    "t_den_sb": {"n": "Tobillera Denario San Benito", "p": "$18.000", "cat": "tob", "d": "Tipo denario. Acero."},
    "t_7nud": {"n": "Tobilleras 7 Nudos", "p": "$8.000", "cat": "tob", "d": "Hilo rojo con dije en acero."},
    "t_amu_sb": {"n": "Tobillera Amuleto San Benito", "p": "$20.000", "cat": "tob", "d": "Ojo turco y medalla. Oro/Plata. Rodio."},

    # Relicarios
    "r_acero": {"n": "Relicarios en Acero (40cm)", "p": "$25.000", "cat": "rel", "d": "Corazón o circular para fotos. Acero."},

    # Aretes, Topos y Earcuffs
    "e_cand_p": {"n": "Candongas de Perlas", "p": "$25.000", "cat": "ar_r", "d": "Medianas con perlas colgantes. Rodio."},
    "e_set_cl": {"n": "Set Candongas Lisas Doradas", "p": "$32.000", "cat": "ar_r", "d": "Variado de candongas lisas. Rodio."},
    "e_set_cb": {"n": "Set Candongas Bolitas", "p": "$40.000", "cat": "ar_r", "d": "Detalles de esferas. Rodio."},
    "e_ear_t": {"n": "Est Earcuffs", "p": "$15.000", "cat": "ear", "d": "Texturizado. Sin perforación. Covergold."},
    "e_ear_e": {"n": "Earcuffs Estilo Eslabón", "p": "$15.000", "cat": "ear", "d": "Diseño cadena. Sin perforación. Covergold."},
    "e_ear_l": {"n": "Earcuffs Lisos Clásicos", "p": "$12.000", "cat": "ear", "d": "Minimalistas pulidos. Sin perforación. Rodio."},
    "e_top_rc": {"n": "Topos Set Rodio Clásicos", "p": "$18.000", "cat": "top_s", "d": "Modelos pequeños combinables. Rodio."},
    "e_top_rv": {"n": "Topos Set Rodio Variados", "p": "$18.000", "cat": "top_s", "d": "Figuras. Set x2 $18k / Set x3 $27k. Rodio."},
    "e_top_d3": {"n": "Topos Set Rodio Dorados x3", "p": "$27.000", "cat": "top_s", "d": "Tres pares dorados premium. Rodio."},
    "e_are_m": {"n": "Aretes Hechos a Mano Corazones", "p": "$18.000", "cat": "ar_m", "d": "Tejido artesanal, base dorada."},
    "e_are_la": {"n": "Aretes Largos en Acero", "p": "$15.000", "cat": "ar_m", "d": "Cadena colgante delgada. Acero dorado."},
    "e_are_bf": {"n": "Aretes Brillantes Fantasía", "p": "$10.000", "cat": "ar_m", "d": "Maxi aretes colgantes con strass."},

    # Joyeros
    "j_cuad_p": {"n": "Joyero Cuadrado Pequeño", "p": "$25.000", "cat": "joy", "d": "Portátil. Sintético texturizado."},
    "j_red": {"n": "Joyero Redondo", "p": "$25.000", "cat": "joy", "d": "Compacto. Negro o Verde Menta."},
    "j_cor": {"n": "Joyero Corazón", "p": "$28.000", "cat": "joy", "d": "Forma corazón. Solo Negro."},
    "j_grad_es": {"n": "Joyero Grande con Espejo", "p": "$45.000", "cat": "joy", "d": "Alta capacidad, compartimentos y cierre."},

    # Pulseras, Brazaletes y Pandoras
    "p_pan_r": {"n": "Pandoras Rodinadas Premium", "p": "Consultar", "cat": "pan", "d": "Balines y dijes de alta calidad. Rodio."},
    "p_pan_ac": {"n": "Pandoras Acero Covergold", "p": "$50.000", "cat": "pan", "d": "Charms variados y cruz. Acero/Covergold."},
    "p_bra_lc": {"n": "Brazalete Love Cartier", "p": "$25.000", "cat": "braz", "d": "Rígido, diseño icónico minimalista. Rodio."},
    "p_bra_ra": {"n": "Brazaletes Rígidos (unidad)", "p": "$20.000", "cat": "braz", "d": "Abierto con nudo central. Rodio."},
    "p_duo_cc": {"n": "Dúo Clavo Cartier", "p": "$20.000", "cat": "braz", "d": "Incluye brazalete rígido y anillo ajustable. Rodio."},
    "p_pul_neo": {"n": "Pulseras Neopreno Parejas", "p": "$25.000", "cat": "par", "d": "Ajustables, balines dorados. Color a elección."},
    "p_pul_dij": {"n": "Pulseras Parejas con Dijes", "p": "$30.000", "cat": "par", "d": "Set x2 de hilo. Dijes complementarios."},
    "p_pul_esp": {"n": "Pulseras Parejas Especiales", "p": "$25.000", "cat": "par", "d": "Set x2 de hilo. Dije corona o esfera."},
    "p_pul_bal": {"n": "Pulsera Balines en Rodio", "p": "$12.000", "cat": "pul", "d": "Balines dorados brillantes. Rodio."}
}

URL_CATALOGO = "https://wa.me/c/573103632461"

WELCOME_MSG = """¡Hola! 🌟 Bienvenidas a Sofia Vasquez Accesorios 💖. Estoy aquí para ayudarte a elegir tus joyas favoritas de forma rápida.

¿Qué puedes hacer conmigo?
1️⃣ Consultar productos: Escribe el tipo de accesorio que buscas (ej. cadenas, topos, pulseras).
2️⃣ Ver fotos y modelos: Si quieres ver el catálogo visual con fotos detalladas, haz clic aquí: """ + URL_CATALOGO + """ ✨.
3️⃣ Comprar: Cuando te decidas por algo, dime el nombre o número del producto y la cantidad (ej. Quiero 2 cadenas de oso estándar).

📌 Nota: Si tienes una duda muy específica, deseas personalizar una prenda con tu nombre o necesitas soporte con un pago, solo pídelo y te transferiré de inmediato con un asesor personalizado para que te atienda personalmente. 🥰

¿En qué te puedo ayudar hoy? 💕"""

SALUDOS = ["hola", "buenas", "buen día", "buenas tardes", "buenos días", "qué tal", "hey", "buenass", "buenos dias"]

SYSTEM_PROMPT = """
Eres "Sofi", la asistente virtual experta en ventas de 'Sofiaccesorios'. Tu objetivo es atender con amabilidad, naturalidad, entusiasmo y un tono muy femenino, usando emojis de forma estética (✨, 💖, 🛍️, 🥰).

MENSAJE DE BIENVENIDA (solo cuando el cliente dice Hola u otro saludo por primera vez):
Envía este mensaje exacto sin modificarlo:
"¡Hola! 🌟 Bienvenidas a Sofia Vasquez Accesorios 💖. Estoy aquí para ayudarte a elegir tus joyas favoritas de forma rápida.

¿Qué puedes hacer conmigo?
1️⃣ Consultar productos: Escribe el tipo de accesorio que buscas (ej. cadenas, topos, pulseras).
2️⃣ Ver fotos y modelos: Si quieres ver el catálogo visual con fotos detalladas, haz clic aquí: https://wa.me/c/573103632461 ✨.
3️⃣ Comprar: Cuando te decidas por algo, dime el nombre o número del producto y la cantidad (ej. Quiero 2 cadenas de oso estándar).

📌 Nota: Si tienes una duda muy específica, deseas personalizar una prenda con tu nombre o necesitas soporte con un pago, solo pídelo y te transferiré de inmediato con un asesor humano para que te atienda personalmente. 🥰

¿En qué te puedo ayudar hoy? 💕"

CONOCIMIENTO DE INVENTARIO Y PRECIOS:
- Cadenas: Cadena Maxi Oso Articulado - $28.000 | Cadena Oso Estándar - $28.000 | Maxi Cruz Brillante - $24.000 | Chokers - $15.000 | Gargantilla Lazo - $28.000 | Gargantilla Cubana - $20.000 | Camándula Cristal - $18.000 | Camándula Acero - $25.000 | Nombre Personalizada (Consultar precio).
- Anillos: Chunky Dorados - $15.000 | Serpiente - $18.000 | 3° Geométrico - $15.000.
- Tobilleras: Denario San Benito - $18.000 | 7 Nudos - $8.000 | Amuleto San Benito - $20.000.
- Relicarios: Acero 40cm - $25.000.
- Aretes: Candongas de Perlas - $25.000 | Set Lisas Doradas - $32.000 | Set Bolitas - $40.000 | Earcuffs - $12.000 a $15.000 | Topos - $18.000 a $27.000 | Hechos a Mano Corazones - $18.000 | Largos Acero - $15.000 | Brillantes Fantasía - $10.000.
- Joyeros: Cuadrado Pequeño - $25.000 | Redondo - $25.000 | Corazón - $28.000 | Grande con Espejo - $45.000.
- Pulseras/Brazaletes: Pandora Rodinadas (Consultar) | Pandora Covergold - $50.000 | Love Cartier - $25.000 | Brazaletes Rígidos - $20.000 | Dúo Clavo Cartier - $20.000 | Neopreno Parejas - $25.000 | Parejas con Dijes - $30.000 | Parejas Especiales - $25.000 | Balines Rodio - $12.000.

REGLAS DE INTERACCIÓN:
1. Si el cliente saluda por primera vez, envía el MENSAJE DE BIENVENIDA exacto.
2. Si pregunta por una categoría (ej. cadenas), lista los productos de esa categoría con precios y comparte SIEMPRE el link del catálogo: https://wa.me/c/573103632461
3. Si el cliente dice "quiero comprar" o "quiero llevar", pide: nombre del producto, cantidad, nombre completo, ciudad, dirección y teléfono.
4. Para el pago indica: transferencia (Bancolombia, Nequi, Daviplata) o link de pago para tarjeta.
5. Mantén respuestas cortas y directas para WhatsApp.

CUÁNDO TRANSFERIR A UN ASESOR HUMANO:
Si el cliente pide algo fuera del catálogo, quiere personalizar un producto con su nombre, tiene problemas con un pago, o hace una pregunta muy específica que no puedes responder, responde:
"Entiendo perfectamente 💖 Para darte la mejor atención con tu solicitud, voy a transferirte con un asesor humano que te atenderá personalmente. En unos momentos te contactará. 🥰"
NO intentes responder preguntas que no están en tu catálogo. Solo transfiere al asesor.
"""

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip()
    from_number = request.values.get("From", "unknown")
    start = time.time()
    print(f"[WEBHOOK] Mensaje de {from_number}: {incoming_msg}")

    resp = MessagingResponse()

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": incoming_msg}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.6,
        )
        reply_text = chat_completion.choices[0].message.content
        reply_text = reply_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        resp.message(reply_text)
        print(f"[WEBHOOK] Respuesta enviada: {reply_text[:80]}...")

    except Exception as e:
        print(f"[WEBHOOK] Error en Groq: {e}")
        resp.message("¡Hola! ✨ Estamos presentando alta demanda, pero puedes ver fotos y precios de todo nuestro inventario en el catálogo oficial: https://wa.me/c/573103632461 🥰")

    elapsed = round(time.time() - start, 2)
    print(f"[WEBHOOK] Respondido en {elapsed}s")
    twiml_str = str(resp)
    print(f"[WEBHOOK] TwiML: {twiml_str}")
    return Response(twiml_str, mimetype="text/xml")


@app.route("/status", methods=["POST"])
def status():
    print(f"[STATUS] Status callback: {request.values}")
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)