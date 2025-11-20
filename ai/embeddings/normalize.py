from embeddings.embeddingModel import embedder

def normalize_user_item(user_text):
    matches = embedder.find_best_match(user_text, k=10)
    # Devuelve el mejor match con score > 0.80, sino el más alto
    for product_row, score in matches:
        if score > 0.80:
            return product_row.to_dict(), score
    # fallback
    return matches[0][0].to_dict(), matches[0][1]
