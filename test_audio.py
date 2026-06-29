import os
import io
import sys
import time
import json
import requests
import tempfile
from groq import Groq
from dotenv import load_dotenv
from gtts import gTTS

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

load_dotenv()

API_KEY = os.environ.get("GROQ_API_KEY")
TWILIO_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
URL_CATALOGO = "https://wa.me/c/573103632461"

AUDIO_TEST_CASES = [
    {"name": "Saludo simple", "texto": "Hola buenas tardes"},
    {"name": "Consulta cadenas", "texto": "Qué cadenas tienen disponibles"},
    {"name": "Precio", "texto": "Cuánto cuesta la pulsera de neopreno"},
    {"name": "Compra", "texto": "Quiero comprar dos pulseras para pareja"},
    {"name": "Fuera de catálogo", "texto": "Tienen aretes de plata con turquesa"},
]

SYSTEM_PROMPT = """Eres "Sofii", agente de ventas de Sofiiaccesorios. Responde corto y con emojis.
Catalogo: cadenas ($28,000-$15,000), anillos ($15,000-$18,000), tobilleras ($8,000-$20,000), aretes ($12,000-$30,000), joyeros ($25,000-$45,000), pulseras ($18,000-$25,000).
Link catalogo fotos: """ + URL_CATALOGO + """
Regla: Si el cliente pide algo fuera del catalogo, responde con mensaje empatico e incluye al final: [AGENDAR_ASESOR_HUMANO]"""


def generar_audio(texto, filename=None):
    tts = gTTS(text=texto, lang="es", slow=False)
    if filename:
        tts.save(filename)
        return filename
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf


def test_whisper_conexion(client):
    print("[TEST] Verificando conexión a Groq Whisper...")
    try:
        models = client.models.list()
        whisper_available = any("whisper" in m.id for m in models.data)
        print(f"  -> Whisper {'disponible' if whisper_available else 'NO disponible'}")
        return whisper_available
    except Exception as e:
        print(f"  -> Error: {e}")
        return False


def test_transcripcion(client, audio_data, nombre_test):
    start = time.time()
    try:
        if isinstance(audio_data, io.BytesIO):
            audio_data.name = "audio.mp3"

        transcription = client.audio.transcriptions.create(
            model="whisper-large-v3-turbo",
            file=audio_data,
            language="es",
        )
        elapsed = round(time.time() - start, 2)
        texto = transcription.text.strip()
        return {"ok": True, "time": elapsed, "texto": texto}
    except Exception as e:
        elapsed = round(time.time() - start, 2)
        return {"ok": False, "time": elapsed, "error": str(e)}


def test_pipeline_completo(client, transcripcion):
    start = time.time()
    msg = f"[Transcripción de audio del cliente: {transcripcion}]"
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": msg}
            ],
            temperature=0.6,
        )
        elapsed = round(time.time() - start, 2)
        reply = completion.choices[0].message.content
        tokens_in = completion.usage.prompt_tokens
        tokens_out = completion.usage.completion_tokens
        return {"ok": True, "time": elapsed, "tokens_in": tokens_in, "tokens_out": tokens_out, "reply": reply[:120]}
    except Exception as e:
        elapsed = round(time.time() - start, 2)
        return {"ok": False, "time": elapsed, "error": str(e)}


def run_tests():
    print("=" * 65)
    print("  TEST DE AUDIO - Transcripción Whisper + Pipeline Completo")
    print("=" * 65)

    if not API_KEY:
        print("\n[ERROR] GROQ_API_KEY no encontrada")
        return

    client = Groq(api_key=API_KEY)
    print(f"API Key: {API_KEY[:8]}...{API_KEY[-4:]}\n")

    if not test_whisper_conexion(client):
        print("[ERROR] Whisper no disponible, abortando")
        return

    print("\n" + "=" * 65)
    print("  FASE 1: Transcripción de audio con Whisper")
    print("=" * 65)

    transcripcion_results = []
    pipeline_results = []

    for i, test in enumerate(AUDIO_TEST_CASES, 1):
        print(f"\n[{i}/{len(AUDIO_TEST_CASES)}] {test['name']}: \"{test['texto']}\"")

        print("  Generando audio...", end=" ")
        audio_buf = generar_audio(test["texto"])
        audio_buf.seek(0)
        size_kb = round(len(audio_buf.getvalue()) / 1024, 1)
        print(f"{size_kb} KB")

        r1 = test_transcripcion(client, audio_buf, test["name"])
        transcripcion_results.append(r1)

        if r1["ok"]:
            print(f"  Transcripción ({r1['time']}s): \"{r1['texto']}\"")
            is_accurate = r1["texto"].lower()[:10] == test["texto"].lower()[:10]
            print(f"  Precisión: {'ALTA (~100%)' if is_accurate else 'MEDIA'}")

            print(f"  Pipeline LLM...", end=" ")
            r2 = test_pipeline_completo(client, r1["texto"])
            pipeline_results.append(r2)
            if r2["ok"]:
                print(f"({r2['time']}s, {r2['tokens_out']} tokens)")
                print(f"  Respuesta Sofii: {r2['reply']}...")
            else:
                print(f"ERROR: {r2['error']}")
        else:
            print(f"  ERROR: {r1['error']}")

    print("\n" + "=" * 65)
    print("  RESUMEN DE AUDIO")
    print("=" * 65)

    t_transc = [r["time"] for r in transcripcion_results if r["ok"]]
    t_pipe = [r["time"] for r in pipeline_results if r["ok"]]
    t_total = [t_transc[i] + t_pipe[i] if i < len(t_pipe) else t_transc[i] for i in range(len(t_transc))]

    print(f"  Transcripción Whisper:")
    print(f"    Promedio: {round(sum(t_transc)/len(t_transc), 2) if t_transc else 0}s")
    print(f"    Mínimo:   {min(t_transc) if t_transc else 0}s")
    print(f"    Máximo:   {max(t_transc) if t_transc else 0}s")
    print(f"  Pipeline completo (Whisper + LLM):")
    print(f"    Promedio: {round(sum(t_pipe)/len(t_pipe), 2) if t_pipe else 0}s")
    print(f"  Tiempo total cliente (audio → respuesta):")
    print(f"    Promedio: {round(sum(t_total)/len(t_total), 2) if t_total else 0}s")
    print(f"    Mínimo:   {min(t_total) if t_total else 0}s")
    print(f"    Máximo:   {max(t_total) if t_total else 0}s")

    print("\n" + "=" * 65)
    print("  VEREDICTO")
    print("=" * 65)
    errors = sum(1 for r in transcripcion_results if not r["ok"])
    total = len(AUDIO_TEST_CASES)
    exito = total - errors
    print(f"  Transcripciones: {exito}/{total} exitosas")
    print(f"  Pipeline LLM:    {len(pipeline_results)}/{exito} exitosos")
    if t_total and sum(t_total) / len(t_total) < 3:
        print(f"  ✅ Tiempo total < 3s: ACEPTABLE para WhatsApp")
    else:
        print(f"  ⚠️ Tiempo total > 3s: Puede ser lento para WhatsApp")
    print("=" * 65)


if __name__ == "__main__":
    run_tests()
