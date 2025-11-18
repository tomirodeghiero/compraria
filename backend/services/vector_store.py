import chromadb
chroma = chromadb.PersistentClient(path="../chroma_db")
collection = chroma.get_or_create_collection("historial")

def embed(text): 
    return [0.0] * 768  # fake embedding

def buscar_historial(personas, preferencias):
    return "Historial: mucho asado, sin TACC, 4 personas"

def guardar_compra(lista):
    pass
