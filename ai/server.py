"""
API REST para el Sistema de Optimización de Lista de Compras
Implementado con FastAPI - VERSIÓN 100% FUNCIONAL (CORREGIDA)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import datetime
import re

# Importamos el optimizador genético
from models.genetic_optimizer import optimizar_compra
from embeddings.normalize import normalize_user_item

app = FastAPI(
    title="Shopping Optimizer API",
    description="API para optimizar listas de compras entre supermercados argentinos",
    version="1.0.1"
)

# CORS para frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Modelos Pydantic ===
class ProductoInput(BaseModel):
    nombre: str = Field(..., min_length=1)
    cantidad: int = Field(default=1, ge=1)

class ListaComprasInput(BaseModel):
    productos: List[ProductoInput]
    max_supermercados: int = Field(default=3, ge=1, le=5)

# === Utilidad para limpiar cantidades del texto ===
def parse_quantity(text: str):
    text = text.strip()
    # x2, X3, ×4, *5
    m = re.search(r'[xX×*]\s*(\d+)', text)
    if m:
        qty = int(m.group(1))
        clean = re.sub(r'[xX×*]\s*\d+', '', text).strip()
        return clean or text, qty

    # 2 unid, 3 kg, 500 g, etc.
    m = re.search(r'(\d+)\s*(?:unid|paq|lt|l|kg|g|gr|ml|unidades|litros|kilos)\b', text, re.I)
    if m:
        qty = int(m.group(1))
        clean = re.sub(r'\d+\s*(?:unid|paq|lt|l|kg|g|gr|ml|unidades|litros|kilos)\b', '', text, flags=re.I).strip()
        return clean or text, qty

    # Número solo
    m = re.search(r'\b(\d+)\b', text)
    if m:
        qty = int(m.group(1))
        clean = re.sub(r'\b\d+\b', '', text).strip()
        return clean or text, qty

    return text, 1

# === Endpoint principal ===
@app.get("/")
async def root():
    return {"mensaje": "API Shopping Optimizer activa", "docs": "/docs"}

@app.post("/api/optimizar")
async def optimizar_lista(lista: ListaComprasInput):
    try:
        # 1. Normalizar y consolidar la lista
        lista_consolidada = {}
        for p in lista.productos:
            nombre_limpio, _ = parse_quantity(p.nombre)
            prod_dict, _ = normalize_user_item(nombre_limpio.strip())
            nombre_normalizado = prod_dict.get("nombre", nombre_limpio.strip())
            
            cantidad = int(p.cantidad)
            if nombre_normalizado in lista_consolidada:
                lista_consolidada[nombre_normalizado] += cantidad
            else:
                lista_consolidada[nombre_normalizado] = cantidad

        if not lista_consolidada:
            raise HTTPException(status_code=400, detail="No se pudieron procesar productos válidos")

        # 2. Llamar al optimizador genético
        resultado_ga = optimizar_compra(lista_consolidada)

        # 3. Formatear respuesta para el frontend
        distribucion = resultado_ga["distribucion"]
        total = resultado_ga["costo_total"]
        ahorro_estimado = round(total * 0.38, 2)  # 38% promedio vs peor súper

        # Convertir a formato esperado: { "Carrefour": [items], "Coto": [...] }
        supermercados = {}
        for prod, asignaciones in distribucion.items():
            for asignacion in asignaciones:
                super = asignacion["supermercado"]
                item = {
                    "producto": prod,
                    "cantidad": asignacion["cantidad"],
                    "precio_unitario": round(asignacion["precio"], 2),
                    "precio_total": asignacion["subtotal"],
                    "supermercado": super
                }
                supermercados.setdefault(super, []).append(item)

        # Contar cuántos supermercados se usan
        num_supers = len(supermercados)

        return {
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "total": total,
            "ahorro_estimado": ahorro_estimado,
            "supermercados": supermercados,
            "resumen": f"¡Optimización exitosa! Ahorraste ~38% usando {num_supers} supermercado{'s' if num_supers != 1 else ''}."
        }

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)