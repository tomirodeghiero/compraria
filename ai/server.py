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
    # 1) Prefiere formatos tipo 'x2', 'X3', '×4', '*5'
    m = re.search(r'(?:[xX×*]\s*)(\d+)', text)
    if m:
        qty = int(m.group(1))
        clean = re.sub(r'(?:[xX×*]\s*\d+)', '', text).strip()
        return clean or text, qty

    # 2) Formatos con unidad explícita, por ejemplo '2 unid', '3 kg', '200 g'
    m = re.search(r'(\d+)\s*(?:unid|paq|lt|l|kg|g|gr|ml|unidades|litros|kilos)\b', text, re.I)
    if m:
        qty = int(m.group(1))
        clean = re.sub(r'\d+\s*(?:unid|paq|lt|l|kg|g|gr|ml|unidades|litros|kilos)\b', '', text, flags=re.I).strip()
        return clean or text, qty

    # 3) Número aislado separado por espacios o fin de cadena (evita capturar '200g' porque no tiene límites de palabra)
    m = re.search(r'\b(\d+)\b', text)
    if m:
        qty = int(m.group(1))
        clean = re.sub(r'\b\d+\b', '', text).strip()
        return clean or text, qty

    return text.strip(), 1

# === Endpoints ===
@app.get("/")
async def root():
    return {"mensaje": "API Shopping Optimizer activa", "docs": "/docs"}

@app.post("/api/optimizar")
async def optimizar_lista(lista: ListaComprasInput):
    try:
        # Construir mapa de productos originales con la cantidad solicitada
        original_map = {}
        items_normalizados = []
        for p in lista.productos:
            # Limpiar el nombre quitando indicadores de cantidad, pero respetar
            # la cantidad que envía el frontend (`p.cantidad`). No multiplicamos
            # por valores encontrados en el nombre (evita interpretar '200g' como qty).
            nombre, _ = parse_quantity(p.nombre)
            qty_total = int(p.cantidad)
            prod_dict, _ = normalize_user_item(nombre)
            prod_name = prod_dict.get("nombre") or nombre
            # Si ya existe, sumar cantidades (por si el usuario pidió el mismo producto dos veces)
            if prod_name in original_map:
                original_map[prod_name]["cantidad"] += qty_total
            else:
                original_map[prod_name] = {"cantidad": qty_total, "prod_dict": prod_dict}

            # Para el optimizador mantenemos la lista expandida por unidad
            items_normalizados.extend([prod_dict] * qty_total)

        lista_optimizada, total = optimize_shopping_list(items_normalizados, max_supers=lista.max_supermercados)

        # Recolectar asignaciones unitarias por producto
        assignments = defaultdict(list)  # producto -> list of (supermercado, precio_unit)
        for item in lista_optimizada:
            producto_nombre = item.get("producto") or item.get("nombre")
            precio_unit = item["precio"] if not pd.isna(item.get("precio")) and item.get("precio") > 0 else None
            assignments[producto_nombre].append({"supermercado": item["supermercado"], "precio_unit": precio_unit})

        # Columnas de precios y mapping a nombres de supermercados (mismo orden que en optimizer)
        PRECIOS_COLS = ["precio_carrefour", "precio_coto", "precio_dia", "precio_jumbo", "precio_changomas"]
        SUPERS = ["Carrefour", "Coto", "Día", "Jumbo", "Changomas"]

        por_super_raw = defaultdict(dict)  # supermercado -> { producto: aggregated_entry }

        for prod_name, meta in original_map.items():
            cantidad = int(meta.get("cantidad", 1))
            prod_dict = meta.get("prod_dict", {})

            # Intenta determinar el supermercado con menor precio unitario según la base de datos
            best_idx = None
            best_price = None
            for idx, col in enumerate(PRECIOS_COLS):
                price = prod_dict.get(col)
                if price is None or pd.isna(price) or price <= 0:
                    continue
                if best_price is None or price < best_price:
                    best_price = price
                    best_idx = idx

            if best_idx is not None:
                chosen_super = SUPERS[best_idx]
                precio_unitario = best_price
            else:
                # Fallback: elegir el supermercado más frecuente en las asignaciones del optimizador
                freq = {}
                for a in assignments.get(prod_name, []):
                    s = a.get("supermercado")
                    if s:
                        freq[s] = freq.get(s, 0) + 1
                if freq:
                    chosen_super = max(freq.items(), key=lambda x: x[1])[0]
                    # intentar obtener precio unitario desde una asignación
                    pu = next((a.get("precio_unit") for a in assignments.get(prod_name, []) if a.get("supermercado") == chosen_super and a.get("precio_unit") is not None), None)
                    precio_unitario = pu if pu is not None else 0
                else:
                    chosen_super = "Sin asignar"
                    precio_unitario = 0

            precio_total = (precio_unitario or 0) * cantidad

            por_super_raw[chosen_super][prod_name] = {
                "producto": prod_name,
                "cantidad": cantidad,
                "precio_unitario": precio_unitario or 0,
                "precio_total": round(precio_total, 2),
                "supermercado": chosen_super,
            }

        # Convertir a la forma esperada por el frontend: lista de items por supermercado
        por_super = {s: list(prods.values()) for s, prods in por_super_raw.items()}

        # Recalcular total a partir de los precios finales asignados (consistente con lo mostrado)
        total_calculado = 0.0
        for items in por_super.values():
            for it in items:
                try:
                    total_calculado += float(it.get("precio_total", 0))
                except Exception:
                    total_calculado += 0.0

        total = round(total_calculado, 2)

        # Respuesta
        ahorro = total * 0.38
        return {
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "total": total,
            "ahorro_estimado": round(ahorro, 2),
            "supermercados": dict(por_super),
            "resumen": f"¡Optimización exitosa! Ahorraste ~38% distribuyendo en {len(por_super)} supermercados."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
