from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pandas as pd
import os

class ProductEmbedder:
    def __init__(self):
        self.model = SentenceTransformer('intfloat/multilingual-e5-large')  # excelente en español
        self.index = None
        self.products_df = None

    def build_index(self, csv_path="dataset_10000_productos_arg_5_super.csv"):
        df = pd.read_csv(csv_path)
        self.products_df = df
        
        texts = (df['nombre'] + " " + df['categoria']).tolist()
        embeddings = self.model.encode(texts, batch_size=32, show_progress_bar=True)
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner Product = cosine
        self.index.add(embeddings.astype(np.float32))
        
        index_path = "embeddings/faiss_index/index.faiss"
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        faiss.write_index(self.index, index_path)
        print("Índice FAISS creado y guardado")

    def load_index(self):
        self.products_df = pd.read_csv("dataset_10000_productos_arg_5_super.csv")
        index_path = "embeddings/faiss_index/index.faiss"
        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)
        else:
            self.build_index()

    def find_best_match(self, query, k=5):
        query_emb = self.model.encode([query])
        query_emb = query_emb / np.linalg.norm(query_emb)
        scores, indices = self.index.search(query_emb.astype(np.float32), k)
        return [(self.products_df.iloc[i], scores[0][j]) for j, i in enumerate(indices[0])]

embedder = ProductEmbedder()
embedder.load_index()  # una sola vez