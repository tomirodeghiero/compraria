import json, re, os
from openai import AsyncOpenAI
from dotenv import load_dotenv
load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generar_lista_base(inventario, presupuesto, personas, preferencias, historial=""):
    prompt = f"""Sos un experto en compras argentinas. Generá una lista REALISTA de supermercado para {personas} personas.
Presupuesto máximo: ${presupuesto}. Preferencias: {preferencias}. Inventario actual: {inventario}

Devuelve SOLO un JSON válido con esta estructura exacta:
[
  {{"producto": "Yerba", "cantidad": 5, "unidad": "kg", "precio": 8500}},
  {{"producto": "Leche", "cantidad": 24, "unidad": "litros", "precio": 1400}}
]"""

    try:
        if os.getenv("OPENAI_API_KEY"):
            completion = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            texto = completion.choices[0].message.content
        else:
            texto = '[{"producto": "Yerba", "cantidad": 4.5, "unidad": "kg", "precio": 8500}]'  # fallback

        # Forzar formato correcto
        match = re.search(r'\[.*\]', texto, re.DOTALL)
        lista = json.loads(match.group(0)) if match else []
        
        # Normalizar claves
        for item in lista:
            if "product" in item: item["producto"] = item.pop("product")
            if "name" in item: item["producto"] = item.pop("name")
            if "cantidad" not in item: item["cantidad"] = 1
            if "precio" not in item: item["precio"] = 1000
        return lista
        
    except Exception as e:
        print("Error LLM:", e)
        return [
            {"producto": "Yerba Playadito", "cantidad": 5, "unidad": "kg", "precio": 8500},
            {"producto": "Leche La Serenísima", "cantidad": 24, "unidad": "litros", "precio": 1400},
            {"producto": "Fideos Matarazzo", "cantidad": 15, "unidad": "paquetes", "precio": 1800}
        ]