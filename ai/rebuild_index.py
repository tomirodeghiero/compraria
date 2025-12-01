#!/usr/bin/env python3
"""
Script para reconstruir el índice FAISS con los prefijos correctos del modelo E5
"""

from embeddings.embeddingModel import ProductEmbedder

def main():
    print("=" * 70)
    print("RECONSTRUYENDO ÍNDICE FAISS CON PREFIJOS E5")
    print("=" * 70)
    print()
    
    embedder = ProductEmbedder()
    embedder.build_index("dataset_10000_productos_arg_5_super.csv")
    
    print()
    print("=" * 70)
    print("✅ ÍNDICE RECONSTRUIDO EXITOSAMENTE")
    print("=" * 70)
    print()

if __name__ == "__main__":
    main()