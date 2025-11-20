import random
import numpy as np
from deap import base, creator, tools, algorithms

SUPERS = ["Carrefour", "Coto", "Día", "Jumbo", "Changomas"]
PRECIOS_COLS = ["precio_carrefour", "precio_coto", "precio_dia", "precio_jumbo", "precio_changomas"]

def optimize_shopping_list(normalized_products):
    n_products = len(normalized_products)
    n_supers = len(SUPERS)

    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()
    toolbox.register("supermercado", random.randint, 0, n_supers-1)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.supermercado, n=n_products)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    def eval_cost(individual):
        total = 0
        for i, super_idx in enumerate(individual):
            precio = normalized_products[i][PRECIOS_COLS[super_idx]]
            if pd.isna(precio):
                precio = np.nanmean([normalized_products[i][col] for col in PRECIOS_COLS if not pd.isna(normalized_products[i][col])])
            total += precio
        return (total,)

    toolbox.register("evaluate", eval_cost)
    toolbox.register("mate", tools.cxUniform, indpb=0.5)
    toolbox.register("mutate", tools.mutUniformInt, low=0, up=n_supers-1, indpb=0.2)
    toolbox.register("select", tools.selTournament, tournsize=3)

    pop = toolbox.population(n=300)
    hof = tools.HallOfFame(1)
    algorithms.eaSimple(pop, toolbox, cxpb=0.7, mutpb=0.3, ngen=100, halloffame=hof, verbose=False)

    best = hof[0]
    assignment = [SUPERS[i] for i in best]
    total_cost = eval_cost(best)[0]
    
    result = []
    for i, super_name in enumerate(assignment):
        result.append({
            "producto": normalized_products[i]["nombre"],
            "supermercado": super_name,
            "precio": normalized_products[i][PRECIOS_COLS[SUPERS.index(super_name)]]
        })
    
    return result, total_cost