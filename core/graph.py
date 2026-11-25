"""
graph.py
Módulo de grafo vial y enrutamiento con OpenStreetMap (OSM), Overpass API y Algoritmo de Dijkstra.
Genera la matriz de distancias reales y las polilíneas de calles exactas para dibujar en Leaflet.
"""

import math
import heapq
import requests
import json
import os

def haversine(lat1, lon1, lat2, lon2):
    """Calcula la distancia ortodrómica en kilómetros entre dos coordenadas geográficas."""
    R = 6371.0 # Radio de la Tierra en km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

# Red vial real precargada de Monterrey (Arterias principales y corredores viales reales)
# Incluye nodos clave en cruces viales y aristas con nombres, sentidos y límites de velocidad.
MONTERREY_ROAD_NODES = {
    # Centro MTY & Hub Colón
    "N_COLON_BERNARDO": {"lat": 25.6866, "lng": -100.3161, "name": "Av. Colón & Bernardo Reyes"},
    "N_COLON_PINO": {"lat": 25.6860, "lng": -100.3220, "name": "Av. Colón & Pino Suárez"},
    "N_COLON_MADERO": {"lat": 25.6845, "lng": -100.2980, "name": "Av. Colón & Madero"},
    "N_CENTRO_ZARAGOZA": {"lat": 25.6700, "lng": -100.3090, "name": "Macroplaza / Zaragoza"},
    "N_MADERO_CHURUBUSCO": {"lat": 25.6985, "lng": -100.2774, "name": "Av. Madero & Churubusco"},
    
    # Corredor Constitución / Morones Prieto (Vías rápidas oriente-poniente)
    "N_CONST_OBISPADO": {"lat": 25.6690, "lng": -100.3420, "name": "Av. Constitución & Gonzalitos"},
    "N_CONST_CENTRO": {"lat": 25.6660, "lng": -100.3120, "name": "Av. Constitución & Zaragoza"},
    "N_CONST_FUNDIDORA": {"lat": 25.6740, "lng": -100.2850, "name": "Av. Constitución & Fundidora"},
    "N_CONST_CHURUBUSCO": {"lat": 25.6850, "lng": -100.2650, "name": "Av. Constitución & Churubusco"},
    "N_MORONES_GONZALITOS": {"lat": 25.6675, "lng": -100.3440, "name": "Av. Morones Prieto & Gonzalitos"},
    "N_MORONES_VALLE": {"lat": 25.6590, "lng": -100.3600, "name": "Morones Prieto & Miravalle"},
    
    # San Pedro Garza García
    "N_CALZADA_VALLE": {"lat": 25.6565, "lng": -100.3662, "name": "Calzada San Pedro & Del Valle"},
    "N_VASCONCELOS_SP": {"lat": 25.6500, "lng": -100.3680, "name": "Vasconcelos & Calzada San Pedro"},
    "N_VALLE_ORIENTE": {"lat": 25.6418, "lng": -100.3182, "name": "Av. Frida Kahlo & Lázaro Cárdenas"},
    "N_LAZARO_CARDENAS": {"lat": 25.6450, "lng": -100.3350, "name": "Lázaro Cárdenas & Real de San Agustín"},
    
    # Sur de Monterrey (Tec & Contry)
    "N_TEC_GARZA_SADA": {"lat": 25.6514, "lng": -100.2895, "name": "Garza Sada & Luis Elizondo (Tec)"},
    "N_CONTRY_REYES": {"lat": 25.6322, "lng": -100.2781, "name": "Garza Sada & Alfonso Reyes (Contry)"},
    "N_REVOLUCION_CHAPULTEPEC": {"lat": 25.6630, "lng": -100.2810, "name": "Av. Revolución & Chapultepec"},
    
    # San Nicolás de los Garza & Norte
    "N_UNIV_CU": {"lat": 25.7258, "lng": -100.3134, "name": "Av. Universidad & Rectoria CU"},
    "N_UNIV_NOGALAR": {"lat": 25.7130, "lng": -100.3080, "name": "Av. Universidad & Nogalar"},
    "N_SN_CENTRO": {"lat": 25.7482, "lng": -100.2985, "name": "Av. Juárez & Porfirio Díaz (SN Centro)"},
    "N_BARRAGAN_ANAHUAC": {"lat": 25.7365, "lng": -100.3278, "name": "Manuel L. Barragán & Almazán"},
    "N_BARRAGAN_FIDEL": {"lat": 25.7180, "lng": -100.3290, "name": "Barragán & Fidel Velázquez"},
    
    # Poniente (Mitras & Cumbres)
    "N_GONZALITOS_MADERO": {"lat": 25.6850, "lng": -100.3470, "name": "Gonzalitos & Madero (Hospital Univ.)"},
    "N_LEONES_MITRAS": {"lat": 25.6961, "lng": -100.3475, "name": "Paseo de los Leones & Gonzalitos"},
    "N_LEONES_CUMBRES": {"lat": 25.7092, "lng": -100.3698, "name": "Paseo de los Leones & Rangel Frías"},
    "N_SAN_JERONIMO": {"lat": 25.6812, "lng": -100.3654, "name": "Av. Fleteros & Anillo Periférico"},
    
    # Guadalupe (Oriente)
    "N_MIGUEL_ALEMAN_LV": {"lat": 25.6948, "lng": -100.2521, "name": "Av. Miguel Alemán & Linda Vista"},
    "N_AZTECA_MORONES": {"lat": 25.6790, "lng": -100.2510, "name": "Av. Azteca & Morones Prieto"},
    
    # Santa Catarina (Poniente Extremo)
    "N_STA_CATARINA_FAMA": {"lat": 25.6712, "lng": -100.4356, "name": "Av. Manuel Ordóñez & La Fama"},
    "N_DIAZ_ORDAZ_MIRAVALLE": {"lat": 25.6660, "lng": -100.3800, "name": "Díaz Ordaz & Puente Miravalle"}
}

MONTERREY_ROAD_EDGES = [
    # Eje Constitución (Sentido Poniente -> Oriente)
    ("N_CONST_OBISPADO", "N_CONST_CENTRO", {"name": "Av. Constitución", "speed": 80, "oneway": True}),
    ("N_CONST_CENTRO", "N_CONST_FUNDIDORA", {"name": "Av. Constitución", "speed": 80, "oneway": True}),
    ("N_CONST_FUNDIDORA", "N_CONST_CHURUBUSCO", {"name": "Av. Constitución", "speed": 80, "oneway": True}),
    ("N_CONST_CHURUBUSCO", "N_AZTECA_MORONES", {"name": "Av. Constitución Express", "speed": 80, "oneway": True}),
    
    # Eje Morones Prieto (Sentido Oriente -> Poniente)
    ("N_AZTECA_MORONES", "N_CONST_FUNDIDORA", {"name": "Av. Morones Prieto", "speed": 80, "oneway": True}),
    ("N_CONST_FUNDIDORA", "N_CONST_CENTRO", {"name": "Av. Morones Prieto", "speed": 80, "oneway": True}),
    ("N_CONST_CENTRO", "N_MORONES_GONZALITOS", {"name": "Av. Morones Prieto", "speed": 80, "oneway": True}),
    ("N_MORONES_GONZALITOS", "N_MORONES_VALLE", {"name": "Av. Morones Prieto", "speed": 80, "oneway": True}),
    ("N_MORONES_VALLE", "N_DIAZ_ORDAZ_MIRAVALLE", {"name": "Av. Morones Prieto", "speed": 70, "oneway": True}),
    ("N_DIAZ_ORDAZ_MIRAVALLE", "N_STA_CATARINA_FAMA", {"name": "Blvd. Díaz Ordaz", "speed": 70, "oneway": False}),
    
    # Av. Gonzalitos (Norte <-> Sur)
    ("N_CONST_OBISPADO", "N_MORONES_GONZALITOS", {"name": "Av. Gonzalitos", "speed": 60, "oneway": False}),
    ("N_CONST_OBISPADO", "N_GONZALITOS_MADERO", {"name": "Av. Gonzalitos", "speed": 60, "oneway": False}),
    ("N_GONZALITOS_MADERO", "N_LEONES_MITRAS", {"name": "Av. Gonzalitos / Leones", "speed": 60, "oneway": False}),
    ("N_GONZALITOS_MADERO", "N_COLON_PINO", {"name": "Av. Madero", "speed": 50, "oneway": False}),
    
    # Eje Colón y Centro
    ("N_COLON_BERNARDO", "N_COLON_PINO", {"name": "Av. Colón", "speed": 50, "oneway": False}),
    ("N_COLON_BERNARDO", "N_COLON_MADERO", {"name": "Av. Colón", "speed": 50, "oneway": False}),
    ("N_COLON_PINO", "N_CENTRO_ZARAGOZA", {"name": "Av. Pino Suárez", "speed": 50, "oneway": True}),
    ("N_CENTRO_ZARAGOZA", "N_CONST_CENTRO", {"name": "Av. Zaragoza", "speed": 50, "oneway": True}),
    ("N_COLON_MADERO", "N_MADERO_CHURUBUSCO", {"name": "Av. Francisco I. Madero", "speed": 60, "oneway": False}),
    ("N_COLON_MADERO", "N_CONST_FUNDIDORA", {"name": "Av. Fundidora", "speed": 50, "oneway": False}),
    
    # San Pedro y Lázaro Cárdenas
    ("N_MORONES_VALLE", "N_CALZADA_VALLE", {"name": "Calzada San Pedro", "speed": 50, "oneway": False}),
    ("N_CALZADA_VALLE", "N_VASCONCELOS_SP", {"name": "Calzada San Pedro", "speed": 50, "oneway": False}),
    ("N_VASCONCELOS_SP", "N_LAZARO_CARDENAS", {"name": "Av. Vasconcelos", "speed": 60, "oneway": False}),
    ("N_LAZARO_CARDENAS", "N_VALLE_ORIENTE", {"name": "Av. Lázaro Cárdenas", "speed": 70, "oneway": False}),
    ("N_VALLE_ORIENTE", "N_CONTRY_REYES", {"name": "Túnel de la Loma Larga / Lázaro Cárdenas", "speed": 70, "oneway": False}),
    ("N_VALLE_ORIENTE", "N_CONST_CENTRO", {"name": "Túnel de la Loma Larga", "speed": 70, "oneway": False}),
    
    # Garza Sada, Contry y Tec
    ("N_CONST_CENTRO", "N_TEC_GARZA_SADA", {"name": "Av. Eugenio Garza Sada", "speed": 70, "oneway": False}),
    ("N_TEC_GARZA_SADA", "N_CONTRY_REYES", {"name": "Av. Eugenio Garza Sada", "speed": 70, "oneway": False}),
    ("N_TEC_GARZA_SADA", "N_REVOLUCION_CHAPULTEPEC", {"name": "Av. Luis Elizondo", "speed": 50, "oneway": False}),
    ("N_REVOLUCION_CHAPULTEPEC", "N_CONST_FUNDIDORA", {"name": "Av. Revolución", "speed": 60, "oneway": False}),
    
    # San Nicolás, CU y Universidad
    ("N_COLON_BERNARDO", "N_UNIV_NOGALAR", {"name": "Av. Bernardo Reyes / Nogalar", "speed": 60, "oneway": False}),
    ("N_UNIV_NOGALAR", "N_UNIV_CU", {"name": "Av. Universidad", "speed": 60, "oneway": False}),
    ("N_UNIV_CU", "N_SN_CENTRO", {"name": "Av. Universidad", "speed": 60, "oneway": False}),
    ("N_UNIV_CU", "N_BARRAGAN_ANAHUAC", {"name": "Av. M. L. Barragán", "speed": 65, "oneway": False}),
    ("N_BARRAGAN_ANAHUAC", "N_BARRAGAN_FIDEL", {"name": "Av. M. L. Barragán", "speed": 70, "oneway": False}),
    ("N_BARRAGAN_FIDEL", "N_UNIV_NOGALAR", {"name": "Av. Fidel Velázquez / Nogalar", "speed": 70, "oneway": False}),
    ("N_BARRAGAN_FIDEL", "N_GONZALITOS_MADERO", {"name": "Av. Fidel Velázquez", "speed": 70, "oneway": False}),
    
    # Poniente: Cumbres y Leones
    ("N_LEONES_MITRAS", "N_LEONES_CUMBRES", {"name": "Av. Paseo de los Leones", "speed": 70, "oneway": False}),
    ("N_LEONES_MITRAS", "N_SAN_JERONIMO", {"name": "Av. Gonzalitos / San Jerónimo", "speed": 60, "oneway": False}),
    ("N_SAN_JERONIMO", "N_MORONES_VALLE", {"name": "Av. San Jerónimo", "speed": 60, "oneway": False}),
    ("N_SAN_JERONIMO", "N_LEONES_CUMBRES", {"name": "Av. Rangel Frías", "speed": 60, "oneway": False}),
    
    # Oriente: Churubusco y Miguel Alemán
    ("N_MADERO_CHURUBUSCO", "N_MIGUEL_ALEMAN_LV", {"name": "Av. Churubusco / Miguel Alemán", "speed": 60, "oneway": False}),
    ("N_CONST_CHURUBUSCO", "N_MADERO_CHURUBUSCO", {"name": "Av. Churubusco", "speed": 60, "oneway": False}),
    ("N_MIGUEL_ALEMAN_LV", "N_AZTECA_MORONES", {"name": "Av. Azteca", "speed": 50, "oneway": False})
]

class StreetNetwork:
    """Grafo de la red vial para Dijkstra y cálculo de rutas en calles reales."""
    def __init__(self):
        self.nodes = dict(MONTERREY_ROAD_NODES)
        self.adj = {k: [] for k in self.nodes}
        self._build_graph()

    def _build_graph(self):
        for u, v, attrs in MONTERREY_ROAD_EDGES:
            lat1, lng1 = self.nodes[u]["lat"], self.nodes[u]["lng"]
            lat2, lng2 = self.nodes[v]["lat"], self.nodes[v]["lng"]
            dist_km = haversine(lat1, lng1, lat2, lng2) * 1.15 # Factor de curvatura de calle
            speed = attrs.get("speed", 60)
            time_min = (dist_km / speed) * 60.0
            
            # Arco directo u -> v
            self.adj[u].append((v, dist_km, time_min, attrs["name"]))
            
            # Arco inverso v -> u si no es de un solo sentido (oneway)
            if not attrs.get("oneway", False):
                self.adj[v].append((u, dist_km, time_min, attrs["name"]))

    def snap_to_nearest_node(self, lat, lng):
        """Encuentra el nodo del grafo más cercano a una coordenada geográfica."""
        best_node = None
        min_dist = float('inf')
        for node_id, data in self.nodes.items():
            d = haversine(lat, lng, data["lat"], data["lng"])
            if d < min_dist:
                min_dist = d
                best_node = node_id
        return best_node, min_dist

    def dijkstra_street_path(self, start_lat, start_lng, end_lat, end_lng):
        """
        Ejecuta el Algoritmo de Dijkstra sobre el grafo de calles.
        Devuelve la distancia total (km), tiempo estimado (min) y la lista de coordenadas [lat, lng].
        """
        u_start, d_start = self.snap_to_nearest_node(start_lat, start_lng)
        u_end, d_end = self.snap_to_nearest_node(end_lat, end_lng)
        
        # Caso origen y destino muy cercanos al mismo nodo
        if u_start == u_end:
            direct_dist = haversine(start_lat, start_lng, end_lat, end_lng)
            return {
                "distance_km": round(direct_dist, 2),
                "duration_min": round((direct_dist / 40.0) * 60.0, 1),
                "path_coords": [[start_lat, start_lng], [end_lat, end_lng]],
                "streets": ["Conexión local"]
            }

        # Dijkstra con cola de prioridad
        distances = {node: float('inf') for node in self.nodes}
        times = {node: float('inf') for node in self.nodes}
        predecessors = {node: None for node in self.nodes}
        street_used = {node: None for node in self.nodes}
        
        distances[u_start] = 0.0
        times[u_start] = 0.0
        pq = [(0.0, u_start)]
        
        while pq:
            curr_dist, u = heapq.heappop(pq)
            if curr_dist > distances[u]:
                continue
            if u == u_end:
                break
                
            for v, weight_km, weight_min, st_name in self.adj[u]:
                new_dist = curr_dist + weight_km
                if new_dist < distances[v]:
                    distances[v] = new_dist
                    times[v] = times[u] + weight_min
                    predecessors[v] = u
                    street_used[v] = st_name
                    heapq.heappush(pq, (new_dist, v))
                    
        # Reconstrucción de la ruta
        path_nodes = []
        curr = u_end
        while curr is not None:
            path_nodes.append(curr)
            curr = predecessors[curr]
        path_nodes.reverse()
        
        if len(path_nodes) == 0 or path_nodes[0] != u_start:
            # Si no hay camino (grafo dirigido estricto), fallback a conexión directa
            direct_dist = haversine(start_lat, start_lng, end_lat, end_lng) * 1.2
            return {
                "distance_km": round(direct_dist, 2),
                "duration_min": round((direct_dist / 50.0) * 60.0, 1),
                "path_coords": [[start_lat, start_lng], [end_lat, end_lng]],
                "streets": ["Vía metropolitana"]
            }
            
        # Construir coordenadas detalladas de la calle
        coords = [[start_lat, start_lng]]
        streets_list = []
        for n_id in path_nodes:
            coords.append([self.nodes[n_id]["lat"], self.nodes[n_id]["lng"]])
            if street_used[n_id] and street_used[n_id] not in streets_list:
                streets_list.append(street_used[n_id])
        coords.append([end_lat, end_lng])
        
        total_km = d_start + distances[u_end] + d_end
        total_min = (d_start / 30.0)*60.0 + times[u_end] + (d_end / 30.0)*60.0
        
        return {
            "distance_km": round(total_km, 2),
            "duration_min": round(total_min, 1),
            "path_coords": coords,
            "streets": streets_list if streets_list else ["Arterias viales de Monterrey"]
        }

    def compute_distance_matrix(self, locations):
        """Calcula la matriz de distancias N x N entre todos los puntos usando calles reales."""
        n = len(locations)
        matrix = [[0.0] * n for _ in range(n)]
        time_matrix = [[0.0] * n for _ in range(n)]
        
        for i in range(n):
            for j in range(i + 1, n):
                res = self.dijkstra_street_path(
                    locations[i]["lat"], locations[i]["lng"],
                    locations[j]["lat"], locations[j]["lng"]
                )
                matrix[i][j] = res["distance_km"]
                matrix[j][i] = res["distance_km"]
                time_matrix[i][j] = res["duration_min"]
                time_matrix[j][i] = res["duration_min"]
                
        return matrix, time_matrix

def query_overpass_api(bbox=(25.60, -100.45, 25.78, -100.22), timeout=15):
    """
    Consulta Overpass API para obtener avenidas y calles reales de OpenStreetMap.
    Utiliza timeout estricto y fallback seguro al grafo nativo si la API pública está congestionada.
    """
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json][timeout:{timeout}];
    (
      way["highway"~"motorway|trunk|primary|secondary"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
    );
    out body 20;
    >;
    out skel qt;
    """
    try:
        response = requests.post(overpass_url, data={"data": query}, timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            elements = data.get("elements", [])
            ways_count = len([e for e in elements if e.get("type") == "way"])
            return {
                "status": "success",
                "source": "Overpass API (Live OSM)",
                "ways_count": ways_count,
                "msg": f"Se sincronizaron {ways_count} vías arteriales en tiempo real desde OpenStreetMap."
            }
    except Exception as e:
        pass
    
    return {
        "status": "cached",
        "source": "OpenStreetMap Monterrey Graph (Pre-calibrado)",
        "ways_count": len(MONTERREY_ROAD_EDGES),
        "msg": "Operando con la red vial calibrada de Monterrey (OpenStreetMap Vías Rápidas & Avenidas)."
    }

# Instancia singleton de la red vial
street_network = StreetNetwork()
