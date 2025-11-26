import os
from pathlib import Path
from openai import OpenAI

# Cargar .env si está disponible
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Inicializar cliente OpenAI usando OPENAI_API_KEY del entorno
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else OpenAI()


def _load_prompt():
    # prompt relativo al directorio del módulo
    p = Path(__file__).resolve().parent / "prompts" / "explanation_prompt.txt"
    if p.exists():
        return p.read_text(encoding="utf-8")

    # Fallback por si no existe el archivo
    return (
        "Eres un asistente que resume y explica una lista de compras optimizada entre supermercados. "
        "Explica de forma clara qué decisiones se tomaron, menciona los supermercados usados y su impacto en el costo, "
        "y ofrece recomendaciones breves para ahorrar más."
    )


def generate_explanation(shopping_list, total_cost):
    """Genera un texto explicativo sobre la lista de compras.

    shopping_list: lista de dicts con claves esperadas: 'producto', 'supermercado', 'precio' o 'precio_total'
    total_cost: número (float)
    """
    prompt = _load_prompt()

    # Normalizar items para el prompt
    lines = []
    for item in shopping_list:
        nombre = item.get("producto") or item.get("nombre") or "(sin nombre)"
        supermercado = item.get("supermercado", "(sin supermercado)")
        precio = item.get("precio") or item.get("precio_unitario") or item.get("precio_total") or 0
        try:
            precio_text = f"${float(precio):,.2f}"
        except Exception:
            precio_text = str(precio)
        lines.append(f"- {nombre} → {supermercado} ({precio_text})")

    items_text = "\n".join(lines)

    user_message = f"Lista optimizada:\n{items_text}\n\nCosto total: ${float(total_cost):,.2f}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt},
                      {"role": "user", "content": user_message}],
            temperature=0.7,
            max_tokens=600,
        )

        # Compatibilidad con distintas formas de respuesta
        if hasattr(response, "choices") and response.choices:
            choice = response.choices[0]
            if hasattr(choice, "message") and hasattr(choice.message, "content"):
                return choice.message.content
            elif isinstance(choice, dict) and "message" in choice and "content" in choice["message"]:
                return choice["message"]["content"]

        # Fallback: intentar acceder como dict
        data = response if isinstance(response, dict) else getattr(response, "to_dict", lambda: {})()
        if data:
            try:
                return data["choices"][0]["message"]["content"]
            except Exception:
                pass

        return ""  # vacío si no se pudo extraer

    except Exception as e:
        # No romper la aplicación si falla la llamada a la API de OpenAI
        return f"[Error generando explicación: {str(e)}]"