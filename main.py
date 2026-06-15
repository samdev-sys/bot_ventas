import os
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from groq import Groq

app = Flask(__name__)

# Configuración del cliente de Groq utilizando variables de entorno
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# BASE DE DATOS ESTRUCTURADA Y REAL DEL CATÁLOGO
CATALOGO_PRODUCTOS = {
    # --- CADENAS, GARGANTILLAS Y RECUERDOS ---
    "cadena_maxi_oso": {
        "nombre": "Cadena Maxi Oso Articulado",
        "precio": "$28.000 COP",
        "categoria": "Cadenas",
        "descripcion": "Hermosa cadena con dije de oso articulado grande. Material: Rodio."
    },
    "cadena_oso_articulado": {
        "nombre": "Cadena Oso Articulado Estándar",
        "precio": "$28.000 COP",
        "categoria": "Cadenas",
        "descripcion": "Dije de oso con movimiento sutil. Material: Baño en rodio de excelente calidad."
    },
    "maxi_cruz_brillante": {
        "nombre": "Maxi Cruz Brillante",
        "precio": "$24.000 COP",
        "categoria": "Cadenas",
        "descripcion": "Dije de cruz con acabado brillante texturizado. Modelo Maxi Cruz-Shine en Rodio."
    },
    "chokers_1": {
        "nombre": "Chokers #1",
        "precio": "$15.000 COP",
        "categoria": "Cadenas",
        "descripcion": "Gargantilla corta ajustable con detalles delicados. Material: Rodio. El precio es por unidad."
    },
    "gargantilla_lazo": {
        "nombre": "Gargantilla Lazo Mediana",
        "precio": "$28.000 COP",
        "categoria": "Cadenas",
        "descripcion": "Tejido elegante tipo lazo texturizado. Material: Rodio."
    },
    "gargantilla_cubana": {
        "nombre": "Gargantilla Cubana",
        "precio": "$20.000 COP",
        "categoria": "Cadenas",
        "descripcion": "Cadena de eslabones estilo cubano clásico y brillante. Material: Rodio."
    },
    "camandula_cristal": {
        "nombre": "Camándula en Cristal",
        "precio": "$18.000 COP",
        "categoria": "Cadenas",
        "descripcion": "Hermosa camándula tejida con cuentas de cristal brillante y dijes religiosos. Diseño muy delicado."
    },
    "camandula_acero": {
        "nombre": "Camándula en Acero",
        "precio": "$25.000 COP",
        "categoria": "Cadenas",
        "descripcion": "Camándula clásica de alta durabilidad con medalla de San Benito y cruz. Material: Acero inoxidable."
    },
    "cadena_nombre_lisa": {
        "nombre": "Cadena Nombre Lisa (Personalizada)",
        "precio": "Consultar valor final",
        "categoria": "Cadena con Nombre",
        "descripcion": "Cadena personalizada con nombre en letra lisa delicada."
    },
    "cadena_nombre_brillante": {
        "nombre": "Cadena Nombre Brillante (Personalizada)",
        "precio": "Consultar valor final",
        "categoria": "Cadena con Nombre",
        "descripcion": "Cadena personalizada con nombre y apliques texturizados de letra brillante."
    },

    # --- ANILLOS ---
    "anillos_chunky_dorados": {
        "nombre": "Anillos Chunky Dorados",
        "precio": "$15.000 COP",
        "categoria": "Anillos",
        "descripcion": "Anillos gruesos de tendencia. Material: Rodinados. Valor por unidad."
    },
    "anillos_serpiente": {
        "nombre": "Anillos Serpiente",
        "precio": "$18.000 COP",
        "categoria": "Anillos",
        "descripcion": "Diseño en forma de serpiente estilizada. Material: Rodinados. Valor por unidad."
    },
    "anillos_3_grados": {
        "nombre": "Anillos 3°",
        "precio": "$15.000 COP",
        "categoria": "Anillos",
        "descripcion": "Anillo con diseño geométrico sutil. Material: Rodinados. Valor por unidad."
    },

    # --- TOBILLERAS ---
    "tobillera_denario": {
        "nombre": "Tobillera Denario San Benito",
        "precio": "$18.000 COP",
        "categoria": "Tobilleras",
        "descripcion": "Tobillera tipo denario de protección. Material: Acero resistente."
    },
    "tobilleras_7_nudos": {
        "nombre": "Tobilleras 7 Nudos",
        "precio": "$8.000 COP",
        "categoria": "Tobilleras",
        "descripcion": "Tobillera roja de protección y buena suerte. Cada una incluye un dije en acero."
    },
    "tobillera_amuleto": {
        "nombre": "Tobillera Amuleto San Benito",
        "precio": "$20.000 COP",
        "categoria": "Tobilleras",
        "descripcion": "Diseño con ojo turco y medalla de San Benito. Disponible en color dorado y plateado."
    },

    # --- RELICARIOS ---
    "relicarios_acero": {
        "nombre": "Relicarios en Acero",
        "precio": "$25.000 COP",
        "categoria": "Relicario",
        "descripcion": "Dije de corazón o circular para guardar fotos. Material: Acero. Medida: 40cm."
    },

    # --- ARETES, TOPOS Y EARCUFFS ---
    "candongas_perlas": {
        "nombre": "Candongas de Perlas",
        "precio": "$25.000 COP",
        "categoria": "Aretes Rodio",
        "descripcion": "Candongas medianas con perlas colgantes elegantes."
    },
    "set_candongas_lisas": {
        "nombre": "Set Candongas Lisas Doradas",
        "precio": "$32.000 COP",
        "categoria": "Aretes Rodio",
        "descripcion": "Set variado de candongas clásicas lisas. Material: Baño en rodio."
    },
    "set_candongas_bolitas": {
        "nombre": "Set Candongas Bolitas",
        "precio": "$40.000 COP",
        "categoria": "Aretes Rodio",
        "descripcion": "Set múltiple de candongas con detalles de esferas. Material: Baño en rodio."
    },
    "est_earcuffs": {
        "nombre": "Est Earcuffs",
        "precio": "$15.000 COP",
        "categoria": "Earcuffs",
        "descripcion": "Earcuff texturizado que se ajusta a la oreja sin perforación. Material: Covergold rodinado."
    },
    "earcuffs_cadena": {
        "nombre": "Earcuffs Estilo Eslabón",
        "precio": "$15.000 COP",
        "categoria": "Earcuffs",
        "descripcion": "Diseño tipo cadena o eslabones. Material: Covergold rodinado."
    },
    "earcuffs_lisos": {
        "nombre": "Earcuffs Lisos Clásicos",
        "precio": "$12.000 COP",
        "categoria": "Earcuffs",
        "descripcion": "Earcuffs de superficie lisa, pulida y minimalista. Ajustables sin perforación. Material: Rodio."
    },
    "topos_set_rodio": {
        "nombre": "Topos en Set Rodio Clásicos",
        "precio": "$18.000 COP",
        "categoria": "Topos en set x2 x3",
        "descripcion": "Set con múltiples diseños de aretes pequeños para combinar en Rodio."
    },
    "topos_set_variados": {
        "nombre": "Topos en Set Variados (Material Rodio)",
        "precio": "$18.000 COP",
        "categoria": "Topos en set x2 x3",
        "descripcion": "Variedad de figuras pequeñas. Set x2 en $18.000 o Set x3 en $27.000."
    },
    "topos_set_dorados": {
        "nombre": "Topos en Set Rodio Dorados x3",
        "precio": "$27.000 COP",
        "categoria": "Topos en set x2 x3",
        "descripcion": "Set premium de tres pares de topos dorados en Rodio."
    },
    "aretes_manos": {
        "nombre": "Aretes Elaborados a Mano (Corazones)",
        "precio": "$18.000 COP",
        "categoria": "Aretes maxi - largos en acero",
        "descripcion": "Diseño artesanal tejido en forma de corazón con base dorada."
    },
    "aretes_largos_acero": {
        "nombre": "Aretes Largos en Acero",
        "precio": "$15.000 COP",
        "categoria": "Aretes maxi - largos en acero",
        "descripcion": "Aretes de cadena colgante delgada y elegante en acero dorado."
    },
    "aretes_brillantes_fantasia": {
        "nombre": "Aretes Brillantes Fantasía",
        "precio": "$10.000 COP",
        "categoria": "Aretes maxi - largos en acero",
        "descripcion": "Maxi aretes colgantes cubiertos de strass de brillo espectacular."
    },

    # --- JOYEROS ---
    "joyero_cuadrado_pequeno": {
        "nombre": "Joyero Cuadrado Pequeño",
        "precio": "$25.000 COP",
        "categoria": "Joyeros",
        "descripcion": "Organizador portátil para rings, topos y cadenas. Material sintético texturizado."
    },
    "joyero_redondo": {
        "nombre": "Joyero Redondo",
        "precio": "$25.000 COP",
        "categoria": "Joyeros",
        "descripcion": "Joyero circular compacto con divisiones internas. Disponible en color negro y verde menta."
    },
    "joyero_corazon": {
        "nombre": "Joyero Corazón",
        "precio": "$28.000 COP",
        "categoria": "Joyeros",
        "descripcion": "Diseño romántico en forma de corazón. Disponible sólo en color negro."
    },
    "joyero_grande_espejo": {
        "nombre": "Joyero Grande con Espejo",
        "precio": "$45.000 COP",
        "categoria": "Joyeros",
        "descripcion": "Joyero amplio de gran capacidad con espejo integrado, múltiples compartimentos para cadenas, anillos y aretes. Cierre seguro."
    },

    # --- PULSERAS, BRAZALETES Y PANDORAS ---
    "pandoras_rodinadas": {
        "nombre": "Pandoras Rodinadas Premium",
        "precio": "Consultar precio según charms",
        "categoria": "Pandoras",
        "descripcion": "Pulsera estilo Pandora con dijes y balines rodinados de alta calidad."
    },
    "pandoras_acero_covergold": {
        "nombre": "Pandoras Acero Covergold",
        "precio": "$50.000 COP",
        "categoria": "Pandoras",
        "descripcion": "Pulsera con charms variados y dije de cruz. Material: Acero con covergold rodinado."
    },
    "brazalete_love_cartier": {
        "nombre": "Brazalete Love Cartier",
        "precio": "$25.000 COP",
        "categoria": "Brazaletes",
        "descripcion": "Brazalete rígido de diseño icónico minimalista. Material: Rodinado."
    },
    "brazaletes_nudo": {
        "nombre": "Brazaletes Rígidos Ajustables",
        "precio": "$20.000 COP",
        "categoria": "Brazaletes",
        "descripcion": "Brazalete abierto con detalle de nudo central. Material: Rodinado. Valor por unidad."
    },
    "duo_clavo_cartier": {
        "nombre": "Dúo Clavo Cartier (Brazalete + Anillo)",
        "precio": "$20.000 COP",
        "categoria": "Brazaletes",
        "descripcion": "Set que incluye brazalete rígido de clavo y un anillo graduable a juego. Material: Rodinado."
    },
    "pulseras_neopreno": {
        "nombre": "Pulseras en Neopreno (Personalizadas)",
        "precio": "$25.000 COP",
        "categoria": "Parejas. - Amig@s",
        "descripcion": "Pulseras elásticas o ajustables con balines dorados. Tú escoges el color del neopreno."
    },
    "pulseras_parejas_dijes": {
        "nombre": "Pulseras Parejas con Dijes",
        "precio": "$30.000 COP",
        "categoria": "Parejas. - Amig@s",
        "descripcion": "Set de dos pulseras de hilo con dijes complementarios. Se personalizan al gusto."
    },
    "pulseras_parejas_perlas": {
        "nombre": "Pulseras para Parejas Especiales",
        "precio": "$25.000 COP",
        "categoria": "Parejas. - Amig@s",
        "descripcion": "Set de dos pulseras con hilo rojo/negro y dije central esférico o de corona."
    },
    "pulsera_balines_rodio": {
        "nombre": "Pulsera Balines en Rodio",
        "precio": "$12.000 COP",
        "categoria": "Pulseras",
        "descripcion": "Pulsera delicada de balines dorados brillantes. Estilo clásico y combinable. Material: Rodio."
    }
}

URL_CATALOGO = "https://wa.me/c/573103632461"

SYSTEM_PROMPT = f"""
Eres Sofii, la asesora virtual experta de "Sofia Vasquez Accesorios". Tu propósito es atender con un tono muy amable, entusiasta, empático, educado y profesional a las clientas interesadas en nuestra joyería. Puedes usar emojis delicados (✨, 🥰, 💖, 💎) para hacer la conversación amigable.

REGLAS DE ATENCIÓN:
1. Utiliza ÚNICAMENTE los productos, nombres, descripciones y precios que se encuentran registrados en la siguiente base de datos del inventario:
{CATALOGO_PRODUCTOS}

2. Si te preguntan por un accesorio específico que está en la base de datos, proporciónale con total precisión su precio y características.
3. Si la clienta te pide ver imágenes, más modelos, o está buscando explorar todas las opciones completas de una categoría, debes ser proactiva y proveer el siguiente enlace directo al catálogo oficial de WhatsApp: {URL_CATALOGO}
4. Si un producto de la base de datos dice "Consultar valor final" (como las piezas personalizadas), explícale amablemente que el valor se define según la personalización exacta que prefiera y que puede ver opciones en nuestro catálogo: {URL_CATALOGO}
5. Jamás inventes productos, materiales ni precios que no estén listados explícitamente en la base de datos proporcionada. Si no dispones de la información, invítala cordialmente a revisar el catálogo de WhatsApp.
"""

@app.route("/webhook", methods=["POST"])
def webhook():
    # Obtener el mensaje enviado por el usuario desde WhatsApp (vía Twilio)
    incoming_msg = request.values.get("Body", "").strip()
    
    # Crear la estructura de respuesta de Twilio
    resp = MessagingResponse()
    msg = resp.message()

    try:
        # Llamar a la API de Groq usando el modelo Llama 3 para procesar la respuesta
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": incoming_msg}
            ],
            model="llama3-8b-8192",
            temperature=0.6,
        )
        
        # Extraer la respuesta generada por la IA
        reply_text = chat_completion.choices[0].message.content
        msg.body(reply_text)

    except Exception as e:
        # Manejo de fallos de conexión o de API
        print(f"Error procesando la solicitud en Groq: {e}")
        msg.body("¡Hola! ✨ En este momento estoy experimentando un pequeño inconveniente técnico, pero puedes ver todos nuestros accesorios y precios directamente en nuestro catálogo oficial aquí: https://wa.me/c/573103632461 🥰")

    return str(resp)

if __name__ == "__main__":
    # Iniciar la aplicación Flask en el puerto definido por el entorno o por defecto en el 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)