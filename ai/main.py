import sys
import re
from typing import List, Dict, Tuple, Any
from collections import defaultdict
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv

from embeddings.normalize import normalize_user_item

# ====================== CONFIGURACIÓN ======================
MAX_SUPERMERCADOS = 3
PORCENTAJE_AHORRO_ESTIMADO = 0.38
SEPARADOR_ITEMS = ','
ANCHO_LINEA = 90

# Mapeo de columnas CSV a nombres de supermercados
SUPERMERCADOS_MAP = {
    'precio_carrefour': 'Carrefour',
    'precio_coto': 'Coto',
    'precio_dia': 'Dia',
    'precio_jumbo': 'Jumbo',
    'precio_changomas': 'Changomas'
}


class OptimizadorCompras:
    """Optimizador inteligente de listas de compras para Argentina."""

    def __init__(self, max_supermercados: int = MAX_SUPERMERCADOS):
        load_dotenv()
        self.max_supermercados = max_supermercados

    @staticmethod
    def parse_quantity(text: str) -> Tuple[str, int]:
        """Detecta cantidades como 'x3', '2kg', '3 unid', etc."""
        text = text.strip()

        # Caso: leche x3, leche * 2, leche X4
        m = re.search(r'[xX×\*]\s*(\d+)', text)
        if m:
            return re.sub(r'[xX×\*]\s*\d+', '', text).strip(), int(m.group(1))

        # Caso: 2 kg arroz, 500ml aceite, 3 unid
        m = re.search(r'(\d+)\s*(kg|kilos?|lt|litros?|l|ml|g|gr|unid|paq|unidades?)\b', text, re.IGNORECASE)
        if m:
            cantidad = int(m.group(1))
            nombre = re.sub(r'\d+\s*(kg|kilos?|lt|litros?|l|ml|g|gr|unid|paq|unidades?)\b', '', text, flags=re.IGNORECASE)
            return nombre.strip(), cantidad

        # Caso: 3 manzanas
        m = re.search(r'^(\d+)', text)
        if m:
            return text[len(m.group(1)):].strip(), int(m.group(1))

        return text, 1

    def procesar_entrada(self, entrada: str) -> List[str]:
        """Divide la entrada en items limpios."""
        items = [item.strip() for item in entrada.replace('\n', ',').split(',') if item.strip()]
        return items

    def _safe_price(self, precio) -> float:
        """Convierte cualquier precio a float o inf si no es válido."""
        if precio in (None, '', 'N/A', 'Sin precio'):
            return float('inf')
        if pd.isna(precio):
            return float('inf')
        try:
            val = float(precio)
            return val if val > 0 else float('inf')
        except (ValueError, TypeError):
            return float('inf')

    def normalizar_items(self, items_raw: List[str]) -> List[Dict[str, Any]]:
        """Convierte texto plano → productos con todas las opciones de supermercados."""
        items_normalizados = []

        print("Normalizando productos...")
        for item_raw in items_raw:
            nombre_limpio, cantidad = self.parse_quantity(item_raw)
            producto_dict, score = normalize_user_item(nombre_limpio)

            # Obtener el nombre del producto
            nombre_producto = producto_dict.get('nombre', nombre_limpio.title())
            
            # Crear una entrada por cada supermercado con su precio
            opciones = []
            for col_precio, nombre_super in SUPERMERCADOS_MAP.items():
                precio = self._safe_price(producto_dict.get(col_precio))
                opciones.append({
                    'nombre': nombre_producto,
                    'producto': nombre_producto,
                    'supermercado': nombre_super,
                    'precio': precio,
                    'marca': producto_dict.get('marca', ''),
                    'categoria': producto_dict.get('categoria', ''),
                })
            
            # Encontrar la mejor opción para mostrar
            mejor_opcion = min(opciones, key=lambda x: x['precio'])
            precio_texto = f"${mejor_opcion['precio']:,.0f}" if mejor_opcion['precio'] != float('inf') else "Sin precio"
            
            print(f"Found: {item_raw:<45} → {nombre_producto:<40} | {mejor_opcion['supermercado']:<12} | {precio_texto} ×{cantidad}")
            
            # Agregar todas las opciones (para poder optimizar después)
            for _ in range(cantidad):
                items_normalizados.extend(opciones)

        return items_normalizados

    def optimizar_distribucion(self, items: List[Dict]) -> Tuple[List[Dict], float]:
        """Asigna productos al mejor supermercado respetando límite."""
        print(f"\nOptimizando ítems (máx. {self.max_supermercados} supermercados)...")

        # Agrupar por nombre de producto
        grupos = defaultdict(list)
        for item in items:
            grupos[item['nombre']].append(item)

        usados = defaultdict(int)
        resultado = []

        for nombre, lista_items in grupos.items():
            # Obtener opciones únicas por supermercado
            opciones = {}
            for item in lista_items:
                super_nombre = item['supermercado']
                precio = item['precio']
                if super_nombre not in opciones or precio < opciones[super_nombre]['precio']:
                    opciones[super_nombre] = {'item': item, 'precio': precio}

            # Ordenar: primero supermercados ya usados, luego más barato
            opciones_ordenadas = sorted(
                opciones.items(),
                key=lambda x: (
                    usados[x[0]] == 0,   # False = ya usado → prioridad
                    x[1]['precio'] if x[1]['precio'] != float('inf') else 999999
                )
            )

            # Contar cuántas unidades necesitamos de este producto
            # Como duplicamos por cada supermercado, dividimos por la cantidad de supermercados
            unidades_necesarias = len(lista_items) // len(SUPERMERCADOS_MAP)

            # Asignar cada unidad
            for _ in range(unidades_necesarias):
                asignado = False
                for super_nombre, datos in opciones_ordenadas:
                    if usados[super_nombre] > 0 or len(usados) < self.max_supermercados:
                        nuevo = datos['item'].copy()
                        resultado.append(nuevo)
                        usados[super_nombre] += 1
                        asignado = True
                        break

                if not asignado and opciones_ordenadas:
                    # Forzar el más barato
                    super_nombre, datos = opciones_ordenadas[0]
                    nuevo = datos['item'].copy()
                    resultado.append(nuevo)
                    usados[super_nombre] += 1

        # Total real
        total = sum(item['precio'] for item in resultado if item['precio'] != float('inf'))

        print(f"Distribución optimizada en {len(usados)} supermercado(s):")
        for sup, cant in sorted(usados.items(), key=lambda x: -x[1]):
            print(f"  • {sup}: {cant} producto(s)")

        return resultado, total

    @staticmethod
    def agrupar_por_supermercado(items: List[Dict]) -> Dict[str, List[Dict]]:
        grupos = defaultdict(list)
        for item in items:
            grupos[item['supermercado']].append(item)
        return dict(grupos)

    def mostrar_resultado(self, por_supermercado: Dict[str, List[Dict]], total: float) -> str:
        separador = "=" * ANCHO_LINEA
        print(f"\n{separador}")
        print("       LISTA DE COMPRAS OPTIMIZADA       ".center(ANCHO_LINEA))
        print(f"{separador}")

        fecha = datetime.now().strftime('%d/%m/%Y')
        texto_wsp = f"*LISTA OPTIMIZADA - {fecha}*\n"
        texto_wsp += f"*Total estimado: ${total:,.0f}*\n\n"

        total_con_precio = 0

        for supermercado, items in sorted(por_supermercado.items()):
            print(f"\n{supermercado.upper()}")
            texto_wsp += f"*{supermercado.upper()}*\n"

            subtotal = 0
            for item in items:
                if item['precio'] == float('inf'):
                    precio_texto = "Sin precio"
                else:
                    precio_texto = f"${item['precio']:,.0f}"
                    subtotal += item['precio']
                    total_con_precio += item['precio']

                print(f"  • {item['producto']:<50} {precio_texto:>15}")
                texto_wsp += f"• {item['producto']} — {precio_texto}\n"

            if subtotal > 0:
                print(f"  {'Subtotal':<52} ${subtotal:>15,.0f}")
                texto_wsp += f"_Subtotal: ${subtotal:,.0f}_\n\n"

        ahorro = int(total_con_precio * PORCENTAJE_AHORRO_ESTIMADO)
        print(f"\n{'TOTAL CON PRECIO:':<52} ${total_con_precio:>15,.0f}")
        print(f"{'AHORRO ESTIMADO:':<52} ${ahorro:>15,.0f}")
        print(f"{separador}")

        texto_wsp += f"\n*TOTAL: ${total_con_precio:,.0f}*\n"
        texto_wsp += f"*Ahorro estimado: ${ahorro:,.0f}*"

        return texto_wsp

    def ejecutar(self, entrada: str) -> Dict[str, Any]:
        print("\n" + "=" * ANCHO_LINEA)
        print("          PROCESANDO TU LISTA DE COMPRAS          ".center(ANCHO_LINEA))
        print("=" * ANCHO_LINEA + "\n")

        items_raw = self.procesar_entrada(entrada)
        print(f"{len(items_raw)} producto(s) detectado(s)\n")

        items_normalizados = self.normalizar_items(items_raw)

        lista_optimizada, total = self.optimizar_distribucion(items_normalizados)

        por_supermercado = self.agrupar_por_supermercado(lista_optimizada)

        texto_whatsapp = self.mostrar_resultado(por_supermercado, total)

        return {
            'total': total,
            'texto_whatsapp': texto_whatsapp,
            'num_supermercados': len(por_supermercado),
            'por_supermercado': por_supermercado
        }


def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py \"leche, yerba playadito 1kg, coca cola 2.25\"")
        sys.exit(1)

    entrada = " ".join(sys.argv[1:])
    opt = OptimizadorCompras()
    resultado = opt.ejecutar(entrada)

    print("\n✅ Listo! Podés copiar esto a WhatsApp:")
    print("\n" + resultado['texto_whatsapp'])


if __name__ == "__main__":
    main()