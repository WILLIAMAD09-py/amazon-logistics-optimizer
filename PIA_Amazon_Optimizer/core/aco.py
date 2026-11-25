"""
aco.py
Algoritmo de Optimización por Colonias de Hormigas (ACO) para el Sistema de Reparto de Amazon.
Resuelve el Vehicle Routing / TSP con control dinámico total de hiperparámetros.
"""

import time
import numpy as np

def run_aco_optimizer(
    dist_matrix,
    time_matrix=None,
    n_ants=20,
    n_iter=100,
    alpha=1.0,
    beta=2.0,
    rho=0.1,
    Q=100.0,
    elitism=3,
    objective="distance",  # "distance" o "time"
    seed=None
):
    """
    Ejecuta el algoritmo ACO sobre la matriz de costos.
    objective: "distance" utiliza dist_matrix; "time" utiliza time_matrix.
    """
    if seed is not None:
        np.random.seed(seed)
        
    start_time = time.time()
    
    # Matriz de costo según el objetivo
    cost_matrix = np.array(time_matrix if objective == "time" and time_matrix is not None else dist_matrix)
    n = len(cost_matrix)
    
    # Matriz heurística (visibilidad inversa)
    with np.errstate(divide='ignore'):
        eta = 1.0 / np.where(cost_matrix == 0, np.inf, cost_matrix)
        
    # Inicialización de feromonas uniforme
    tau = np.ones((n, n)) * 1.0
    
    best_cost = float('inf')
    best_route = None
    convergence_history = []
    
    def calculate_cost(route):
        c = 0.0
        for i in range(len(route)):
            c += cost_matrix[route[i], route[(i + 1) % len(route)]]
        return c

    for it in range(n_iter):
        routes = []
        costs = []
        
        for ant in range(n_ants):
            route = [0]  # El Hub de Amazon es el origen fijo
            unvisited = set(range(1, n))
            curr = 0
            
            while unvisited:
                unv_list = list(unvisited)
                # Regla de transición probabilística
                probs = (tau[curr, unv_list] ** alpha) * (eta[curr, unv_list] ** beta)
                sum_p = probs.sum()
                if sum_p == 0 or np.isnan(sum_p):
                    probs = np.ones(len(unv_list)) / len(unv_list)
                else:
                    probs = probs / sum_p
                
                next_node = np.random.choice(unv_list, p=probs)
                route.append(next_node)
                unvisited.remove(next_node)
                curr = next_node
                
            routes.append(route)
            c = calculate_cost(route)
            costs.append(c)
            
            if c < best_cost:
                best_cost = c
                best_route = list(route)
                
        convergence_history.append(round(float(best_cost), 2))
        
        # Evaporación de feromonas
        tau = (1.0 - rho) * tau
        
        # Depósito de feromonas por todas las hormigas
        for r, c in zip(routes, costs):
            dep = Q / c if c > 0 else 0
            for i in range(n):
                u, v = r[i], r[(i + 1) % n]
                tau[u, v] += dep
                tau[v, u] += dep
                
        # Refuerzo elitista a la mejor ruta global
        if elitism > 0 and best_route is not None:
            dep_e = elitism * (Q / best_cost)
            for i in range(n):
                u, v = best_route[i], best_route[(i + 1) % n]
                tau[u, v] += dep_e
                tau[v, u] += dep_e

    elapsed_ms = round((time.time() - start_time) * 1000, 2)
    
    # Calcular métricas finales de distancia y tiempo
    total_dist = sum(dist_matrix[best_route[i]][best_route[(i + 1) % n]] for i in range(n))
    total_time = sum(time_matrix[best_route[i]][best_route[(i + 1) % n]] for i in range(n)) if time_matrix else (total_dist / 45.0) * 60.0
    
    # Cerrar la ruta visual para Leaflet (retorno a Hub) con tipos int nativos de Python
    closed_route = [int(idx) for idx in best_route] + [0]
    
    return {
        "algorithm": "ACO (Ant Colony Optimization)",
        "route_indices": closed_route,
        "best_cost": round(float(best_cost), 2),
        "total_distance_km": round(float(total_dist), 2),
        "total_duration_min": round(float(total_time), 1),
        "execution_time_ms": elapsed_ms,
        "convergence": [float(x) for x in convergence_history],
        "iterations": int(n_iter),
        "ants": int(n_ants),
        "hyperparameters": {
            "alpha": float(alpha),
            "beta": float(beta),
            "rho": float(rho),
            "Q": float(Q),
            "elitism": int(elitism)
        }
    }
