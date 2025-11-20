import random
import numpy as np
from deap import base, creator, tools, algorithms
import pandas as pd
from collections import Counter

SUPERS = ["Carrefour", "Coto", "Día", "Jumbo", "Changomas"]
PRECIOS_COLS = ["precio_carrefour", "precio_coto", "precio_dia", "precio_jumbo", "precio_changomas"]

def optimize_shopping_list(normalized_products, max_supers=5):
    n_products = len(normalized_products)
    n_supers = 5

    creator.create("FitnessMin", base.Fitness, weights=(-1.0, -0.001))  # costo + penalización por muchos supers
    creator.create("Individual", list, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()
    toolbox.register("attr_super", random.randint, 0, n_supers-1)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_super, n=n_products)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    def eval_cost(individual):
        total = 0.0
        supers_used = len(set(individual))
        penalty = 0 if supers_used <= max_supers else (supers_used - max_supers) * 5000  # fuerte penalización
        for i, super_idx in enumerate(individual):
            price = normalized_products[i][PRECIOS_COLS[super_idx]]
            if pd.isna(price) or price <= 0:
                valid = [normalized_products[i][c] for c in PRECIOS_COLS if pd.notna(normalized_products[i][c]) and normalized_products[i][c] > 0]
                price = np.mean(valid) if valid else 1000
            total += price
        return (total + penalty, supers_used)

    toolbox.register("evaluate", eval_cost)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutUniformInt, low=0, up=n_supers-1, indpb=0.25)
    toolbox.register("select", tools.selTournament, tournsize=5)

    pop = toolbox.population(n=400)
    hof = tools.HallOfFame(1)
    algorithms.eaSimple(pop, toolbox, cxpb=0.8, mutpb=0.3, ngen=120, halloffame=hof, verbose=False)

    best = hof[0]
    total = eval_cost(best)[0]

    result = []
    for i, super_idx in enumerate(best):
        result.append({
            "producto": normalized_products[i]["nombre"],
            "supermercado": SUPERS[super_idx],
            "precio": normalized_products[i][PRECIOS_COLS[super_idx]] if not pd.isna(normalized_products[i][PRECIOS_COLS[super_idx]]) else 0
        })

    return sorted(result, key=lambda x: x["supermercado"]), round(total, 2)
