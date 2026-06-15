import os
from flask import Flask, request, jsonify
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

# TEXTO DE BIENVENIDA QUE SE DISPARA DIRECTO SIN USAR TOKENS DE GROQ
MENSAJE_BIENVENIDA ="""¡Hola! 🌟 Bienvenidas a *Sofia Vasquez Accesorios* 💖. Estoy aquí para ayudarte a elegir tus joyas favoritas de forma rápida.

*¿Qué puedes hacer conmigo?*
1️⃣ *Consultar productos:* Escribe el tipo de accesorio que buscas (ej. cadenas, topos, pulseras).
2️⃣ *Ver fotos y modelos:* Si quieres ver el catálogo visual con fotos detalladas, haz clic aquí: {URL_CATALOGO} ✨.
3️⃣ *Comprar:* Cuando te decidas por algo, dime el nombre o número del producto y la cantidad (ej. Quiero 2 cadenas de oso estándar).

📌 *Nota: Si tienes una duda muy específica, deseas personalizar una prenda con tu nombre o necesitas soporte con un pago, solo pídelo y te transferiré de inmediato con un asesor humano para que te atienda personalmente. 🥰*

¿En qué te puedo ayudar hoy? 💕"""

# SYSTEM PROMPT COMBINADO (TU MENSAJE + LAS REGLAS DE CONTROL)
SYSTEM_PROMPT = """
Eres Sofii, asesora de "Sofia Vasquez Accesorios". Atiende con tono amable, entusiasta y emojis (✨, 🥰, 💖). 
Usa la siguiente base de datos (n=nombre, p=precio, cat=categoría, d=descripción):
""" + str(CATALOGO_PRODUCTOS) + """

REGLAS DE OPERACIÓN:
1. Da precios y detalles exactos basándote en la lista. Si piden fotos o ver colecciones, dales este link: {URL_CATALOGO}
2. Si el precio dice "Consultar" (como las piezas personalizadas), explica que depende del diseño y ponlos en espera agregando al final: [TRANSFERIR_A_HUMANO]
3. Si piden hablar con un asesor real, soporte, humano, o si hacen preguntas complejas que no puedas resolver con los datos del catálogo, diles amablemente que los dejarás en espera y añade EXACTAMENTE la etiqueta: [TRANSFERIR_A_HUMANO]
"""

@app.route("/webhook", methods=["POST"])
def webhook():
    # Aseguramos que si 'Body' no existe, sea un string vacío antes de aplicar funciones de texto
    body_raw = request.values.get("Body", "")
    if body_raw is None:
        body_raw = ""
        
    incoming_msg = body_raw.strip().lower()
    
    resp = MessagingResponse()
    msg = resp.message()

    # LISTA DE SALUDOS EN MINÚSCULAS
    SALUDOS = ["hola", "buenas", "buenos dias", "buenas tardes", "buenas noches", "hola!", "inicio", "hola sofii"]

    # Si el mensaje coincide con un saludo, disparamos la bienvenida directa
    if incoming_msg in SALUDOS:
        msg.body(MENSAJE_BIENVENIDA)
        return str(resp)

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": body_raw} # Le pasamos el mensaje original a Groq
            ],
            model="llama-3.1-8b-instant",
            temperature=0.6,
        )
        reply_text = chat_completion.choices[0].message.content
        
        if "[TRANSFERIR_A_HUMANO]" in reply_text:
            reply_text = reply_text.replace("[TRANSFERIR_A_HUMANO]", "").strip()

        msg.body(reply_text)

    except Exception as e:
        print(f"Error en Groq: {e}")
        msg.body("¡Hola! ✨ Estamos presentando alta demanda, pero puedes ver fotos y precios de todo nuestro inventario en el catálogo oficial: https://wa.me/c/573103632461 🥰")

    return str(resp)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)