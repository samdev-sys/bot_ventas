import os
import io
import sys
import base64
import requests
from groq import Groq
from dotenv import load_dotenv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
load_dotenv()

API_KEY = os.environ.get("GROQ_API_KEY")

TEST_IMAGE_URL = "https://httpbin.org/image/jpeg"

def test_vision():
    print("=" * 60)
    print("  TEST DE VISIÓN — Groq + Llama 4 Scout")
    print("=" * 60)

    if not API_KEY:
        print("[ERROR] GROQ_API_KEY no encontrada")
        return

    client = Groq(api_key=API_KEY)
    print(f"API Key: {API_KEY[:8]}...{API_KEY[-4:]}")
    print(f"Modelo: meta-llama/llama-4-scout-17b-16e-instruct\n")

    print(f"Descargando imagen de prueba...")
    resp = requests.get(TEST_IMAGE_URL, timeout=15)
    img_bytes = resp.content
    print(f"Imagen: {len(img_bytes)} bytes\n")

    img_b64 = base64.b64encode(img_bytes).decode("utf-8")

    print("Analizando con modelo de visión...")
    import time
    start = time.time()

    try:
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe brevemente qué es esta imagen en 1-2 oraciones. Si es un accesorio o joya, describe tipo, color, material y estilo. Responde solo con la descripción, sin saludos."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                ]
            }],
            temperature=0.3,
            max_completion_tokens=150,
        )
        elapsed = round(time.time() - start, 2)
        desc = completion.choices[0].message.content
        tokens_in = completion.usage.prompt_tokens
        tokens_out = completion.usage.completion_tokens

        print(f"  Tiempo: {elapsed}s")
        print(f"  Tokens: {tokens_in} in / {tokens_out} out")
        print(f"  Descripción: {desc}")
        print(f"\n{'=' * 60}")
        print(f"  ✅ Visión funcionando correctamente")
        print(f"{'=' * 60}")

    except Exception as e:
        elapsed = round(time.time() - start, 2)
        print(f"  Error ({elapsed}s): {e}")

if __name__ == "__main__":
    test_vision()
