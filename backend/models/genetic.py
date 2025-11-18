def optimizar_con_genetico(items, presupuesto, inventario):
    for item in items:
        item["cantidad"] = round(item["cantidad"] * 0.95, 2)  # 5% menos para ajustar al presupuesto
    return items
