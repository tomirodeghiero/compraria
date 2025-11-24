# ver_csv.py
from pathlib import Path
import pandas as pd

# Ruta automática: busca el CSV en la raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = "/Users/tomasrodeghiero/Documents/UNRC/inteligencia-artificial-unrc/compraria/ai/dataset_10000_productos_arg_5_super.csv"

print(f"ERROR: No se encontró el archivo en {CSV_PATH}")
print("Asegurate de que el CSV esté en la misma carpeta que este script o en la raíz del proyecto.")
try:
    # Leemos solo las primeras 2 filas (cabecera + primera fila de datos)
    df = pd.read_csv(CSV_PATH, nrows=1)  # solo 1 fila de datos
    print("ARCHIVO ENCONTRADO")
    print("="*80)
    print("COLUMNA (cabecera):")
    print(list(df.columns))
    print("\nPRIMERA FILA DE DATOS:")
    primera_fila = pd.read_csv(CSV_PATH, nrows=1).iloc[0]
    for col, valor in primera_fila.items():
        print(f"  {col:25} → {valor}")
    print("="*80)
    
    # Bonus: cantidad total de filas
    total_filas = len(pd.read_csv(CSV_PATH))
    print(f"Total de productos en el dataset: {total_filas:,}")
    
except Exception as e:
    print(f"Error al leer el CSV: {e}")