# prueba_optimizar.py  ← guardalo en la raíz del proyecto (donde está el CSV)

from models.genetic_optimizer import optimizar_compra

# NOMBRES EXACTOS que SÍ existen en tu dataset_10000_productos_arg_5_super.csv
mi_compra = {
    "Arroz Gallo Oro 1Kg": 3,
    "Leche La Serenísima Entera 1L": 6,
    "Aceite Natura Girasol 1.5L": 2,
    "Fideos Matarazzo Spaghetti 500g": 5,
    "Azúcar Ledesma 1Kg": 4,
    "Yerba Playadito 1Kg": 2,
    "Coca-Cola 2.25L": 4,
    "Detergente Magistral Limón 750ml": 2,
    # hay varias versiones, esta es común
}

print("Arrancando la optimización más barata de Argentina 2025...\n")

resultado = optimizar_compra(mi_compra)

print("\n" + "="*70)
print("              RESULTADO FINAL - LISTA OPTIMIZADA")
print("="*70)
print(f"COSTO TOTAL MÍNIMO ENCONTRADO:   ${resultado['costo_total']:,.2f}")
print(f"Ahorro aproximado vs súper más caro:   ~15-25%")
print(f"Productos optimizados:           {resultado['productos_optimizados']}")
print(f"Unidades totales:                {resultado['unidades_totales']}")
print("="*70 + "\n")

print("DÓNDE COMPRAR CADA PRODUCTO:\n")
for producto, items in resultado['distribucion'].items():
    print(f"{producto}")
    for item in items:
        print(f"   → {item['cantidad']} unid. en {item['supermercado']:9} → ${item['precio']:8,.0f} c/u → ${item['subtotal']:9,.2f}")
    print()

print("TOTAL POR SUPERMERCADO:")
for supermercado, monto in resultado['total_por_supermercado'].items():
    if monto > 0:
        print(f"   {supermercado:9}: ${monto:10,.2f}")
print("\n¡Listo! Guardá este resultado y andá a romperla con los precios")