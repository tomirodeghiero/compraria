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
        # Resolve path relative to the package if a relative path was passed
        if not os.path.isabs(csv_path):
            base_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
            csv_path = os.path.join(base_dir, os.path.basename(csv_path))

        print(f"Loading CSV from: {csv_path}")
        df = pd.read_csv(csv_path)
        self.products_df = df

        texts = (df['nombre'].fillna('') + " " + df['categoria'].fillna('')).tolist()
        total_texts = len(texts)
        print(f"Productos en CSV: {len(df)}, textos a codificar: {total_texts}")

        # Encode in chunks to avoid OOM / partial encodes
        chunk_size = 512
        emb_list = []
        for i in range(0, total_texts, chunk_size):
            chunk = texts[i:i+chunk_size]
            print(f"Encoding chunk {i}..{i+len(chunk)-1} (size={len(chunk)})")
            emb = self.model.encode(chunk, batch_size=32, show_progress_bar=False)
            emb_list.append(emb)

        if len(emb_list) == 1:
            embeddings = emb_list[0]
        else:
            embeddings = np.vstack(emb_list)

        # normalize
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner Product = cosine
        self.index.add(embeddings.astype(np.float32))

        # ensure index directory is inside embeddings package
        index_dir = os.path.join(os.path.dirname(__file__), 'faiss_index')
        os.makedirs(index_dir, exist_ok=True)
        index_path = os.path.join(index_dir, 'index.faiss')
        faiss.write_index(self.index, index_path)
        print(f"Índice FAISS creado y guardado en: {index_path} (ntotal={self.index.ntotal})")

    def load_index(self):
        # load CSV relative to package
        csv_default = os.path.join(os.path.normpath(os.path.join(os.path.dirname(__file__), '..')), 'dataset_10000_productos_arg_5_super.csv')
        if os.path.exists(csv_default):
            self.products_df = pd.read_csv(csv_default)
        else:
            # fallback to current working dir
            self.products_df = pd.read_csv('dataset_10000_productos_arg_5_super.csv')

        index_path = os.path.join(os.path.dirname(__file__), 'faiss_index', 'index.faiss')
        if os.path.exists(index_path):
            print(f"Cargando índice desde: {index_path}")
            self.index = faiss.read_index(index_path)
            print(f"Índice cargado, ntotal={self.index.ntotal}")
        else:
            print("No se encontró índice FAISS, construyendo uno nuevo...")
            self.build_index(csv_path=csv_default)

    def find_best_match(self, query, k=5):
        query_emb = self.model.encode([query])
        query_emb = query_emb / np.linalg.norm(query_emb)
        scores, indices = self.index.search(query_emb.astype(np.float32), k)
        return [(self.products_df.iloc[i], scores[0][j]) for j, i in enumerate(indices[0])]

embedder = ProductEmbedder()
embedder.load_index()  # una sola vez