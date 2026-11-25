# 🚚 Amazon Prime Logistics Optimizer: Sistema Bioinspirado de Reparto (ACO & PSO)
### Producto Integrador de Aprendizaje (PIA) - Algoritmos Bioinspirados
**Universidad Autónoma de Nuevo León (UANL) | Escuela Industrial y Preparatoria Técnica "Álvaro Obregón" (EIAO)**  
**Alumno:** William Gómez Velázquez | **Matrícula:** 2250780 | **Carrera:** Técnico en Inteligencia Artificial BPI

---

## 📌 1. Descripción del Proyecto
Este sistema es una plataforma web interactiva de optimización de última milla inspirada en la infraestructura logística global de **Amazon**. Permite simular y optimizar el reparto diario de paquetería desde un centro de distribución (*Hub Central*) hacia múltiples destinos reales en el **Área Metropolitana de Monterrey, Nuevo León**, permitiendo la manipulación dinámica de hiperparámetros en tiempo real para algoritmos bioinspirados:

1. **ACO (Ant Colony Optimization):** Algoritmo por colonias de hormigas para enrutamiento en grafos discretos ponderados.
2. **PSO (Particle Swarm Optimization):** Algoritmo por enjambre de partículas mediante codificación de claves aleatorias (*Random-Key*).
3. **Dijkstra:** Algoritmo de caminos mínimos sobre la red vial física de avenidas y calles reales.
4. **Línea Base Ingenua:** Heurística del vecino más cercano (*Nearest Neighbor*) para contrastar ahorros de combustible, tiempo y emisiones de CO₂.

---

## 🔬 2. Investigación: El Sistema de Optimización de Amazon con ACO y PSO
En la industria logística moderna, **Amazon** procesa más de 13 millones de paquetes al día a nivel global. El problema de enrutar las camionetas de reparto (*Amazon Delivery Vans*) pertenece a la clase de complejidad **NP-Hard (Vehicle Routing Problem con ventanas de tiempo - VRPTW)**:

* **¿Cómo usa Amazon ACO (Ant Colony Optimization)?:**  
  Amazon modela las ciudades como grafos ponderados dirigidos donde los arcos representan tramos de calles. Las hormigas artificiales depositan "feromonas virtuales" en las rutas que experimentan menor congestión y menor costo kilométrico. Este enfoque permite una adaptación estocástica dinámica: si una avenida (como Av. Constitución o Gonzalitos) sufre un accidente o congestión en hora pico, la evaporación de feromonas $\rho$ penaliza esa ruta rápidamente y promueve caminos alternos descubiertos por otras hormigas.
* **¿Cómo usa Amazon PSO (Particle Swarm Optimization)?:**  
  PSO se implementa primordialmente en la optimización continua de la flota: estimación de tiempos de servicio, calibración paramétrica de velocidades promedio por zona horaria y enrutamiento jerárquico continuo (asignación de clústeres de entrega a diferentes camionetas antes de la secuenciación final).

---

## 🗺️ 3. Tecnologías Utilizadas (100% Gratuitas y de Código Abierto)
1. **Leaflet (versión 1.9.4):** Librería de JavaScript para renderizar el mapa interactivo (zoom, marcadores personalizados de almacén y paradas, trazado de polilíneas viales y animación de camioneta). Cargada directamente desde el CDN de `cdnjs`.
2. **OpenStreetMap (OSM):** Proveedor cartográfico base (`tile.openstreetmap.org`) sin costo y sin requerir API keys. Incorpora un filtro CSS cálido para armonizar con el diseño de Amazon Prime.
3. **Overpass API:** Servicio que consulta la base de datos de OpenStreetMap para extraer avenidas, sentidos (`oneway`) y velocidades máximas (`maxspeed`), construyendo el grafo vial real para Dijkstra.
4. **Backend Python (Flask):** Servidor ligero y modular con endpoints REST para ejecutar la optimización y servir los archivos estáticos.
5. **Chart.js:** Gráficas interactivas en vivo que comparan la curva de convergencia iteración por iteración entre ACO y PSO.

---

## 🚀 4. Ejecución en Local

### Prerrequisitos:
* Python 3.9 o superior instalado.

### Pasos:
```bash
# 1. Clonar o navegar a la carpeta del proyecto
cd PIA_Amazon_Optimizer

# 2. Instalar dependencias (Flask, Requests, NumPy, Gunicorn)
pip install -r requirements.txt

# 3. Iniciar el servidor
python app.py
```
Abre tu navegador en: **`http://localhost:5000`**

---

## 🌐 5. Despliegue Gratuito en Render ($0 Costo)

El proyecto está preconfigurado para desplegarse gratis en **Render** mediante su plan gratuito de Web Service:

### Pasos para alojarlo en Render:
1. Crea una cuenta gratuita en [render.com](https://render.com).
2. Sube esta carpeta a un repositorio de GitHub (público o privado).
3. En el panel de Render, haz clic en **New +** y selecciona **Web Service**.
4. Conecta tu repositorio de GitHub.
5. Configura los siguientes campos:
   * **Name:** `amazon-logistics-optimizer`
   * **Language:** `Python 3`
   * **Build Command:** `pip install -r requirements.txt`
   * **Start Command:** `gunicorn app:app`
   * **Instance Type:** `Free`
6. Haz clic en **Create Web Service**.
7. En unos 2 minutos, Render te proporcionará tu URL pública gratuita (ejemplo: `https://amazon-logistics-optimizer.onrender.com`), la cual estará activa 24/7 sin ningún costo ni tarjeta de crédito.

---

## ⚙️ 6. Hiperparámetros Configurables en la Plataforma

### Para ACO:
* $\alpha$ (Alfa): Peso de la feromona (memoria colectiva acumulada).
* $\beta$ (Beta): Peso de la heurística de cercanía ($1 / \text{distancia}$).
* $\rho$ (Rho): Tasa de evaporación de feromonas por ciclo ($0 < \rho < 1$).
* Hormigas ($m$): Tamaño de la colonia exploradora.
* Iteraciones: Presupuesto computacional del algoritmo.
* Elitismo ($e$): Refuerzo multiplicativo otorgado a la mejor ruta global.

### Para PSO:
* $n$: Número de partículas en el enjambre.
* $w$: Factor de inercia de la velocidad.
* $c_1$: Coeficiente de aprendizaje cognitivo (memoria individual).
* $c_2$: Coeficiente de aprendizaje social (cooperación del enjambre).
* $v_{\max}$: Límite de velocidad por iteración.
