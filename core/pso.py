"""
pso.py
Algoritmo de Optimización por Enjambre de Partículas (PSO) para el Sistema de Reparto de Amazon.
Resuelve el Vehicle Routing / TSP mediante Claves Aleatorias (Random-Key) y control dinámico de hiperparámetros.
"""

import time
import numpy as np

def run_pso_optimizer(
    dist_matrix,
    time_matrix=None,
    n_particles=30,
    n_iter=100,
    w=0.72,
    c1=1.49,
    c2=1.49,
    vmax=4.0,
    objective="distance",  # "distance" o "time"
    seed=None
):
    """
    Ejecuta el algoritmo PSO continuo con decodificación de claves aleatorias para TSP.
    """
    if seed is not None:
        np.random.seed(seed)
        
    start_time = time.time()
    
    cost_matrix = np.array(time_matrix if objective == "time" and time_matrix is not None else dist_matrix)
    n = len(cost_matrix)
    dim = n - 1  # El Hub 0 es el inicio y fin fijo
    
    # Inicialización de partículas en R^dim
    X = np.random.uniform(-10.0, 10.0, (n_particles, dim))
    V = np.random.uniform(-vmax, vmax, (n_particles, dim))
    
    pbest_X = X.copy()
    pbest_costs = np.full(n_particles, float('inf'))
    
    gbest_cost = float('inf')
    gbest_X = None
    gbest_route = None
    
    convergence_history = []
    
    def decode_permutation(x_vec):
        """Mapea vector continuo de prioridades a permutación discreta [0] + orden."""
        order = np.argsort(x_vec) + 1
        return [0] + [int(idx) for idx in order]
        
    def calculate_cost(route):
        c = 0.0
        for i in range(len(route)):
            c += cost_matrix[route[i], route[(i + 1) % len(route)]]
        return c

    # Evaluación inicial
    for i in range(n_particles):
        route = decode_permutation(X[i])
        cost = calculate_cost(route)
        pbest_costs[i] = cost
        if cost < gbest_cost:
            gbest_cost = cost
            gbest_X = X[i].copy()
            gbest_route = list(route)
            
    convergence_history.append(round(float(gbest_cost), 2))
    
    # Bucle de iteraciones de PSO
    for it in range(n_iter):
        for i in range(n_particles):
            r1 = np.random.rand(dim)
            r2 = np.random.rand(dim)
            
            # Ecuación de actualización de velocidad
            V[i] = w * V[i] + c1 * r1 * (pbest_X[i] - X[i]) + c2 * r2 * (gbest_X - X[i])
            V[i] = np.clip(V[i], -vmax, vmax)
            
            # Ecuación de actualización de posición
            X[i] = np.clip(X[i] + V[i], -10.0, 10.0)
            
            route = decode_permutation(X[i])
            cost = calculate_cost(route)
            
            # Actualización de mejor personal (pbest)
            if cost < pbest_costs[i]:
                pbest_costs[i] = cost
                pbest_X[i] = X[i].copy()
                
                # Actualización de mejor global (gbest)
                if cost < gbest_cost:
                    gbest_cost = cost
                    gbest_X = X[i].copy()
                    gbest_route = list(route)
                    
        convergence_history.append(round(float(gbest_cost), 2))

    elapsed_ms = round((time.time() - start_time) * 1000, 2)
    
    total_dist = sum(dist_matrix[gbest_route[i]][gbest_route[(i + 1) % n]] for i in range(n))
    total_time = sum(time_matrix[gbest_route[i]][gbest_route[(i + 1) % n]] for i in range(n)) if time_matrix else (total_dist / 45.0) * 60.0
    
    closed_route = [int(idx) for idx in gbest_route] + [0]
    
    return {
        "algorithm": "PSO (Particle Swarm Optimization)",
        "route_indices": closed_route,
        "best_cost": round(float(gbest_cost), 2),
        "total_distance_km": round(float(total_dist), 2),
        "total_duration_min": round(float(total_time), 1),
        "execution_time_ms": elapsed_ms,
        "convergence": [float(x) for x in convergence_history],
        "iterations": int(n_iter),
        "particles": int(n_particles),
        "hyperparameters": {
            "w": float(w),
            "c1": float(c1),
            "c2": float(c2),
            "vmax": float(vmax)
        }
    }
