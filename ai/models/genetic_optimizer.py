# models/genetic_optimizer.py
import numpy as np
import pandas as pd
from typing import Dict
import random
from pathlib import Path

# RUTA FIJA AL DATASET (está en la raíz del proyecto)
BASE_DIR = Path(__file__).resolve().parent.parent  # sube dos niveles desde models/
DATASET_PATH = BASE_DIR / "dataset_10000_productos_arg_5_super.csv"

# Cargamos el dataset una sola vez al importar el módulo (más rápido)
print("Cargando dataset de precios...")
df_precios = pd.read_csv(DATASET_PATH)
print(f"Dataset cargado: {len(df_precios)} productos disponibles en 5 supermercados.\n")

class SupermarketGAOptimizer:
    def __init__(
        self,
        shopping_list: Dict[str, int],
        population_size: int = 100,
        n_generations: int = 200,
        mutation_rate: float = 0.15,
        elite_size: int = 10,
        early_stopping: int = 30
    ):
        total_productos = len(shopping_list)
        total_unidades = sum(shopping_list.values())

        print("\n" + "="*65)
        print("       OPTIMIZADOR GENÉTICO DE SUPERMERCADOS")
        print("="*65)
        print(f"   Productos solicitados           : {total_productos}")
        print(f"   Unidades totales a comprar      : {total_unidades}")
        print("-"*65)

        # Filtrar productos que realmente existen
        productos_validos = [p for p in shopping_list if p in df_precios['nombre'].values]
        no_encontrados = total_productos - len(productos_validos)

        if no_encontrados > 0:
            print(f"   Advertencia: {no_encontrados} producto(s) no encontrado(s) → se ignoran")

        if not productos_validos:
            raise ValueError("Ningún producto de tu lista está en el dataset.")

        self.shopping_list = {p: shopping_list[p] for p in productos_validos}
        self.products = productos_validos
        self.quantities = np.array([self.shopping_list[p] for p in self.products])

        # Supermercados
        self.supermarkets = ['Carrefour', 'Coto', 'Dia', 'Jumbo', 'Changomas']
        self.n_supers = 5

        # Matriz de precios (productos × supermercados)
        # === CORRECCIÓN CLAVE: tomamos el precio MÁS BARATO de cada producto en cada súper ===
        price_cols = ['precio_carrefour', 'precio_coto', 'precio_dia', 'precio_jumbo', 'precio_changomas']
        
        # Agrupamos por nombre y nos quedamos con el precio mínimo de cada supermercado
        df_minimos = (
            df_precios.groupby('nombre')[price_cols]
            .min()
            .reindex(self.products)  # orden exacto de tu lista
            .fillna(999999)          # si algún súper nunca tuvo ese producto
        )
        
        self.price_matrix = df_minimos.values  # ahora SÍ es (n_productos × 5)
        # =====================================================================

        # Supermercados
        self.supermarkets = ['Carrefour', 'Coto', 'Día', 'Jumbo', 'Changomas']
        self.n_supers = 5

        # Parámetros GA (sin cambios)
        self.population_size = population_size
        self.n_generations = n_generations
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size
        self.early_stopping = early_stopping

        self.best_cost = float('inf')
        self.best_solution = None
        self.history = []

        print(f"   Productos que se optimizarán    : {len(self.products)}")
        print(f"   Unidades a optimizar            : {sum(self.quantities)}")
        print("="*65 + "\n")

    def _create_individual(self):
        ind = np.zeros((len(self.products), self.n_supers), dtype=int)
        for i, qty in enumerate(self.quantities):
            if qty > 0:
                ind[i] = np.random.multinomial(qty, [1/self.n_supers] * self.n_supers)
        return ind

    def _fitness(self, ind):
        cost = np.sum(ind * self.price_matrix)
        faltantes = np.sum(np.maximum(0, self.quantities - np.sum(ind, axis=1)))
        return cost + faltantes * 1_000_000

    def _crossover(self, p1, p2):
        c1, c2 = p1.copy(), p2.copy()
        for i in range(len(self.products)):
            if random.random() < 0.5:
                c1[i], c2[i] = p2[i].copy(), p1[i].copy()
        return c1, c2

    def _mutate(self, ind):
        for i in range(len(self.products)):
            if random.random() < self.mutation_rate and self.quantities[i] > 0:
                ind[i] = np.random.multinomial(self.quantities[i], [1/self.n_supers] * self.n_supers)
        return ind

    def optimize(self) -> Dict:
        population = [self._create_individual() for _ in range(self.population_size)]
        stagnant = 0

        for gen in range(self.n_generations):
            fitnesses = [self._fitness(ind) for ind in population]
            best_now = min(fitnesses)

            if best_now < self.best_cost:
                self.best_cost = best_now
                self.best_solution = population[np.argmin(fitnesses)].copy()
                stagnant = 0
                print(f"   Gen {gen+1:3d} → Mejor precio: ${best_now:,.2f}")
            else:
                stagnant += 1

            if stagnant >= self.early_stopping:
                print(f"\n   Early stopping en generación {gen+1}")
                break

            # Elite + nueva población
            elite = [population[i].copy() for i in np.argsort(fitnesses)[:self.elite_size]]
            new_pop = elite[:]

            while len(new_pop) < self.population_size:
                p1 = random.choices(population, weights=[1/f for f in fitnesses], k=1)[0]
                p2 = random.choices(population, weights=[1/f for f in fitnesses], k=1)[0]
                c1, c2 = self._crossover(p1, p2)
                new_pop.extend([self._mutate(c1), self._mutate(c2)])

            population = new_pop[:self.population_size]

        print(f"\n   OPTIMIZACIÓN FINALIZADA")
        print(f"   COSTO MÍNIMO ENCONTRADO: ${self.best_cost:,.2f}\n")
        return self._build_result()

    def _build_result(self) -> Dict:
        result = {
            "costo_total": round(float(self.best_cost), 2),
            "productos_optimizados": len(self.products),
            "unidades_totales": int(np.sum(self.quantities)),
            "ahorro_vs_peor_supermercado": 0.0,  # lo calculamos después si querés
            "distribucion": {},
            "total_por_supermercado": {s: 0.0 for s in self.supermarkets}
        }

        for i, prod in enumerate(self.products):
            for j, cant in enumerate(self.best_solution[i]):
                if cant > 0:
                    super = self.supermarkets[j]
                    precio = self.price_matrix[i][j]
                    subtotal = cant * precio
                    result["distribucion"].setdefault(prod, []).append({
                        "supermercado": super,
                        "cantidad": int(cant),
                        "precio": float(precio),
                        "subtotal": round(float(subtotal), 2)
                    })
                    result["total_por_supermercado"][super] += subtotal

        return result


# FUNCIÓN MÁS FÁCIL DE USAR
def optimizar_compra(lista_compra: Dict[str, int]) -> Dict:
    """
    La función que vas a llamar desde cualquier lado.
    
    Ejemplo:
        mi_lista = {
            "Arroz Gallo 1kg": 2,
            "Leche La Serenísima 1L": 3,
            "Aceite Natura 900ml": 1
        }
        resultado = optimizar_compra(mi_lista)
    """
    optimizer = SupermarketGAOptimizer(lista_compra)
    return optimizer.optimize()