from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pandas as pd
import os

class ProductEmbedder:
    def __init__(self):
        print("📦 Inicializando modelo de embeddings...")
        self.model = SentenceTransformer('intfloat/multilingual-e5-large')
        print("✅ Modelo cargado")
        self.index = None
        self.products_df = None

    def build_index(self, csv_path="dataset_10000_productos_arg_5_super.csv"):
        # Resolve path relative to the package if a relative path was passed
        if not os.path.isabs(csv_path):
            base_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
            csv_path = os.path.join(base_dir, os.path.basename(csv_path))

        print(f"📊 Cargando CSV: {csv_path}")
        df = pd.read_csv(csv_path)
        self.products_df = df

        # Add "passage: " prefix for e5 models (recommended by authors)
        texts = ["passage: " + (str(row['nombre']) + " " + str(row['categoria'])) 
                 for _, row in df.iterrows()]
        total_texts = len(texts)
        print(f"Total productos: {len(df)}")

        # Encode in chunks to avoid OOM
        chunk_size = 512
        emb_list = []
        print(f"🔄 Generando embeddings...")
        for i in range(0, total_texts, chunk_size):
            chunk = texts[i:i+chunk_size]
            emb = self.model.encode(chunk, batch_size=64, show_progress_bar=False, convert_to_numpy=True)
            emb_list.append(emb)

        embeddings = np.vstack(emb_list) if len(emb_list) > 1 else emb_list[0]

        # Normalize for cosine similarity
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = embeddings / np.maximum(norms, 1e-10)

        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner Product = cosine
        self.index.add(embeddings.astype(np.float32))

        # Save index
        index_dir = os.path.join(os.path.dirname(__file__), 'faiss_index')
        os.makedirs(index_dir, exist_ok=True)
        index_path = os.path.join(index_dir, 'index.faiss')
        faiss.write_index(self.index, index_path)
        print(f"💾 Índice guardado: {index_path} (productos={self.index.ntotal})")

    def load_index(self):
        # Load CSV
        csv_default = os.path.join(
            os.path.normpath(os.path.join(os.path.dirname(__file__), '..')), 
            'dataset_10000_productos_arg_5_super.csv'
        )
        
        if os.path.exists(csv_default):
            self.products_df = pd.read_csv(csv_default)
        else:
            # fallback
            self.products_df = pd.read_csv('dataset_10000_productos_arg_5_super.csv')

        # Load FAISS index
        index_path = os.path.join(os.path.dirname(__file__), 'faiss_index', 'index.faiss')
        
        if os.path.exists(index_path):
            print(f"📂 Cargando índice FAISS...")
            self.index = faiss.read_index(index_path)
            print(f"✅ Índice cargado ({self.index.ntotal} productos)")
        else:
            print("⚠️  No se encontró índice FAISS, construyendo uno nuevo...")
            self.build_index(csv_path=csv_default)

    def find_best_match(self, query, k=5):
        """
        Busca los k mejores matches para la query
        Retorna: lista de tuplas (row_dict, score)
        """
        # Prepend "query: " prefix for e5 models (recommended by authors)
        prefixed_query = f"query: {query}"
        
        # Encode query
        query_emb = self.model.encode([prefixed_query], convert_to_numpy=True)
        
        # Normalize
        query_emb = query_emb / np.maximum(np.linalg.norm(query_emb), 1e-10)
        
        # Search
        scores, indices = self.index.search(query_emb.astype(np.float32), k)
        
        # Return results
        results = []
        for j, idx in enumerate(indices[0]):
            row = self.products_df.iloc[idx].to_dict()
            score = float(scores[0][j])
            results.append((row, score))
        
        return results