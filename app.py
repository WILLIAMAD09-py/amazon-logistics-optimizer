"""
app.py
Servidor Flask de la plataforma de optimización de rutas de reparto Amazon Prime Logistics (Monterrey, N.L.).
Integra Leaflet 1.9.4, OpenStreetMap (OSM), Overpass API, Dijkstra, ACO y PSO.
Listo para despliegue gratuito en Render.
"""

import os
from flask import Flask, render_template, request, jsonify
from core.amazon_data import DEPOT, DELIVERY_POINTS, get_all_locations
from core.graph import street_network, query_overpass_api
from core.aco import run_aco_optimizer
from core.pso import run_pso_optimizer
from core.baseline import run_nearest_neighbor

app = Flask(__name__)

# Memoria de ubicaciones activas
active_locations = get_all_locations()

@app.route("/")
def index():
    """Página principal con Leaflet, panel de hiperparámetros y métricas en vivo."""
    return render_template("index.html")

@app.route("/api/locations", methods=["GET"])
def get_locations():
    """Devuelve las ubicaciones actuales (Depósito Amazon + Paquetes)."""
    return jsonify({
        "status": "success",
        "depot": active_locations[0],
        "deliveries": active_locations[1:],
        "count": len(active_locations)
    })

@app.route("/api/locations/add", methods=["POST"])
def add_location():
    """Permite al usuario agregar un nuevo paquete de entrega haciendo clic en el mapa."""
    data = request.get_json() or {}
    lat = float(data.get("lat"))
    lng = float(data.get("lng"))
    name = data.get("name", f"Entrega Personalizada #{len(active_locations)}")
    address = data.get("address", f"Coordenadas: {round(lat, 4)}, {round(lng, 4)}")
    
    new_point = {
        "id": len(active_locations),
        "name": name,
        "address": address,
        "lat": lat,
        "lng": lng,
        "customer": data.get("customer", "Cliente Prime MTY"),
        "package_id": f"AMZN-{1000 + len(active_locations)}-X",
        "weight": "2.0 kg",
        "priority": "Alta",
        "time_window": "10:00 - 18:00",
        "items": "Paquete Amazon Prime"
    }
    active_locations.append(new_point)
    return jsonify({"status": "success", "point": new_point, "total": len(active_locations)})

@app.route("/api/locations/reset", methods=["POST"])
def reset_locations():
    """Restablece los puntos a la flota predeterminada de Monterrey."""
    global active_locations
    active_locations = get_all_locations()
    return jsonify({"status": "success", "total": len(active_locations)})

@app.route("/api/overpass_status", methods=["GET"])
def overpass_status():
    """Verifica la conectividad con OpenStreetMap y Overpass API."""
    res = query_overpass_api()
    return jsonify(res)

@app.route("/api/optimize", methods=["POST"])
def optimize():
    """
    Ejecuta la optimización bioinspirada (ACO, PSO o Comparativa Ambos)
    calculando la ruta sobre calles reales con Dijkstra y métricas logísticas de Amazon.
    """
    data = request.get_json() or {}
    algo_choice = data.get("algorithm", "both").lower()
    objective = data.get("objective", "distance")  # "distance" o "time"
    
    # Cantidad de paquetes seleccionados (filtro o personalización)
    num_deliveries = int(data.get("num_deliveries", len(active_locations) - 1))
    current_nodes = [active_locations[0]] + active_locations[1:num_deliveries + 1]
    
    # 1. Calcular matriz de distancias y tiempos viales reales con Dijkstra
    dist_mat, time_mat = street_network.compute_distance_matrix(current_nodes)
    
    # 2. Línea Base Ingenua
    nn_res = run_nearest_neighbor(dist_mat, time_mat)
    
    results = {
        "objective": objective,
        "num_locations": len(current_nodes),
        "baseline": nn_res
    }
    
    def build_street_polyline(route_indices):
        """Convierte la secuencia de paradas en una polilínea detallada de calles reales con Dijkstra."""
        full_coords = []
        street_segments = []
        for i in range(len(route_indices) - 1):
            u_idx = route_indices[i]
            v_idx = route_indices[i + 1]
            seg = street_network.dijkstra_street_path(
                current_nodes[u_idx]["lat"], current_nodes[u_idx]["lng"],
                current_nodes[v_idx]["lat"], current_nodes[v_idx]["lng"]
            )
            # Evitar duplicar el nodo de unión
            if full_coords and seg["path_coords"]:
                full_coords.extend(seg["path_coords"][1:])
            else:
                full_coords.extend(seg["path_coords"])
                
            street_segments.append({
                "from_node": current_nodes[u_idx]["name"],
                "to_node": current_nodes[v_idx]["name"],
                "distance_km": seg["distance_km"],
                "duration_min": seg["duration_min"],
                "streets": seg["streets"]
            })
        return full_coords, street_segments

    # 3. Ejecutar ACO si fue solicitado
    if algo_choice in ["aco", "both"]:
        aco_p = data.get("aco_params", {})
        aco_res = run_aco_optimizer(
            dist_mat, time_mat,
            n_ants=int(aco_p.get("n_ants", 25)),
            n_iter=int(aco_p.get("n_iter", 100)),
            alpha=float(aco_p.get("alpha", 1.0)),
            beta=float(aco_p.get("beta", 2.0)),
            rho=float(aco_p.get("rho", 0.1)),
            Q=float(aco_p.get("Q", 100.0)),
            elitism=int(aco_p.get("elitism", 3)),
            objective=objective
        )
        coords_aco, segs_aco = build_street_polyline(aco_res["route_indices"])
        aco_res["polyline"] = coords_aco
        aco_res["segments"] = segs_aco
        # Estimaciones logísticas Amazon
        # Camioneta eléctrica/diésel Amazon: ~0.18 L/km, $24 MXN/L, 2.3 kg CO2/L
        fuel_liters = round(aco_res["total_distance_km"] * 0.18, 2)
        co2_kg = round(fuel_liters * 2.31, 2)
        aco_res["logistics_kpis"] = {
            "fuel_liters": fuel_liters,
            "fuel_cost_mxn": round(fuel_liters * 24.50, 2),
            "co2_emissions_kg": co2_kg,
            "efficiency_vs_baseline": round(((nn_res["total_distance_km"] - aco_res["total_distance_km"]) / nn_res["total_distance_km"]) * 100, 1)
        }
        results["aco"] = aco_res

    # 4. Ejecutar PSO si fue solicitado
    if algo_choice in ["pso", "both"]:
        pso_p = data.get("pso_params", {})
        pso_res = run_pso_optimizer(
            dist_mat, time_mat,
            n_particles=int(pso_p.get("n_particles", 30)),
            n_iter=int(pso_p.get("n_iter", 100)),
            w=float(pso_p.get("w", 0.72)),
            c1=float(pso_p.get("c1", 1.49)),
            c2=float(pso_p.get("c2", 1.49)),
            vmax=float(pso_p.get("vmax", 4.0)),
            objective=objective
        )
        coords_pso, segs_pso = build_street_polyline(pso_res["route_indices"])
        pso_res["polyline"] = coords_pso
        pso_res["segments"] = segs_pso
        fuel_liters_pso = round(pso_res["total_distance_km"] * 0.18, 2)
        co2_kg_pso = round(fuel_liters_pso * 2.31, 2)
        pso_res["logistics_kpis"] = {
            "fuel_liters": fuel_liters_pso,
            "fuel_cost_mxn": round(fuel_liters_pso * 24.50, 2),
            "co2_emissions_kg": co2_kg_pso,
            "efficiency_vs_baseline": round(((nn_res["total_distance_km"] - pso_res["total_distance_km"]) / nn_res["total_distance_km"]) * 100, 1)
        }
        results["pso"] = pso_res

    # Si se ejecutaron ambos, generar comparativa directa
    if algo_choice == "both":
        diff_km = round(results["pso"]["total_distance_km"] - results["aco"]["total_distance_km"], 2)
        diff_pct = round((diff_km / results["pso"]["total_distance_km"]) * 100, 1)
        results["comparison"] = {
            "winner": "ACO" if diff_km > 0 else "PSO",
            "distance_advantage_km": abs(diff_km),
            "advantage_percentage": abs(diff_pct),
            "time_advantage_min": round(abs(results["pso"]["total_duration_min"] - results["aco"]["total_duration_min"]), 1),
            "verdict": f"ACO supera a PSO por {abs(diff_km)} km menos de recorrido, ahorrando {results['aco']['logistics_kpis']['fuel_cost_mxn']} MXN en combustible." if diff_km > 0 else "PSO alcanzó una ruta competitiva."
        }
        
    return jsonify({"status": "success", "data": results})

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "Amazon Logistics Optimizer MTY"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
