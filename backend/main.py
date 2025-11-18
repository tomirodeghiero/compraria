from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict
import os
from dotenv import load_dotenv

from services.llm import generar_lista_base
from models.genetic import optimizar_con_genetico
from models.xgboost_predictor import predecir_agotamiento
from models.priority_net import asignar_prioridades
from services.vector_store import buscar_historial, guardar_compra
from services.pdf_whatsapp import generar_pdf_y_whatsapp

load_dotenv()
app = FastAPI(title="ComprAR-IA 🛒🇦🇷")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
os.makedirs("pdfs", exist_ok=True)
app.mount("/pdfs", StaticFiles(directory="pdfs"), name="pdfs")

class Solicitud(BaseModel):
    inventario_actual: Dict[str, float] = {}
    presupuesto: float = 80000
    personas: int = 4
    preferencias: str = ""

@app.post("/generar-lista")
async def generar_lista(solicitud: Solicitud):
    try:
        contexto = buscar_historial(solicitud.personas, solicitud.preferencias)
        lista_base = await generar_lista_base(solicitud.inventario_actual, solicitud.presupuesto, solicitud.personas, solicitud.preferencias, contexto)
        lista_optimizada = optimizar_con_genetico(lista_base, solicitud.presupuesto, solicitud.inventario_actual)

        for item in lista_optimizada:
            item["agotamiento_pronto"] = predecir_agotamiento(item.get("producto", ""))

        lista_final = asignar_prioridades(lista_optimizada)
        guardar_compra(lista_final)
        pdf_url = "https://i.imgur.com/3f2jK8D.png"  # PDF placeholder bonito
        whatsapp_url = generar_pdf_y_whatsapp(lista_final, solicitud.presupuesto)

        total = sum(item.get("precio", 0) * item.get("cantidad", 0) for item in lista_final)

        return {
            "lista": lista_final,
            "total": round(total),
            "pdf": pdf_url,
            "whatsapp": whatsapp_url
        }
    except Exception as e:
        raise HTTPException(500, detail=str(e))