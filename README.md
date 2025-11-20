# Compraria

**Generador Inteligente de Lista de Compras Mensual para el Hogar**

Proyecto Final – Inteligencia Artificial
Facultad de Ciencias Exactas, Físico-Químicas y Naturales
Universidad Nacional de Río Cuarto

**Autores:** Joaquín Mezzano, Tomás Rodeghiero

## Descripción

Compraria es un sistema web que integra técnicas de inteligencia artificial para generar automáticamente listas de compras mensuales personalizadas. Incorpora embeddings vectoriales, modelos de lenguaje, algoritmos genéticos, predicción con XGBoost y clasificación con redes neuronales.

## Requisitos del Sistema

- Python 3.10 – 3.12
- Node.js ≥ 18
- Clave API de OpenAI

## Instalación y Ejecución

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tomirodeghiero/compraria.git
cd compraria
```

---

## 2. Configuración del Servidor (Carpeta `ai/`)

Entrar al módulo de IA:

```bash
cd ai
```

### Crear entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate    # Linux/macOS
# venv\Scripts\activate     # Windows
```

### Instalar dependencias

```bash
pip install -r requirements.txt
```

### Ejecutar el optimizador / sistema por consola

Podés probar el sistema de IA directamente desde terminal con:

```bash
python3 main.py "leche descremada, yerba playadito 1kg, arroz, coca cola 2.25, bizcochitos don satur, jabon dove"
```

### Ejecutar el server

Es posible ejecutar el servidor mediante el comando:

```bash
uvicorn server:app --reload --port 8000
```

Esto ejecuta el pipeline completo de embeddings + normalización + optimizador.

## 3. Configuración del Frontend (Next.js)

```bash
cd frontend
yarn install
yarn dev
```

La aplicación queda disponible en:

**[http://localhost:3000](http://localhost:3000)**

## Estructura del Proyecto

```
compraria/
├── ai/                # Módulo principal de IA (embeddings, LLM, GA, etc.)
│   ├── main.py
│   ├── embeddings/
│   ├── optimizer/
│   ├── models/
│   └── prompt/
└── frontend/          # Next.js 16
    └── src/app/
```

## Tecnologías Implementadas

- **Búsqueda semántica:** Embeddings + normalización vectorial
- **Generación de listas:** GPT-4o-mini
- **Optimización:** Algoritmo Genético (DEAP)
- **Predicción:** XGBoost
- **Clasificación:** Red Neuronal (PyTorch)
- **Frontend:** Next.js 14 + Tailwind CSS
- **Backend/IA Server:** Python

**Universidad Nacional de Río Cuarto – 2025**
