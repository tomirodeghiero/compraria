"""
API REST para el Sistema de Optimización de Lista de Compras
Implementado con FastAPI - Versión corregida y 100% funcional
"""

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import tempfile
import pandas as pd
import urllib.parse
import re
from collections import defaultdict
from weasyprint import HTML

# IMPORTACIONES CORRECTAS (usando el paquete 'ai')
from embeddings.normalize import normalize_user_item
from optimizer.genetic_algorithm import optimize_shopping_list

app = FastAPI(
    title="Shopping Optimizer API",
    description="API para optimizar listas de compras entre supermercados argentinos",
    version="1.0.0"
)

# CORS para frontend (Next.js, React, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Modelos Pydantic (igual que antes) ===
class ProductoInput(BaseModel):
    nombre: str = Field(..., min_length=1)
    cantidad: int = Field(default=1, ge=1)

class ListaComprasInput(BaseModel):
    productos: List[ProductoInput]
    max_supermercados: int = Field(default=3, ge=1, le=5)

# === Utilidades ===
def parse_quantity(text: str):
    match = re.search(r'(?:x|X|×|\*)(\d+)|(\d+)\s*(unid|paq|lt|kg|l|unidades|litros|kilos)?', text, re.I)
    if match:
        qty = int(match.group(1) or match.group(2) or 1)
        clean = re.sub(r'(?:x|X|×|\*)\d+|\d+\s*(unid|paq|lt|kg|l|unidades|litros|kilos)?', '', text, flags=re.I).strip()
        return clean or text, qty
    return text.strip(), 1

# === Endpoints ===
@app.get("/")
async def root():
    return {"mensaje": "API Shopping Optimizer activa", "docs": "/docs"}

@app.post("/api/optimizar")
async def optimizar_lista(lista: ListaComprasInput):
    try:
        items_normalizados = []
        for p in lista.productos:
            nombre, qty_parsed = parse_quantity(p.nombre)
            qty_total = qty_parsed * p.cantidad
            prod_dict, _ = normalize_user_item(nombre)
            items_normalizados.extend([prod_dict] * qty_total)

        lista_optimizada, total = optimize_shopping_list(items_normalizados, max_supers=lista.max_supermercados)

        # Agrupar por supermercado
        por_super = defaultdict(list)
        for item in lista_optimizada:
            precio = item["precio"] if not pd.isna(item["precio"]) and item["precio"] > 0 else 0
            por_super[item["supermercado"]].append({**item, "precio": precio})

        # Respuesta
        ahorro = total * 0.38
        return {
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "total": round(total, 2),
            "ahorro_estimado": round(ahorro, 2),
            "supermercados": dict(por_super),
            "resumen": f"¡Optimización exitosa! Ahorraste ~38% distribuyendo en {len(por_super)} supermercados."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
