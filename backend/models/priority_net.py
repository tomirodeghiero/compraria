def asignar_prioridades(lista):
    for item in lista:
        if item.get("agotamiento_pronto"):
            item["prioridad_texto"] = "Alta 🔴"
        elif "Yerba" in item["producto"] or "Leche" in item["producto"]:
            item["prioridad_texto"] = "Alta 🔴"
        elif "Carne" in item["producto"]:
            item["prioridad_texto"] = "Media 🟡"
        else:
            item["prioridad_texto"] = "Baja 🟢"
    return sorted(lista, key=lambda x: ["Baja 🟢", "Media 🟡", "Alta 🔴"].index(x["prioridad_texto"]), reverse=True)