import csv
from collections import Counter

archivo = "dataset_10000_productos_arg_5_super.csv"

# Leer CSV
filas = []
productos = []

with open(archivo, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        filas.append(row)
        productos.append(row[1].strip())

# Detectar repetidos
conteo = Counter(productos)
repetidos = {p for p, c in conteo.items() if c > 1}

print(f"🔍 Productos repetidos detectados: {len(repetidos)}")

# Set dinámico de nombres actuales
nombres_actuales = set(productos)

# Contador de apariciones
apariciones = {}

contador_unico = 1

# Reemplazar SOLO los repetidos
for row in filas:
    nombre = row[1].strip()
    apariciones[nombre] = apariciones.get(nombre, 0) + 1

    if apariciones[nombre] == 1:
        continue

    if nombre in repetidos:
        # Generar nombre único garantizado
        nuevo = f"Producto Único {contador_unico:05d}"
        contador_unico += 1

        print(f"✅ {nombre} → {nuevo}")

        row[1] = nuevo
        nombres_actuales.add(nuevo)

# Guardar archivo
with open(archivo, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(filas)

print("\n✅ Archivo actualizado sin repetidos.")
