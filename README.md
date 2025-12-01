# Compraria

**Generador inteligente de listas de compras optimizadas**

Proyecto final — Inteligencia Artificial
Facultad de Ciencias Exactas, Físico-Químicas y Naturales — Universidad Nacional de Río Cuarto

**Autores:** Joaquín Mezzano, Tomás Rodeghiero

**Resumen**
- Compraria optimiza listas de compra entre varios supermercados argentinos usando embeddings, un optimizador genético y generación de texto mediante un LLM para explicar las decisiones.

**Requisitos**
- Python 3.10–3.12
- Node.js ≥ 18
- `pip` y `yarn` (o `npm`)
- Clave API de OpenAI (variable de entorno `OPENAI_API_KEY`)

**Estructura relevante**
- `ai/`: backend y componentes de IA (embeddings, optimizador, servidor FastAPI, cliente LLM)
- `ai/llm/prompts/explanation_prompt.txt`: prompt usado para generar explicaciones con el LLM
- `frontend/`: aplicación Next.js (UI)

**Instalación y ejecución — Backend (AI)**

1. Abrir la carpeta `ai` y crear/activar un virtualenv:

```bash
cd ai
python3 -m venv venv
source venv/bin/activate
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Exportar la API key de OpenAI (o crear un archivo `.env` con `OPENAI_API_KEY`):

```bash
export OPENAI_API_KEY="tu_api_key_aqui"
# o crear ai/.env con: OPENAI_API_KEY=tu_api_key_aqui
```

4. Ejecutar el servidor FastAPI:

```bash
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

Endpoints principales del backend
- `GET /` — estado básico de la API
- `POST /api/optimizar` — optimiza la lista de productos y devuelve la distribución por supermercado, total y `explanation` (texto generado por LLM). Payload:

```json
{
    "productos": [{"nombre":"leche x2","cantidad":2}, {"nombre":"pan","cantidad":1}],
    "max_supermercados": 3
}
```

**Instalación y ejecución — Frontend (Next.js)**

1. Abrir la carpeta `frontend`:

```bash
cd frontend
yarn install
yarn dev
```

2. Acceder a `http://localhost:3000` en el navegador.

**LLM / OpenAI**
- El cliente de OpenAI está en `ai/llm/client.py`. Usa la variable de entorno `OPENAI_API_KEY`.
- El prompt base está en `ai/llm/prompts/explanation_prompt.txt` y se puede personalizar para cambiar el tono, formato y longitud de la explicación.
- Modelo usado por defecto: `gpt-4o-mini` (puedes cambiarlo en `client.py`).

**Frontend: dónde se muestra la explicación**
- `frontend/src/components/custom/results-panel.tsx` muestra `explanation` (si existe) justo debajo del encabezado del panel de resultados.

**Pruebas rápidas**
- Ejecuta backend y frontend como arriba. Desde la UI agrega productos y presiona "Optimizar con Genético"; la respuesta mostrará el resumen y, si la llamada al LLM fue exitosa, una explicación en el panel de resultados.

**Consejos y notas**
- Si la generación del LLM falla (p. ej. sin API key o error de red), el backend incluye un mensaje de error en el campo `explanation` en vez de romper la respuesta.
- Para producción: considera hacer la llamada al LLM de forma asíncrona (background task) y retornar una respuesta inmediata al usuario, o cachear explicaciones para listas idénticas.

**Contacto (GitHub)**
- Joaquín Mezzano (@joaquinmezzano)
- Tomás Rodeghiero (@tomirodeghiero)

-- Fin
