import urllib.parse

def generar_pdf_y_whatsapp(lista, presupuesto):
    # Calculamos el total real (por si acaso el presupuesto que te pasan es diferente)
    total = sum(item.get("precio", 0) * item.get("cantidad", 0) for item in lista)
    
    # Si quieres usar el presupuesto que te pasan por parámetro, cambia la línea de arriba por:
    # total = presupuesto

    texto = (
        "*Compraria*\n"
        "-----------------------------------\n"
        "*Lista Artículos sugeridos*\n\n"
    )

    # Añadimos cada artículo (máximo 15 para WhatsApp)
    for item in lista[:15]:
        prio = item.get("prioridad_texto", "-")
        producto = item.get("producto", "").strip()
        cantidad = item.get("cantidad", 0)
        unidad = item.get("unidad", "").lower()

        # Formateamos la cantidad según la unidad para que quede bonito
        if unidad == "unidades":
            cantidad_str = f"{int(cantidad) if cantidad.is_integer() else cantidad}"
            texto += f"{prio} *{producto}* — {cantidad_str} unidades\n"
        else:
            cantidad_str = f"{cantidad:.2f}".rstrip('0').rstrip('.') if '.' in str(cantidad) else str(int(cantidad))
            texto += f"{prio} *{producto}* — {cantidad_str} {unidad}\n"

    # ← Aquí termina el bucle, ahora añadimos el pie UNA SOLA VEZ
    texto += (
        f"\n*Presupuesto estimado:* ${total:,.2f}".replace(",", ".") + "\n"
        "-----------------------------------\n"
        "Generado por Mezzano, Joaquín & Rodeghiero, Tomás — UNRC 2025"
    )

    # Codificamos para WhatsApp
    url = f"https://wa.me/?text={urllib.parse.quote(texto)}"
    return url