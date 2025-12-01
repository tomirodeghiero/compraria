import sys
import re
from typing import List, Tuple, Dict, Any
from collections import defaultdict
from datetime import datetime
from dotenv import load_dotenv

# IMPORTS LOCALES (funcionan con python3 main.py)
from normalizer import normalize_user_item, get_embedder
from models.genetic_optimizer import optimizar_compra
from llm.client import generate_explanation

# ====================== CONFIG ======================
MAX_SUPERMERCADOS_POR_DEFECTO = 5
PORCENTAJE_AHORRO_ESTIMADO = 0.38
ANCHO_LINEA = 90


class OptimizadorComprasGA:

    def __init__(self, max_supermercados: int = MAX_SUPERMERCADOS_POR_DEFECTO, usar_llm: bool = True):
        load_dotenv()
        self.max_supermercados = max_supermercados
        self.usar_llm = usar_llm
        # Precargamos el embedder una sola vez al inicializar
        self.embedder = get_embedder()

    # ---------------------------------------------------------
    # PARSEO DE ENTRADA
    # ---------------------------------------------------------

    @staticmethod
    def parse_quantity(text: str) -> Tuple[str, int]:
        text = text.strip()

        m = re.search(r'[xX×\*]\s*(\d+)', text)
        if m:
            return re.sub(r'[xX×\*]\s*\d+', '', text).strip(), int(m.group(1))

        m = re.search(r'(\d+)\s*(kg|kilos?|lt|litros?|l|ml|g|gr|unid|paq|unidades?)\b', text, re.IGNORECASE)
        if m:
            cantidad = int(m.group(1))
            nombre = re.sub(
                r'\d+\s*(kg|kilos?|lt|litros?|l|ml|g|gr|unid|paq|unidades?)\b',
                '',
                text,
                flags=re.IGNORECASE
            )
            return nombre.strip(), cantidad

        m = re.search(r'^(\d+)', text)
        if m:
            return text[len(m.group(1)):].strip(), int(m.group(1))

        return text, 1

    def procesar_entrada(self, entrada: str) -> List[Tuple[str, int]]:
        raw_items = [item.strip() for item in entrada.replace('\n', ',').split(',') if item.strip()]
        parsed = []
        for raw in raw_items:
            nombre_limpio, cantidad = self.parse_quantity(raw)
            if nombre_limpio:
                parsed.append((nombre_limpio, cantidad))
        return parsed

    # ---------------------------------------------------------
    # NORMALIZACIÓN CON EMBEDDINGS (OPTIMIZADA)
    # ---------------------------------------------------------

    def normalizar_y_consolidar(self, items_raw: List[Tuple[str, int]]) -> Dict[str, int]:
        print("Normalizando productos contra el dataset...\n")

        lista_consolidada = {}

        # Usamos el embedder precargado
        for texto_usuario, cantidad in items_raw:
            producto_dict, score = normalize_user_item(texto_usuario, embedder=self.embedder)
            nombre_normalizado = producto_dict.get("nombre", texto_usuario)

            lista_consolidada[nombre_normalizado] = (
                lista_consolidada.get(nombre_normalizado, 0) + cantidad
            )

            print(
                f"Input: {texto_usuario:<35} → "
                f"Match: {nombre_normalizado:<45} "
                f"(score={score:.3f}, cantidad={cantidad})"
            )

        print(f"\nProductos consolidados: {len(lista_consolidada)}\n")
        return lista_consolidada

    # ---------------------------------------------------------
    # OPTIMIZACIÓN GENÉTICA
    # ---------------------------------------------------------

    def optimizar_con_ga(self, lista_consolidada: Dict[str, int]) -> Dict[str, Any]:
        return optimizar_compra(lista_consolidada)

    # ---------------------------------------------------------
    # EXPLICACIÓN CON LLM
    # ---------------------------------------------------------

    def generar_explicacion_llm(self, resultado_ga: Dict[str, Any]) -> str:
        distribucion = resultado_ga.get("distribucion", {})
        total = resultado_ga.get("costo_total", 0.0)

        flattened = []
        for prod, asignaciones in distribucion.items():
            for a in asignaciones:
                flattened.append({
                    "producto": prod,
                    "supermercado": a.get("supermercado"),
                    "precio": a.get("subtotal") or a.get("precio") or 0,
                })

        if not flattened:
            return ""

        try:
            return generate_explanation(flattened, total)
        except Exception as e:
            print(f"[Aviso] Error generando explicación LLM: {e}")
            return ""

    # ---------------------------------------------------------
    # FORMATEO DE RESULTADOS
    # ---------------------------------------------------------

    @staticmethod
    def agrupar_por_supermercado(resultado_ga: Dict[str, Any]) -> Dict[str, List[Dict]]:
        grupos = defaultdict(list)
        for producto, asignaciones in resultado_ga.get("distribucion", {}).items():
            for a in asignaciones:
                grupos[a["supermercado"]].append({
                    "producto": producto,
                    "cantidad": a["cantidad"],
                    "precio_unitario": a["precio"],
                    "subtotal": a["subtotal"],
                })
        return dict(grupos)

    def mostrar_resultado(self, resultado_ga: Dict[str, Any], explanation: str) -> str:
        separador = "=" * ANCHO_LINEA
        costo_total = resultado_ga.get("costo_total", 0.0)
        grupos = self.agrupar_por_supermercado(resultado_ga)

        print(f"\n{separador}")
        print("LISTA DE COMPRAS OPTIMIZADA (GA)".center(ANCHO_LINEA))
        print(separador)

        fecha = datetime.now().strftime('%d/%m/%Y')
        texto_wsp = f"*LISTA OPTIMIZADA (GA) - {fecha}*\n"
        texto_wsp += f"*Total estimado: ${costo_total:,.0f}*\n\n"

        total_con_precio = 0

        for supermercado, items in sorted(grupos.items()):
            print(f"\n{supermercado.upper()}")
            texto_wsp += f"*{supermercado.upper()}*\n"

            subtotal = 0
            for item in items:
                pu = float(item["precio_unitario"])
                st = float(item["subtotal"])
                subtotal += st
                total_con_precio += st

                print(f"  • {item['producto']:<45} x{item['cantidad']}  ${pu:>6.0f} c/u   ${st:>8.0f}")
                texto_wsp += f"• {item['producto']} — x{item['cantidad']} (${pu:,.0f} c/u, subtotal ${st:,.0f})\n"

            texto_wsp += f"_Subtotal: ${subtotal:,.0f}_\n\n"

        ahorro = int(total_con_precio * PORCENTAJE_AHORRO_ESTIMADO)

        print(f"\nTOTAL ESTIMADO: ${total_con_precio:,.0f}")
        print(f"AHORRO ESTIMADO (~38%): ${ahorro:,.0f}")
        print(separador)

        texto_wsp += f"\n*TOTAL: ${total_con_precio:,.0f}*\n"
        texto_wsp += f"*Ahorro estimado (aprox.): ${ahorro:,.0f}*\n"

        if explanation:
            print("\nEXPLICACIÓN DEL LLM:\n")
            print(explanation)
            texto_wsp += "\n\n*Explicación de la optimización:*\n" + explanation

        return texto_wsp

    # ---------------------------------------------------------
    # PIPELINE PRINCIPAL
    # ---------------------------------------------------------

    def ejecutar(self, entrada: str) -> Dict[str, Any]:
        print("\n" + "=" * ANCHO_LINEA)
        print("PROCESANDO TU LISTA DE COMPRAS (GA + LLM)".center(ANCHO_LINEA))
        print("=" * ANCHO_LINEA + "\n")

        items_raw = self.procesar_entrada(entrada)
        print(f"{len(items_raw)} producto(s) detectado(s)\n")

        if not items_raw:
            print("No se detectaron productos.")
            return {}

        lista_consolidada = self.normalizar_y_consolidar(items_raw)

        if not lista_consolidada:
            print("No se pudo mapear ningún producto.")
            return {}

        resultado_ga = self.optimizar_con_ga(lista_consolidada)

        explanation = self.generar_explicacion_llm(resultado_ga) if self.usar_llm else ""

        texto_whatsapp = self.mostrar_resultado(resultado_ga, explanation)

        return {
            "total": resultado_ga.get("costo_total", 0.0),
            "texto_whatsapp": texto_whatsapp,
            "num_supermercados": len(self.agrupar_por_supermercado(resultado_ga)),
            "por_supermercado": self.agrupar_por_supermercado(resultado_ga),
            "explanation": explanation,
        }


# ---------------------------------------------------------
# EJECUCIÓN CLI
# ---------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print('Uso:')
        print('  python3 main.py "leche x3, yerba playadito 1kg, coca cola 2.25"')
        sys.exit(1)

    entrada = " ".join(sys.argv[1:])
    opt = OptimizadorComprasGA()
    resultado = opt.ejecutar(entrada)

    if not resultado:
        sys.exit(1)

    print("\n✅ Listo! Podés copiar esto a WhatsApp:\n")
    print(resultado["texto_whatsapp"])


if __name__ == "__main__":
    main()