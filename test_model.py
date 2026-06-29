import os
import sys
import time
import io
from groq import Groq
from dotenv import load_dotenv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

load_dotenv()

API_KEY = os.environ.get("GROQ_API_KEY")
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = 'Eres "Sofii", agente de ventas de Sofia Vasquez Accesorios. Regla crítica: Si el cliente pide algo que NO está en tu catálogo, responde con un mensaje empático y al final incluye EXACTAMENTE: [AGENDAR_ASESOR_HUMANO].'

TEST_CASES = [
    {"name": "Saludo", "msg": "Hola, buenas tardes"},
    {"name": "Consulta cadenas", "msg": "Qué cadenas tienen?"},
    {"name": "Precio especifico", "msg": "Cuánto cuesta la cadena de oso?"},
    {"name": "Compra", "msg": "Quiero comprar 2 pulseras de neopreno"},
    {"name": "Personalizar (debe agendar)", "msg": "Quiero una cadena con mi nombre 'Maria' en oro de 18k"},
    {"name": "Fuera de catalogo (debe agendar)", "msg": "Tienen aretes de plata 925 con turquesa natural?"},
    {"name": "Transferencia pago", "msg": "Tengo un problema con mi pago, no me llegó la confirmación"},
]

def run_test():
    print("=" * 60)
    print(f"  TEST DE ESTABILIDAD Y VELOCIDAD - {MODEL}")
    print("=" * 60)

    if not API_KEY:
        print("\n[ERROR] GROQ_API_KEY no encontrada en .env")
        print("Agrega tu API key en el archivo .env")
        return

    print(f"\nAPI Key: {API_KEY[:8]}...{API_KEY[-4:]}")
    print(f"Modelo: {MODEL}")
    print(f"Tests: {len(TEST_CASES)} casos\n")

    client = Groq(api_key=API_KEY)
    results = []
    total_tokens_in = 0
    total_tokens_out = 0
    errors = 0

    for i, test in enumerate(TEST_CASES, 1):
        print(f"[{i}/{len(TEST_CASES)}] {test['name']}: \"{test['msg']}\"")
        start = time.time()

        try:
            completion = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": test["msg"]}
                ],
                temperature=0.6,
            )
            elapsed = round(time.time() - start, 2)
            reply = completion.choices[0].message.content
            tokens_in = completion.usage.prompt_tokens
            tokens_out = completion.usage.completion_tokens
            tps = round(tokens_out / elapsed, 1) if elapsed > 0 else 0

            total_tokens_in += tokens_in
            total_tokens_out += tokens_out

            results.append({
                "name": test["name"],
                "time": elapsed,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "tps": tps,
                "ok": True
            })

            print(f"  OK | {elapsed}s | {tokens_out} tokens | {tps} t/s")
            print(f"  -> {reply[:100]}...\n")

        except Exception as e:
            elapsed = round(time.time() - start, 2)
            errors += 1
            results.append({
                "name": test["name"],
                "time": elapsed,
                "error": str(e),
                "ok": False
            })
            print(f"  ERROR | {elapsed}s | {e}\n")

    times = [r["time"] for r in results if r["ok"]]
    tps_list = [r["tps"] for r in results if r["ok"] and "tps" in r]

    print("=" * 60)
    print("  RESUMEN")
    print("=" * 60)
    print(f"  Tests ejecutados:  {len(TEST_CASES)}")
    print(f"  Exitosos:          {len(TEST_CASES) - errors}")
    print(f"  Errores:           {errors}")
    print(f"  Tiempo promedio:   {round(sum(times)/len(times), 2) if times else 0}s")
    print(f"  Tiempo minimo:     {min(times) if times else 0}s")
    print(f"  Tiempo maximo:     {max(times) if times else 0}s")
    print(f"  Tokens entrada:    {total_tokens_in}")
    print(f"  Tokens salida:     {total_tokens_out}")
    print(f"  TPS promedio:      {round(sum(tps_list)/len(tps_list), 1) if tps_list else 0} t/s")
    print(f"  TPS maximo:        {max(tps_list) if tps_list else 0} t/s")
    print("=" * 60)

if __name__ == "__main__":
    run_test()
