# Compraria

**Generador Inteligente de Lista de Compras Mensual para el Hogar**

Proyecto Final – Inteligencia Artificial  
Facultad de Ciencias Exactas, Físico-Químicas y Naturales  
Universidad Nacional de Río Cuarto

**Autores:** Joaquín Mezzano, Tomás Rodeghiero

---

## Descripción

Compraria es un sistema web que integra técnicas de inteligencia artificial para generar automáticamente listas de compras mensuales personalizadas. Incorpora embeddings vectoriales, modelos de lenguaje, algoritmos genéticos, predicción con XGBoost y clasificación con redes neuronales.

---

## Requisitos del Sistema

- Python 3.10 – 3.12
- Node.js ≥ 18
- Git
- Clave API de OpenAI (opcional)

---

## Instalación y Ejecución

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tomirodeghiero/compraria.git
cd compraria
```

### 2. Configuración del Backend

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install fastapi "uvicorn[standard]" openai chromadb deap xgboost torch pandas joblib reportlab python-dotenv

# Configurar variables de entorno (opcional)
cp backend/.env.example backend/.env
# Editar backend/.env con OPENAI_API_KEY

# Crear directorios necesarios
mkdir -p backend/pdfs backend/chroma_db backend/models

# Ejecutar servidor
cd backend
uvicorn main:app --reload --port=8000
```

**API disponible en:** http://localhost:8000  
**Documentación:** http://localhost:8000/docs

### 3. Configuración del Frontend

```bash
# En terminal independiente
cd frontend
yarn install
yarn dev
```

**Aplicación disponible en:** http://localhost:3000

---

## Estructura del Proyecto

```
compraria/
├── backend/          # API FastAPI
│   ├── main.py
│   ├── services/
│   ├── models/
│   └── chroma_db/
└── frontend/         # Next.js 14
    └── src/app/
```

---

## Tecnologías Implementadas

- **Búsqueda semántica:** ChromaDB + OpenAI Embeddings
- **Generación de listas:** GPT-4o-mini
- **Optimización:** Algoritmo Genético (DEAP)
- **Predicción:** XGBoost
- **Clasificación:** Red Neuronal PyTorch
- **Frontend:** Next.js 14 + Tailwind CSS
- **Backend:** FastAPI + Python

---

**Universidad Nacional de Río Cuarto – 2025**
# compraria
# compraria
