/**
 * app.js - Amazon Prime Logistics Optimizer
 * Integración robusta de Leaflet 1.9.4, OpenStreetMap, Chart.js y simulación de camioneta.
 */

let map = null;
let markersLayer = null;
let acoPolylineLayer = null;
let psoPolylineLayer = null;
let vanMarker = null;
let convergenceChart = null;

let currentAlgorithm = "both";
let currentObjective = "distance";
let isAddMode = false;
let currentLocations = [];
let lastOptimizationData = null;

/**
 * Inicialización controlada con detección de Leaflet
 */
function startApp() {
    if (typeof L === 'undefined') {
        console.warn("Esperando a que la librería Leaflet termine de cargar...");
        setTimeout(startApp, 100);
        return;
    }
    console.log("✅ Leaflet detectado exitosamente. Inicializando componentes...");
    initMap();
    initChart();
    loadLocations();
    checkOverpassStatus();
}

if (document.readyState === 'loading') {
    document.addEventListener("DOMContentLoaded", startApp);
} else {
    startApp();
}

/**
 * 1. Inicialización del Mapa Interactivo Leaflet 1.9.4
 */
function initMap() {
    try {
        if (map) {
            map.remove();
        }

        // Coordenadas centrales de Monterrey, N.L.
        map = L.map("map", {
            center: [25.6866, -100.3161],
            zoom: 12,
            zoomControl: true,
            scrollWheelZoom: true
        });

        // Capa de mosaicos OpenStreetMap estándar (con subdominios a, b, c)
        const osmLayer = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            maxZoom: 19,
            subdomains: ["a", "b", "c"],
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> | Amazon Logistics MTY'
        });
        osmLayer.addTo(map);

        // Capa de respaldo en caso de bloqueo o latencia en OSM
        osmLayer.on("tileerror", function (error, tile) {
            console.warn("Mosaico OSM con retraso, reintentando...");
        });

        // Grupos de capas para marcadores y polilíneas
        markersLayer = L.layerGroup().addTo(map);
        acoPolylineLayer = L.layerGroup().addTo(map);
        psoPolylineLayer = L.layerGroup().addTo(map);

        // Forzar cálculo de dimensiones en CSS Grid / Flex
        setTimeout(() => { if (map) map.invalidateSize(); }, 200);
        setTimeout(() => { if (map) map.invalidateSize(); }, 600);
        window.addEventListener("resize", () => { if (map) map.invalidateSize(); });

        // Evento de clic en el mapa para agregar ubicaciones dinámicas
        map.on("click", (e) => {
            if (isAddMode) {
                addNewPointOnMap(e.latlng.lat, e.latlng.lng);
            }
        });

        console.log("🗺️ Mapa Leaflet inicializado correctamente.");
    } catch (e) {
        console.error("Error al inicializar el mapa:", e);
    }
}

/**
 * 2. Cargar ubicaciones reales desde el servidor
 */
async function loadLocations() {
    try {
        const res = await fetch("/api/locations");
        const data = await res.json();
        if (data.status === "success") {
            currentLocations = [data.depot, ...data.deliveries];
            renderMarkers();
        }
    } catch (err) {
        console.error("Error al cargar ubicaciones:", err);
    }
}

/**
 * 3. Renderizar marcadores con estilo Amazon Prime
 */
function renderMarkers() {
    if (!map || !markersLayer) return;
    
    markersLayer.clearLayers();
    const pkgCount = parseInt(document.getElementById("slider-packages").value) || 10;
    const activeNodes = [currentLocations[0], ...currentLocations.slice(1, pkgCount + 1)];

    activeNodes.forEach((node, index) => {
        if (!node) return;
        const isDepot = index === 0;

        // Marcador HTML personalizado
        const iconHtml = isDepot
            ? `<div class="custom-pin pin-depot" style="width: 32px; height: 32px; font-size: 14px;"><i class="fa-solid fa-warehouse"></i></div>`
            : `<div class="custom-pin pin-delivery" style="width: 26px; height: 26px; font-size: 11px;">${index}</div>`;

        const customIcon = L.divIcon({
            className: "custom-div-icon",
            html: iconHtml,
            iconSize: [30, 30],
            iconAnchor: [15, 15]
        });

        const marker = L.marker([node.lat, node.lng], { icon: customIcon });

        // Popup con detalles de entrega
        const popupContent = isDepot
            ? `<div style="font-family: sans-serif; color: #111;">
                 <h4 style="margin: 0 0 4px; color: #d35400;"><i class="fa-solid fa-warehouse"></i> ${node.name}</h4>
                 <p style="margin: 0; font-size: 12px; color: #555;">${node.address}</p>
                 <div style="margin-top: 6px; font-size: 11px; background: #fff3cd; padding: 4px 6px; border-radius: 4px;">
                   <b>Hub Central MTY:</b> Origen y destino de la flota de reparto.
                 </div>
               </div>`
            : `<div style="font-family: sans-serif; color: #111; min-width: 180px;">
                 <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                   <h4 style="margin: 0; color: #007185;"><i class="fa-solid fa-box"></i> Parada #${index}</h4>
                   <span style="font-size: 10px; background: #232f3e; color: #ff9900; font-weight: bold; padding: 2px 5px; border-radius: 3px;">${node.priority || 'Media'}</span>
                 </div>
                 <p style="margin: 0 0 4px; font-size: 12px; font-weight: bold;">${node.customer || 'Cliente Prime'}</p>
                 <p style="margin: 0; font-size: 11px; color: #666;">${node.address}</p>
                 <hr style="margin: 6px 0; border: none; border-top: 1px solid #eee;">
                 <div style="font-size: 11px; color: #333;">
                   <div><b>Tracking:</b> <code>${node.package_id || 'AMZN-9999'}</code></div>
                   <div><b>Peso:</b> ${node.weight || '1.5 kg'}</div>
                   <div><b>Ventana:</b> ${node.time_window || '10:00 - 18:00'}</div>
                   <div><b>Contenido:</b> ${node.items || 'Paquete Prime'}</div>
                 </div>
               </div>`;

        marker.bindPopup(popupContent);
        markersLayer.addLayer(marker);
    });
}

/**
 * 4. Control de sincronización de inputs en el sidebar
 */
function syncVal(id) {
    const el = document.getElementById(id);
    const target = document.getElementById(`val-${id}`);
    if (el && target) {
        target.innerText = el.value;
    }
}

function updatePackageCount(val) {
    document.getElementById("val-packages").innerText = val;
    renderMarkers();
}

function setAlgorithm(algo) {
    currentAlgorithm = algo;
    document.querySelectorAll(".algo-btn").forEach(btn => {
        btn.classList.toggle("active", btn.dataset.algo === algo);
    });

    const acoPanel = document.getElementById("aco-params-panel");
    const psoPanel = document.getElementById("pso-params-panel");

    if (algo === "both") {
        if (acoPanel) acoPanel.style.display = "block";
        if (psoPanel) psoPanel.style.display = "block";
    } else if (algo === "aco") {
        if (acoPanel) acoPanel.style.display = "block";
        if (psoPanel) psoPanel.style.display = "none";
    } else {
        if (acoPanel) acoPanel.style.display = "none";
        if (psoPanel) psoPanel.style.display = "block";
    }
}

function setObjective(obj) {
    currentObjective = obj;
    document.querySelectorAll(".obj-btn").forEach(btn => {
        btn.classList.toggle("active", btn.dataset.obj === obj);
    });
}

function toggleAddMode() {
    isAddMode = !isAddMode;
    const btn = document.getElementById("btn-add-mode");
    if (!btn) return;
    
    if (isAddMode) {
        btn.style.borderColor = "var(--amazon-orange)";
        btn.style.color = "var(--amazon-orange)";
        btn.innerHTML = `<i class="fa-solid fa-crosshairs"></i> Haz clic en el mapa...`;
    } else {
        btn.style.borderColor = "var(--border-color)";
        btn.style.color = "var(--text-primary)";
        btn.innerHTML = `<i class="fa-solid fa-plus"></i> Clic en Mapa`;
    }
}

async function addNewPointOnMap(lat, lng) {
    toggleAddMode();
    try {
        const res = await fetch("/api/locations/add", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                lat: lat,
                lng: lng,
                name: `Entrega Dinámica #${currentLocations.length}`,
                customer: `Cliente Prime #${currentLocations.length}`
            })
        });
        const data = await res.json();
        if (data.status === "success") {
            currentLocations.push(data.point);
            const slider = document.getElementById("slider-packages");
            slider.max = currentLocations.length - 1;
            slider.value = currentLocations.length - 1;
            document.getElementById("val-packages").innerText = slider.value;
            renderMarkers();
        }
    } catch (err) {
        console.error("Error al añadir ubicación:", err);
    }
}

async function resetLocations() {
    try {
        const res = await fetch("/api/locations/reset", { method: "POST" });
        const data = await res.json();
        if (data.status === "success") {
            const slider = document.getElementById("slider-packages");
            slider.value = 10;
            document.getElementById("val-packages").innerText = 10;
            loadLocations();
        }
    } catch (err) {
        console.error("Error al resetear ubicaciones:", err);
    }
}

/**
 * 5. Ejecución del Motor Bioinspirado de Optimización
 */
async function runOptimization() {
    const btn = document.getElementById("btn-run-optimization");
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Optimizando en OpenStreetMap...`;
    }

    const pkgCount = parseInt(document.getElementById("slider-packages").value) || 10;

    const payload = {
        algorithm: currentAlgorithm,
        objective: currentObjective,
        num_deliveries: pkgCount,
        aco_params: {
            alpha: parseFloat(document.getElementById("aco-alpha").value),
            beta: parseFloat(document.getElementById("aco-beta").value),
            rho: parseFloat(document.getElementById("aco-rho").value),
            n_ants: parseInt(document.getElementById("aco-ants").value),
            n_iter: parseInt(document.getElementById("aco-iter").value),
            elitism: parseInt(document.getElementById("aco-elitism").value),
            Q: 100.0
        },
        pso_params: {
            n_particles: parseInt(document.getElementById("pso-particles").value),
            n_iter: parseInt(document.getElementById("pso-iter").value),
            w: parseFloat(document.getElementById("pso-w").value),
            c1: parseFloat(document.getElementById("pso-c1").value),
            c2: parseFloat(document.getElementById("pso-c2").value),
            vmax: parseFloat(document.getElementById("pso-vmax").value)
        }
    };

    try {
        const res = await fetch("/api/optimize", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const result = await res.json();
        if (result.status === "success") {
            lastOptimizationData = result.data;
            updateDashboard(result.data);
        }
    } catch (err) {
        console.error("Error en optimización:", err);
        alert("Ocurrió un error al procesar la ruta en el servidor.");
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `<i class="fa-solid fa-bolt"></i> Optimizar Reparto Amazon`;
        }
    }
}

/**
 * 6. Actualizar KPIs, Polilíneas en Leaflet y Gráfica
 */
function updateDashboard(data) {
    if (acoPolylineLayer) acoPolylineLayer.clearLayers();
    if (psoPolylineLayer) psoPolylineLayer.clearLayers();

    const baseline = data.baseline;
    let mainResult = data.aco || data.pso;

    if (data.aco && data.pso) {
        mainResult = (data.aco.total_distance_km <= data.pso.total_distance_km) ? data.aco : data.pso;
    }

    if (document.getElementById("kpi-dist")) {
        document.getElementById("kpi-dist").innerText = `${mainResult.total_distance_km} km`;
    }
    if (document.getElementById("kpi-dist-sub")) {
        document.getElementById("kpi-dist-sub").innerText = `Línea Base: ${baseline.total_distance_km} km`;
    }
    if (document.getElementById("kpi-time")) {
        document.getElementById("kpi-time").innerText = `${mainResult.total_duration_min} min`;
    }
    if (document.getElementById("kpi-time-sub")) {
        document.getElementById("kpi-time-sub").innerText = `Velocidades viales de Monterrey`;
    }

    const savingsPct = (((baseline.total_distance_km - mainResult.total_distance_km) / baseline.total_distance_km) * 100).toFixed(1);
    if (document.getElementById("kpi-savings")) {
        document.getElementById("kpi-savings").innerText = `${savingsPct}%`;
    }

    if (document.getElementById("kpi-fuel")) {
        document.getElementById("kpi-fuel").innerText = `${mainResult.logistics_kpis.fuel_liters} L ($${mainResult.logistics_kpis.fuel_cost_mxn} MXN)`;
    }
    if (document.getElementById("kpi-co2")) {
        document.getElementById("kpi-co2").innerText = `${mainResult.logistics_kpis.co2_emissions_kg} kg CO₂ emitidos`;
    }
    if (document.getElementById("kpi-exec")) {
        document.getElementById("kpi-exec").innerText = `${mainResult.execution_time_ms} ms`;
    }

    // Dibujar Ruta ACO en el Mapa (Naranja Amazon)
    if (data.aco && map && acoPolylineLayer) {
        const acoLine = L.polyline(data.aco.polyline, {
            color: "#ff9900",
            weight: 5,
            opacity: 0.9,
            lineJoin: "round"
        }).addTo(acoPolylineLayer);

        acoLine.bindPopup(`<b>Ruta Óptima ACO:</b> ${data.aco.total_distance_km} km (${data.aco.total_duration_min} min)`);
    }

    // Dibujar Ruta PSO en el Mapa (Cyan punteado)
    if (data.pso && map && psoPolylineLayer) {
        const psoLine = L.polyline(data.pso.polyline, {
            color: "#00e5ff",
            weight: 4,
            opacity: 0.8,
            dashArray: "8, 6",
            lineJoin: "round"
        }).addTo(psoPolylineLayer);

        psoLine.bindPopup(`<b>Ruta PSO:</b> ${data.pso.total_distance_km} km (${data.pso.total_duration_min} min)`);
    }

    // Ajustar zoom a la ruta
    const activeLine = data.aco ? data.aco.polyline : data.pso.polyline;
    if (activeLine && activeLine.length > 0 && map) {
        map.fitBounds(L.polyline(activeLine).getBounds(), { padding: [30, 30] });
    }

    // Actualizar gráfica de convergencia
    updateConvergenceChart(data);

    // Actualizar lista de itinerario
    updateItineraryList(mainResult.segments);
}

/**
 * 7. Gráfica de Convergencia con Chart.js
 */
function initChart() {
    const canvas = document.getElementById("convergenceChart");
    if (!canvas || typeof Chart === 'undefined') return;
    
    const ctx = canvas.getContext("2d");
    convergenceChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: [],
            datasets: []
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: "index", intersect: false },
            plugins: {
                legend: {
                    labels: { color: "#8b949e", font: { size: 10 } }
                }
            },
            scales: {
                x: {
                    title: { display: true, text: "Iteración", color: "#6e7681", font: { size: 10 } },
                    grid: { color: "#21262d" },
                    ticks: { color: "#8b949e", font: { size: 9 } }
                },
                y: {
                    title: { display: true, text: "Costo de Ruta (km / min)", color: "#6e7681", font: { size: 10 } },
                    grid: { color: "#21262d" },
                    ticks: { color: "#8b949e", font: { size: 9 } }
                }
            }
        }
    });
}

function updateConvergenceChart(data) {
    if (!convergenceChart) return;
    
    const datasets = [];
    let maxIters = 0;

    if (data.aco) {
        maxIters = Math.max(maxIters, data.aco.convergence.length);
        datasets.push({
            label: "ACO (Hormigas)",
            data: data.aco.convergence,
            borderColor: "#ff9900",
            backgroundColor: "rgba(255, 153, 0, 0.1)",
            borderWidth: 2,
            pointRadius: 0,
            fill: true,
            tension: 0.1
        });
    }

    if (data.pso) {
        maxIters = Math.max(maxIters, data.pso.convergence.length);
        datasets.push({
            label: "PSO (Partículas)",
            data: data.pso.convergence,
            borderColor: "#00e5ff",
            backgroundColor: "rgba(0, 229, 255, 0.05)",
            borderWidth: 2,
            pointRadius: 0,
            fill: true,
            borderDash: [5, 5],
            tension: 0.1
        });
    }

    const labels = Array.from({ length: maxIters }, (_, i) => i + 1);

    convergenceChart.data.labels = labels;
    convergenceChart.data.datasets = datasets;
    convergenceChart.update();
}

/**
 * 8. Itinerario Calle por Calle con Dijkstra
 */
function updateItineraryList(segments) {
    const container = document.getElementById("itinerary-list");
    if (!container) return;
    
    document.getElementById("itinerary-count").innerText = `${segments.length} Tramos`;
    container.innerHTML = "";

    segments.forEach((seg, idx) => {
        const item = document.createElement("div");
        item.className = "itinerary-step";
        item.innerHTML = `
            <div class="step-num">${idx + 1}</div>
            <div class="step-info">
                <div style="font-weight: 600; color: #f0f6fc;">${seg.from_node} ➔ ${seg.to_node}</div>
                <div style="font-size: 11px; color: #8b949e;">Calles: ${seg.streets.join(", ")}</div>
            </div>
            <div class="step-meta">
                ${seg.distance_km} km | ${seg.duration_min} min
            </div>
        `;
        container.appendChild(item);
    });
}

/**
 * 9. Simulación Animada de la Camioneta de Reparto Amazon
 */
function simulateVanMovement() {
    if (!lastOptimizationData) {
        alert("Primero ejecuta la optimización para generar la ruta.");
        return;
    }

    const polyline = (lastOptimizationData.aco || lastOptimizationData.pso).polyline;
    if (!polyline || polyline.length === 0 || !map) return;

    if (vanMarker) {
        map.removeLayer(vanMarker);
    }

    const vanIcon = L.divIcon({
        className: "van-marker-div",
        html: `<div style="background: #111; color: #ff9900; border: 2px solid #ff9900; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 12px rgba(255,153,0,0.8); font-size: 14px;">
                 <i class="fa-solid fa-truck"></i>
               </div>`,
        iconSize: [30, 30],
        iconAnchor: [15, 15]
    });

    vanMarker = L.marker(polyline[0], { icon: vanIcon }).addTo(map);

    let step = 0;
    const totalSteps = polyline.length;
    const speed = 40;

    const btn = document.getElementById("btn-van-sim");
    if (btn) {
        btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin" style="color: #ff9900;"></i> En ruta...`;
        btn.disabled = true;
    }

    const interval = setInterval(() => {
        if (step >= totalSteps) {
            clearInterval(interval);
            if (btn) {
                btn.innerHTML = `<i class="fa-solid fa-truck-fast" style="color: #ff9900;"></i> Simular Camioneta`;
                btn.disabled = false;
            }
            vanMarker.bindPopup("<b>¡Entrega completada!</b> Todos los paquetes fueron entregados con éxito en Monterrey.").openPopup();
            return;
        }

        vanMarker.setLatLng(polyline[step]);
        step++;
    }, speed);
}

/**
 * 10. Comprobación de estado de Overpass API
 */
async function checkOverpassStatus() {
    try {
        const res = await fetch("/api/overpass_status");
        const data = await res.json();
        const textEl = document.getElementById("osm-status-text");
        if (textEl) {
            if (data.status === "success") {
                textEl.innerText = `OSM Overpass Activo (${data.ways_count} vías)`;
            } else {
                textEl.innerText = `OSM Red Vial Monterrey (${data.ways_count} vías)`;
            }
        }
    } catch (err) {
        console.log("OSM modo estándar.");
    }
}
