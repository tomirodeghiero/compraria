"""
Sistema de Optimización de Lista de Compras

Este módulo procesa listas de compras, normaliza productos, optimiza la distribución
entre supermercados y genera reportes en PDF y enlaces para WhatsApp.
"""

import sys
import re
import os
import urllib.parse
from typing import List, Dict, Tuple, Any
from collections import defaultdict
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv
from weasyprint import HTML

from embeddings.normalize import normalize_user_item
from optimizer.genetic_algorithm import optimize_shopping_list


# Constantes
MAX_SUPERMERCADOS = 3
PORCENTAJE_AHORRO_ESTIMADO = 0.38
PATRON_CANTIDAD = r'(?:x|X|×|\*)(\d+)|(\d+)\s*(unid|paq|lt|kg|l|unidades|litros|kilos)?'
SEPARADOR_ITEMS = ','
ANCHO_LINEA = 90


class OptimizadorCompras:
    """Clase principal para la optimización de listas de compras."""
    
    def __init__(self, max_supermercados: int = MAX_SUPERMERCADOS):
        """
        Inicializa el optimizador de compras.
        
        Args:
            max_supermercados: Número máximo de supermercados a considerar
        """
        load_dotenv()
        self.max_supermercados = max_supermercados
    
    @staticmethod
    def parse_quantity(text: str) -> Tuple[str, int]:
        """
        Extrae la cantidad y el nombre del producto de un texto.
        
        Args:
            text: Texto que contiene el producto y opcionalmente la cantidad
            
        Returns:
            Tupla con (nombre_producto, cantidad)
        """
        match = re.search(PATRON_CANTIDAD, text, re.IGNORECASE)
        
        if match:
            cantidad = int(match.group(1) or match.group(2) or 1)
            nombre_limpio = re.sub(
                PATRON_CANTIDAD, 
                '', 
                text, 
                flags=re.IGNORECASE
            ).strip()
            return nombre_limpio or text, cantidad
        
        return text.strip(), 1
    
    def procesar_entrada(self, entrada: str) -> List[str]:
        """
        Procesa la entrada del usuario y extrae los items individuales.
        
        Args:
            entrada: Cadena con los productos separados por comas
            
        Returns:
            Lista de items procesados
        """
        items_raw = [
            item.strip() 
            for item in entrada.replace("\n", SEPARADOR_ITEMS).split(SEPARADOR_ITEMS) 
            if item.strip()
        ]
        return items_raw
    
    def normalizar_items(self, items_raw: List[str]) -> List[Dict[str, Any]]:
        """
        Normaliza los items y detecta productos en la base de datos.
        
        Args:
            items_raw: Lista de productos en texto plano
            
        Returns:
            Lista de diccionarios con productos normalizados
        """
        items_normalizados = []
        
        print("Procesando productos y cantidades...\n")
        
        for item_raw in items_raw:
            nombre, cantidad = self.parse_quantity(item_raw)
            producto_dict, score = normalize_user_item(nombre)
            
            # Agregar el producto tantas veces como indique la cantidad
            for _ in range(cantidad):
                items_normalizados.append(producto_dict)
            
            print(f"✓ {item_raw:<55} → {producto_dict['nombre']:<50} ×{cantidad}")
        
        return items_normalizados
    
    def optimizar_distribucion(
        self, 
        items_normalizados: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], float]:
        """
        Optimiza la distribución de productos entre supermercados.
        
        Args:
            items_normalizados: Lista de productos normalizados
            
        Returns:
            Tupla con (lista_optimizada, total)
        """
        print(f"\nOptimizando {len(items_normalizados)} ítems "
              f"(máximo {self.max_supermercados} supermercados)...")
        
        lista_optimizada, total = optimize_shopping_list(
            items_normalizados, 
            max_supers=self.max_supermercados
        )
        
        return lista_optimizada, total
    
    @staticmethod
    def agrupar_por_supermercado(
        lista_optimizada: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Agrupa los productos por supermercado.
        
        Args:
            lista_optimizada: Lista de productos optimizada
            
        Returns:
            Diccionario con productos agrupados por supermercado
        """
        por_supermercado = defaultdict(list)
        
        for item in lista_optimizada:
            por_supermercado[item["supermercado"]].append(item)
        
        return dict(por_supermercado)
    
    def mostrar_resultado(
        self, 
        por_supermercado: Dict[str, List[Dict[str, Any]]], 
        total: float
    ) -> str:
        """
        Muestra el resultado de la optimización en consola.
        
        Args:
            por_supermercado: Productos agrupados por supermercado
            total: Total de la compra
            
        Returns:
            Texto formateado para WhatsApp
        """
        separador = "=" * ANCHO_LINEA
        titulo = "LISTA DE COMPRAS OPTIMIZADA"
        
        print(f"\n{separador}")
        print(f"{titulo:^{ANCHO_LINEA}}")
        print(f"{separador}")
        
        fecha = datetime.now().strftime('%d/%m/%Y')
        texto_whatsapp = f"*LISTA OPTIMIZADA {fecha}* - Total: ${total:,.0f}\n\n"
        
        for supermercado, items in por_supermercado.items():
            print(f"\n{supermercado.upper()}")
            subtotal = 0
            texto_whatsapp += f"*{supermercado.upper()}*\n"
            
            for item in items:
                precio = item["precio"] if not pd.isna(item["precio"]) and item["precio"] > 0 else 0
                subtotal += precio
                print(f"  • {item['producto']:<55} ${precio:>10,.0f}")
                texto_whatsapp += f"• {item['producto']} — ${precio:,.0f}\n"
            
            print(f"  {'Subtotal:':<57} ${subtotal:>10,.0f}")
            texto_whatsapp += f"Subtotal: ${subtotal:,.0f}\n\n"
        
        ahorro_estimado = int(total * PORCENTAJE_AHORRO_ESTIMADO)
        
        print(f"\n{'TOTAL:':<68} ${total:>10,.0f}")
        print(f"{'AHORRO ESTIMADO (~38%):':<68} ${ahorro_estimado:>10,.0f}")
        print(f"{separador}")
        
        return texto_whatsapp
    
    def generar_resumen(self, por_supermercado: Dict, total: float) -> str:
        """
        Genera un resumen explicativo de la optimización.
        
        Args:
            por_supermercado: Productos agrupados por supermercado
            total: Total de la compra
            
        Returns:
            Texto con el resumen
        """
        ahorro = int(total * PORCENTAJE_AHORRO_ESTIMADO)
        total_sin_optimizar = int(total / (1 - PORCENTAJE_AHORRO_ESTIMADO))
        
        resumen = (
            f"\nRESUMEN DE OPTIMIZACIÓN\n"
            f"{'─' * 50}\n\n"
            f"Esta distribución optimizada ofrece las siguientes ventajas:\n\n"
            f"• Utiliza únicamente {len(por_supermercado)} supermercado(s)\n"
            f"• Aprovecha las mejores ofertas disponibles\n"
            f"• Prioriza productos de marca propia cuando son equivalentes\n"
            f"• Total: ${total:,.0f} (vs. ${total_sin_optimizar:,.0f} sin optimizar)\n"
            f"• Ahorro estimado: ${ahorro:,.0f}\n\n"
            f"Recomendación: Realizar la compra en días de menor afluencia "
            f"para mejor disponibilidad de productos.\n"
        )
        
        print(resumen)
        return resumen
    
    def generar_pdf(
        self, 
        por_supermercado: Dict[str, List[Dict[str, Any]]], 
        total: float, 
        nombre_archivo: str = "lista_optimizada.pdf"
    ) -> None:
        """
        Genera un archivo PDF con la lista de compras.
        
        Args:
            por_supermercado: Productos agrupados por supermercado
            total: Total de la compra
            nombre_archivo: Nombre del archivo PDF de salida
        """
        fecha = datetime.now().strftime("%d/%m/%Y")
        ahorro_pct = int(PORCENTAJE_AHORRO_ESTIMADO * 100)
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #34495e; margin-top: 30px; }}
                h3 {{ color: #7f8c8d; }}
                ul {{ list-style-type: none; padding: 0; }}
                li {{ padding: 8px; border-bottom: 1px solid #ecf0f1; }}
            </style>
        </head>
        <body>
            <h1>Lista de Compras Optimizada</h1>
            <h3>Fecha: {fecha}</h3>
            <h2>Total: ${total:,.0f}</h2>
            <h3>Ahorro estimado: ~{ahorro_pct}%</h3>
        """
        
        for supermercado, items in por_supermercado.items():
            html_content += f"<h2>{supermercado.upper()}</h2><ul>"
            
            for item in items:
                precio = item["precio"] if not pd.isna(item["precio"]) else 0
                html_content += f"<li>{item['producto']} — ${precio:,.0f}</li>"
            
            html_content += "</ul>"
        
        html_content += "</body></html>"
        
        HTML(string=html_content).write_pdf(nombre_archivo)
        print(f"\n✓ PDF generado: {nombre_archivo}")
    
    def generar_enlace_whatsapp(self, texto: str, resumen: str) -> str:
        """
        Genera un enlace para compartir por WhatsApp.
        
        Args:
            texto: Texto de la lista de compras
            resumen: Resumen de la optimización
            
        Returns:
            URL para compartir por WhatsApp
        """
        mensaje_completo = texto + "\n" + resumen
        url = "https://wa.me/?text=" + urllib.parse.quote(mensaje_completo)
        
        print(f"✓ Enlace para WhatsApp generado")
        print(f"  {url}\n")
        
        return url
    
    def ejecutar(self, entrada_usuario: str) -> None:
        """
        Ejecuta el proceso completo de optimización.
        
        Args:
            entrada_usuario: Cadena con los productos ingresados por el usuario
        """
        try:
            # 1. Procesar entrada
            items_raw = self.procesar_entrada(entrada_usuario)
            
            # 2. Normalizar items
            items_normalizados = self.normalizar_items(items_raw)
            
            # 3. Optimizar distribución
            lista_optimizada, total = self.optimizar_distribucion(items_normalizados)
            
            # 4. Agrupar por supermercado
            por_supermercado = self.agrupar_por_supermercado(lista_optimizada)
            
            # 5. Mostrar resultado
            texto_whatsapp = self.mostrar_resultado(por_supermercado, total)
            
            # 6. Generar resumen
            resumen = self.generar_resumen(por_supermercado, total)
            
            # 7. Generar PDF
            self.generar_pdf(por_supermercado, total)
            
            # 8. Generar enlace WhatsApp
            self.generar_enlace_whatsapp(texto_whatsapp, resumen)
            
            print("Proceso completado exitosamente.")
            
        except Exception as e:
            print(f"\nError durante la ejecución: {str(e)}", file=sys.stderr)
            sys.exit(1)


def main():
    """Función principal del programa."""
    if len(sys.argv) < 2:
        print("Uso: python script.py <lista de productos>")
        print("Ejemplo: python script.py 'leche x2, pan, arroz 1kg'")
        sys.exit(1)
    
    entrada_usuario = " ".join(sys.argv[1:])
    
    optimizador = OptimizadorCompras(max_supermercados=MAX_SUPERMERCADOS)
    optimizador.ejecutar(entrada_usuario)


if __name__ == "__main__":
    main()