import os
import io
import time
import html
import requests
import tempfile
from datetime import datetime
import pytz
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from groq import Groq

app = Flask(__name__)

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# CATÁLOGO ULTRA-COMPACTADO PARA AHORRO DE TOKENS
CATALOGO_PRODUCTOS = {
    # Cadenas / Gargantillas / Chokers
    "c_m_oso": {"n": "Cadena Maxi Oso Articulado", "p": "$28.000", "cat": "cad", "d": "Dije grande. Rodio."},
    "c_oso_e": {"n": "Cadena Oso Articulado Estándar", "p": "$28.000", "cat": "cad", "d": "Movimiento sutil. Rodio."},
    "c_m_cruz": {"n": "Maxi Cruz Brillante", "p": "$24.000", "cat": "cad", "d": "Modelo Maxi Cruz-Shine. Rodio."},
    "c_chok1": {"n": "Chokers #1 (unidad)", "p": "$15.000", "cat": "cad", "d": "Material Rodio. Gargantilla corta ajustable."},
    "c_g_lazo": {"n": "Gargantilla Lazo Mediana", "p": "$28.000", "cat": "cad", "d": "Tejido tipo lazo. Rodio."},
    "c_g_cub": {"n": "Gargantilla Cubana", "p": "$20.000", "cat": "cad", "d": "Eslabón clásico brillante. Rodio."},
    "c_g_vcleef": {"n": "Gargantilla Van Cleef en Rodio", "p": "$22.000", "cat": "cad", "d": "Diseño tréboles Van Cleef estilizados."},
    "c_g_cuarzo": {"n": "Gargantilla en Cuarzo", "p": "$20.000", "cat": "cad", "d": "Material covergold rodinado con cuarzo."},
    "c_col_cord": {"n": "Collares en Cordón", "p": "$18.000", "cat": "cad", "d": "Cordón con dijes variados."},
    "c_d_cor25": {"n": "Cadena Dije Corazón", "p": "$25.000", "cat": "cad", "d": "Dije corazón brillante."},
    "c_d_oturco": {"n": "Cadena Dije Ojo Turco", "p": "$20.000", "cat": "cad", "d": "Baño de rodio con perlas sutiles."},
    "c_d_luna": {"n": "Cadena Dije Luna Rodio", "p": "$18.000", "cat": "cad", "d": "Dije de luna brillante. Rodio."},
    "c_g_choker": {"n": "Gargantilla Choker en Rodio", "p": "$15.000", "cat": "cad", "d": "Estilo choker con dijes colgantes."},
    "c_s_plana": {"n": "Cadena Snake Plana Dorada", "p": "$20.000", "cat": "cad", "d": "Material Acero premium."},
    "c_strass_d": {"n": "Cadena Strass Dorada", "p": "$27.000", "cat": "cad", "d": "Material baño en rodio brillante."},
    "c_m_clip": {"n": "Cadena Maxi Clip", "p": "$22.000", "cat": "cad", "d": "Eslabón tipo clip grande. Baño en rodio."},
    "c_rel_rod": {"n": "Cadenas Religiosas Baño Rodio", "p": "$22.000", "cat": "cad", "d": "Modelos religiosos variados (cruces, medallas)."},
    "c_rel_20": {"n": "Cadenas Religiosas Especiales", "p": "$20.000", "cat": "cad", "d": "Baño de rodio premium."},
    "c_ac_par": {"n": "Cadenas en Acero para Pareja", "p": "$25.000", "cat": "cad_p", "d": "Precio por el par de cadenas."},
    "c_n_lisa": {"n": "Cadena Nombre Lisa", "p": "Consultar", "cat": "cad_p", "d": "Personalizada. Letra lisa."},
    "c_n_bril": {"n": "Cadena Nombre Brillante", "p": "Consultar", "cat": "cad_p", "d": "Personalizada. Letra brillante."},

    # Anillos
    "a_chunky": {"n": "Anillos Chunky Dorados / Rodio", "p": "$15.000", "cat": "an", "d": "Gruesos de tendencia, ajustables."},
    "a_serp": {"n": "Anillos Serpiente (unidad)", "p": "$18.000", "cat": "an", "d": "Forma de serpiente. Rodio."},
    "a_3grad": {"n": "Anillos 3° (unidad)", "p": "$15.000", "cat": "an", "d": "Diseño geométrico sutil. Rodio."},

    # Tobilleras
    "t_den_sb": {"n": "Tobillera Denario San Benito", "p": "$18.000", "cat": "tob", "d": "Material Acero, tipo denario ajustable."},
    "t_7nud": {"n": "Tobilleras 7 Nudos", "p": "$8.000", "cat": "tob", "d": "Hilo rojo con dije en acero."},
    "t_amu_sb": {"n": "Tobillera Amuleto San Benito", "p": "$20.000", "cat": "tob", "d": "Ojo turco y medalla. Oro/Plata. Rodio."},
    "t_ac_dama": {"n": "Tobilleras en Acero Dama", "p": "$18.000", "cat": "tob", "d": "Eslabón delicado brillante en acero."},

    # Sets Completos (Juegos de Cadena + Topos / Combinados)
    "s_juego_v": {"n": "Juego Cadena y Topos Virgen", "p": "$28.000", "cat": "set_c", "d": "Covergold rodinado con medalla religiosa."},
    "s_juego_g": {"n": "Juego Gargantilla y Aretes", "p": "$60.000", "cat": "set_c", "d": "Material rodinado de alta gama con piedras verdes."},
    "s_trebol_r": {"n": "Set Trébol Rojo", "p": "$35.000", "cat": "set_c", "d": "Cadena y topos trébol rojo. Covergold rodinado."},
    "s_mariposa": {"n": "Set Mariposa", "p": "$25.000", "cat": "set_c", "d": "Cadena y topos mariposa. Covergold rodinado."},
    "s_cor_mcirc": {"n": "Set Corazón Microcircón", "p": "$38.000", "cat": "set_c", "d": "Cadena y topos corazón microengastado."},
    "s_g_vcleef40": {"n": "Set Gargantilla Van Cleef Premium", "p": "$40.000", "cat": "set_c", "d": "Covergold rodinado estilo premium."},
    "s_cad_oso25": {"n": "Set Cadena y Topos Oso", "p": "$25.000", "cat": "set_c", "d": "Dije oso. Con pulsera incluida por $35.000."},

    # Aretes, Topos y Candongas
    "e_cand_p": {"n": "Candongas de Perlas", "p": "$25.000", "cat": "ar", "d": "Medianas con perlas colgantes. Rodio."},
    "e_cand_m15": {"n": "Candongas Medianas Básicas", "p": "$15.000", "cat": "ar", "d": "Modelos pulidos medianos."},
    "e_cand_pm": {"n": "Candongas Pequeñas-Medianas", "p": "$12.000", "cat": "ar", "d": "Argollas texturizadas o lisas."},
    "e_cand_m_chu": {"n": "Candonga Mediana Chunky", "p": "$18.000", "cat": "ar", "d": "Estilo grueso texturizado de tendencia."},
    "e_cand_peq15": {"n": "Candongas Pequeñas Especiales", "p": "$15.000", "cat": "ar", "d": "Baño de rodio."},
    "e_ear_l": {"n": "Earcuffs Lisos Clásicos", "p": "$12.000", "cat": "ar", "d": "Minimalistas pulidos. Sin perforación. Rodio."},
    "e_ear_est": {"n": "Est Earcuffs Premium", "p": "$15.000", "cat": "ar", "d": "Covergold rodinado texturizado ancho."},
    "e_orejera": {"n": "Orejera Serpiente", "p": "$18.000", "cat": "ar", "d": "Covergold rodinado con silueta de serpiente."},
    "e_top_r12": {"n": "Topos Pequeños Rodio", "p": "$12.000", "cat": "ar", "d": "Diseños pequeños básicos antialérgicos."},
    "e_top_perl18": {"n": "Topos de Perlas Elegantes", "p": "$18.000", "cat": "ar", "d": "Acabado perlado con marco texturizado."},
    "e_top_rv": {"n": "Topos Set Rodio Variados", "p": "$18.000", "cat": "ar", "d": "Figuras. Set x2 es $18.000 / Set x3 es $27.000."},
    "e_set_c_rod": {"n": "Sets Candongas Rodio", "p": "$30.000", "cat": "ar", "d": "Variedad en sets. Set x2 $20.000 / Set x3 $30.000."},
    "e_m_acer": {"n": "Maxitopos Material Acero", "p": "$15.000", "cat": "ar", "d": "Precio por par. Varias texturas doradas."},

    # Joyeros
    "j_cor": {"n": "Joyero Corazón", "p": "$28.000", "cat": "joy", "d": "Forma corazón. Disponible sólo color negro."},
    "j_cuad_p": {"n": "Joyero Cuadrado Pequeño", "p": "$25.000", "cat": "joy", "d": "Portátil. Sintético texturizado."},
    "j_red": {"n": "Joyero Redondo", "p": "$25.000", "cat": "joy", "d": "Compacto. Negro o Verde Menta."},
    "j_grad_es": {"n": "Joyero Grande con Espejo", "p": "$45.000", "cat": "joy", "d": "Alta capacidad con compartimentos."},

    # Pulseras y Brazaletes
    "p_pul_cord": {"n": "Pulseras Cordón Graduables", "p": "$18.000", "cat": "pul", "d": "Material covergold rodinado con cordón fino."},
    "p_pul_rodg": {"n": "Pulseras Rodio Graduables", "p": "$18.000", "cat": "pul", "d": "Eslabón o balines delgados ajustables."},
    "p_b_snake": {"n": "Brazalete Snake King", "p": "$18.000", "cat": "pul", "d": "Material Rodinado texturizado rígido ajustable."},
    "p_pul_mult": {"n": "Pulseras Multidijes", "p": "$23.000", "cat": "pul", "d": "Cadena delgada con dijes colgantes variados."},
    "p_pul_hilo": {"n": "Pulseras Rodio Hilo", "p": "$18.000", "cat": "pul", "d": "Hilo con balines o dijes centrales en rodio."},
    "p_pul_neo": {"n": "Pulseras Neopreno Parejas", "p": "$25.000", "cat": "pul", "d": "Ajustables, balines dorados."},
    "p_par_peq": {"n": "Pulseras Parejas Pequeñas", "p": "$25.000", "cat": "pul", "d": "Set x2 de hilo ajustable con corona o esfera."},
    "p_pan_r": {"n": "Pandoras Rodinadas Premium", "p": "Consultar", "cat": "pul", "d": "Balines y dijes de alta calidad. Rodio."}
}
URL_CATALOGO = "https://wa.me/c/573103632461"

WELCOME_MSG = """¡Hola! 🌟 Bienvenidas a Sofiiaccesorios 💖. Estoy aquí para ayudarte a elegir tus joyas favoritas de forma rápida.

¿Qué puedes hacer conmigo?
1️⃣ Consultar productos: Escribe el tipo de accesorio que buscas (ej. cadenas, topos, pulseras).
2️⃣ Ver fotos y modelos: Si quieres ver el catálogo visual con fotos detalladas, haz clic aquí: """ + URL_CATALOGO + """ ✨.
3️⃣ Comprar: Cuando te decidas por algo, dime el nombre o número del producto y la cantidad (ej. Quiero 2 cadenas de oso estándar).

📌 Nota: Si tienes una duda muy específica, deseas personalizar una prenda con tu nombre o necesitas soporte con un pago, solo pídelo y te transferiré de inmediato con un asesor personalizado para que te atienda personalmente. 🥰

¿En qué te puedo ayudar hoy? 💕"""

SALUDOS = ["hola", "buenas", "buen día", "buenas tardes", "buenos días", "qué tal", "hey", "buenass", "buenos dias"]

# =====================================================================
# CONSTANTES DE TEXTO CORPORATIVO - SOFIIACCESORIOS
# =====================================================================

DATOS_DOMICILIO = """➡️Porfis regalame tus datos para hacerte el domicilio🩵📤

•Nombre completo:
•Dirección exacta:
•Barrio:
•Teléfono:
•Cancelas en efectivo o transferencia:"""

MEDIOS_PAGO = """• *Nequi*
#3225199639
Jose Andrés Vásquez

Daviplata
#3225417775
Ilma Solarte

No se reciben pagos por transfiya"""

AGRADECIMIENTO_CIERRE = """¡Bella mil gracias por apoyarnos🩵🫶🏻!
Espero que lo disfrutes🤗
Por acá siempre bienvenid@
Esperamos poder servirte nuevamente🌟"""

PROCESO_ENVIO = """➡️Para realizar tu compra nos puedes realizar el pago por transferencia bancaria
•NEQUI
•BANCOLOMBIA
•DAVIPLATA

➡️Una vez realizado el pago nos envías captura de pantalla del comprobante y nos envías tus datos completos para poder realizar tu envío

➡️El envío se te realiza por transportadora Envía, y lo pagas al momento en que recibes tu pedido así pagas el valor exacto *solo pagas el costo del envio*
El valor varía según la ciudad en que te encuentres.

➡️Verificado el pago procedemos a alistar tu pedido y se te envía al día siguiente de haber realizado el pago, te enviamos foto de la guía para que puedas rastrear tu pedido y estamos pendientes de que lo recibas."""

COSTOS_ENVIO = """✨ Sabemos lo importante que es conocer el valor del envío 💲📦🚚, pero ten en cuenta que esas tarifas las define directamente cada transportadora.

Por eso, aquí te dejamos los enlaces 🔗 para que puedas consultarlas fácilmente:

🚚📦 Envia
👉 https://envia.co/

🚚📦 Coordinadora
👉 https://acortar.link/gvfjDX

🚚📦 Interrapidísimo
👉 https://interrapidisimo.com/cotiza-tu-envio/

🚚📦 Servientrega
👉 https://www.servientrega.com/wps/portal/cotizador

🙌 Esperamos que esta info te sea súper útil. Si tienes más preguntas, estamos aquí para ayudarte 🤗"""

HORARIO_ATENCION = """Nuestro horario comercial es el siguiente:
Domingo: 2:00 PM - 6:00 PM
Lunes a Sábado: 2:00 PM - 8:30 PM"""

MENSAJE_FUERA_HORARIO = """En este momento está cerrado
Nuestro horario comercial es el siguiente:
Domingo: 2:00 PM - 6:00 PM
Lunes: 2:00 PM - 8:30 PM
Martes: 2:00 PM - 8:30 PM
Miércoles: 2:00 PM - 8:30 PM
Jueves: 2:00 PM - 8:30 PM
Viernes: 2:00 PM - 8:30 PM
Sábado: 2:00 PM - 8:30 PM"""

SYSTEM_PROMPT = """
Eres "Sofii", la asistente virtual experta en ventas de 'Sofia Vasquez Accesorios'. Tu objetivo es atender con amabilidad, naturalidad, entusiasmo y un tono muy femenino, usando emojis de forma estética (✨, 💖, 🛍️, 🥰).

Acompañarás al usuario en todo su proceso de decisión, desde el saludo inicial hasta el cierre final de la venta.

REGLAS DE INYECCIÓN DE TEXTO OBLIDATORIAS:

1. SOLICITUD DE DATOS PARA ENVÍO: Cuando el cliente decida concretar o cerrar una compra (use frases como "quiero llevarlo", "apártame ese", "quiero ordenar"), debes responder con entusiasmo y agregar TEXTUALMENTE este bloque para recolectar su información:
""" + DATOS_DOMICILIO + """

2. MEDIOS DE PAGO: Cuando el cliente pregunte por las cuentas, cómo realizar la transferencia o el pago, envíale EXACTAMENTE este formato:
""" + MEDIOS_PAGO + """

3. LOGÍSTICA Y PROCESO DE ENVÍO: Si el cliente tiene dudas sobre cómo se manejan los despachos, los tiempos de alistamiento o las condiciones de la transportadora, respóndele utilizando este texto oficial:
""" + PROCESO_ENVIO + """

4. CONSULTAR COSTOS DE ENVÍO: Si el cliente pregunta el precio del envío a su ciudad o cómo calcularlo, debes proveerle obligatoriamente este mensaje con los enlaces correspondientes:
""" + COSTOS_ENVIO + """

5. CIERRE Y AGRADECIMIENTO: Cuando el cliente envíe sus datos completos de entrega o confirme que el pago ha sido enviado con éxito, despídete de forma muy dulce enviando este texto de agradecimiento:
""" + AGRADECIMIENTO_CIERRE + """

6. CONSULTA DE HORARIOS: Si el usuario te pregunta por los horarios comerciales de la tienda, lístale la siguiente información:
""" + HORARIO_ATENCION + """

REGLAS CONVERSACIONALES ADICIONALES:
- Mantén tus respuestas relativamente cortas, dinámicas y directas, ideales para una lectura rápida en pantallas de WhatsApp.
- Si el cliente pregunta por un artículo, color o especificación que NO está registrado en tu catálogo provisto por el sistema, infórmale de manera empática que lo registrarás en la lista de espera y añade al final de tu respuesta la siguiente etiqueta exacta: [AGENDAR_ASESOR_HUMANO]
"""

def verificar_horario_comercial():
    zona_co = pytz.timezone('America/Bogota')
    ahora = datetime.now(zona_co)
    dia_semana = ahora.weekday()
    hora_actual = ahora.time()

    if dia_semana == 6:
        apertura = ahora.replace(hour=14, minute=0, second=0, microsecond=0).time()
        cierre = ahora.replace(hour=18, minute=0, second=0, microsecond=0).time()
    else:
        apertura = ahora.replace(hour=14, minute=0, second=0, microsecond=0).time()
        cierre = ahora.replace(hour=20, minute=30, second=0, microsecond=0).time()

    return apertura <= hora_actual <= cierre


def descargar_y_transcribir_audio(media_url):
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    if not account_sid or not auth_token:
        print("[AUDIO] Faltan credenciales Twilio para descargar audio")
        return None

    try:
        resp = requests.get(media_url, auth=(account_sid, auth_token), timeout=30)
        resp.raise_for_status()
        audio_data = io.BytesIO(resp.content)
        audio_data.name = "audio.ogg"
        print(f"[AUDIO] Descargado: {len(resp.content)} bytes")

        transcription = groq_client.audio.transcriptions.create(
            model="whisper-large-v3-turbo",
            file=audio_data,
            language="es",
        )
        texto = transcription.text.strip()
        print(f"[AUDIO] Transcripción: {texto}")
        return texto

    except Exception as e:
        print(f"[AUDIO] Error: {e}")
        return None


@app.route("/webhook", methods=["POST"])
def webhook():
    if not verificar_horario_comercial():
        print("[WEBHOOK] Fuera de horario comercial")
        xml_response = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{MENSAJE_FUERA_HORARIO}</Message></Response>'
        return xml_response, 200, {'Content-Type': 'text/xml'}

    from_number = request.values.get("From", "unknown")
    start = time.time()
    num_media = int(request.values.get("NumMedia", 0))

    incoming_msg = request.values.get("Body", "").strip()

    if num_media > 0:
        media_url = request.values.get("MediaUrl0")
        media_type = request.values.get("MediaContentType0", "")
        print(f"[WEBHOOK] Audio detectado de {from_number} | tipo: {media_type}")

        transcripcion = descargar_y_transcribir_audio(media_url)
        if transcripcion:
            incoming_msg = f"[Transcripción de audio del cliente: {transcripcion}]"
            print(f"[WEBHOOK] Mensaje transcrito: {transcripcion}")
        else:
            incoming_msg = "[El cliente envió un audio que no pudo transcribirse]"
    else:
        print(f"[WEBHOOK] Mensaje de {from_number}: {incoming_msg}")

    resp = MessagingResponse()

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": incoming_msg}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.6,
        )
        reply_text = chat_completion.choices[0].message.content

        if "[AGENDAR_ASESOR_HUMANO]" in reply_text:
            print(f"[WEBHOOK] *** SOLICITUD DE ASESOR HUMANO *** De: {from_number}")
            reply_text = reply_text.replace("[AGENDAR_ASESOR_HUMANO]", "").strip()

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