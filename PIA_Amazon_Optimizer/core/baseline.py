"""
baseline.py
Algoritmo voraz de referencia (Vecino Más Cercano) para entregas de Amazon.
"""

def run_nearest_neighbor(dist_matrix, time_matrix=None):
    n = len(dist_matrix)
    unvisited = set(range(1, n))
    curr = 0
    route = [0]
    
    while unvisited:
        next_node = min(unvisited, key=lambda x: dist_matrix[curr][x])
        route.append(next_node)
        unvisited.remove(next_node)
        curr = next_node
        
    total_dist = sum(dist_matrix[route[i]][route[(i + 1) % n]] for i in range(n))
    total_time = sum(time_matrix[route[i]][route[(i + 1) % n]] for i in range(n)) if time_matrix else (total_dist / 40.0) * 60.0
    
    return {
        "algorithm": "Vecino Más Cercano (Línea Base Ingenua)",
        "route_indices": [int(x) for x in route] + [0],
        "total_distance_km": round(float(total_dist), 2),
        "total_duration_min": round(float(total_time), 1)
    }
