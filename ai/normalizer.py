import re

# Variable global para cachear el embedder
_embedder_cache = None

def get_embedder():
    """
    Obtiene el embedder singleton (se carga una sola vez)
    """
    global _embedder_cache
    if _embedder_cache is None:
        from embeddings.embeddingModel import ProductEmbedder
        print("🔄 Cargando modelo de embeddings (solo primera vez)...")
        _embedder_cache = ProductEmbedder()
        _embedder_cache.load_index()
        print("✅ Modelo cargado\n")
    return _embedder_cache


def normalize_user_item(texto_usuario, embedder=None, k=5):
    """
    Normaliza UN solo producto del usuario usando embeddings.
    Devuelve (producto_dict, score)
    """
    if embedder is None:
        embedder = get_embedder()

    clean = re.sub(r"\s+", " ", texto_usuario.lower().strip())
    matches = embedder.find_best_match(clean, k=k)
    best_row, score = matches[0]

    return best_row, float(score)


def normalize_shopping_list(text, embedder=None, k=5):
    """
    Normaliza una lista completa de productos
    """
    if embedder is None:
        embedder = get_embedder()
    
    raw_items = [x.strip() for x in text.split(",") if x.strip()]
    normalized = []

    for item in raw_items:
        print(f"🔎 Normalizando: {item}")

        clean = re.sub(r"\s+", " ", item.lower().strip())
        matches = embedder.find_best_match(clean, k=k)
        best_row, score = matches[0]

        normalized.append({
            "input": item,
            "match": best_row["nombre"],
            "categoria": best_row["categoria"],
            "score": float(score),
            "row": best_row
        })

        print(f"✅ Match: {best_row['nombre']} (score={score:.3f})")

    return normalized