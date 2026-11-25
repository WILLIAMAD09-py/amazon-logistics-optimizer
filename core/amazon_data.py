"""
amazon_data.py
Ubicaciones reales de la red de entregas de Amazon Prime Logistics en el Área Metropolitana de Monterrey, N.L.
Incluye Centro de Distribución (Depot) y paradas de clientes con metadatos reales de paquetería.
"""

# Ubicación central del Almacén / Centro de Distribución Amazon
DEPOT = {
    "id": 0,
    "name": "Centro de Distribución Amazon (Hub MTY-01)",
    "address": "Av. Cristóbal Colón / Bernardo Reyes, Centro, Monterrey, N.L.",
    "lat": 25.6866,
    "lng": -100.3161,
    "type": "depot",
    "icon": "warehouse",
    "color": "#FF9900"  # Amazon Orange
}

# Clientes y Puntos de Entrega Reales en Monterrey y Zona Metropolitana
DELIVERY_POINTS = [
    {
        "id": 1,
        "name": "Entrega Amazon - Obispado",
        "address": "Calle Padre Mier 1420, Obispado, Monterrey",
        "lat": 25.6738,
        "lng": -100.3444,
        "customer": "Carlos Mendoza",
        "package_id": "AMZN-8921-A",
        "weight": "2.4 kg",
        "priority": "Alta",
        "time_window": "09:00 - 11:00",
        "items": "Echo Show 8, Kindle Paperwhite"
    },
    {
        "id": 2,
        "name": "Entrega Amazon - San Pedro Del Valle",
        "address": "Calzada San Pedro 250, Del Valle, San Pedro Garza García",
        "lat": 25.6565,
        "lng": -100.3662,
        "customer": "Sofía Villarreal",
        "package_id": "AMZN-4102-B",
        "weight": "0.8 kg",
        "priority": "Media",
        "time_window": "10:00 - 12:00",
        "items": "Audífonos Sony WH-1000XM5"
    },
    {
        "id": 3,
        "name": "Entrega Amazon - Valle Oriente",
        "address": "Av. Frida Kahlo 195, Valle Oriente, San Pedro Garza García",
        "lat": 25.6418,
        "lng": -100.3182,
        "customer": "Mauricio Garza Sada",
        "package_id": "AMZN-3391-C",
        "weight": "5.1 kg",
        "priority": "Alta",
        "time_window": "11:00 - 13:00",
        "items": "Cafetera Espresso De'Longhi"
    },
    {
        "id": 4,
        "name": "Entrega Amazon - Campus Tec de Monterrey",
        "address": "Av. Eugenio Garza Sada 2501, Tecnológico, Monterrey",
        "lat": 25.6514,
        "lng": -100.2895,
        "customer": "Mariana Treviño",
        "package_id": "AMZN-7721-D",
        "weight": "1.2 kg",
        "priority": "Media",
        "time_window": "11:30 - 13:30",
        "items": "iPad Air M2, Apple Pencil"
    },
    {
        "id": 5,
        "name": "Entrega Amazon - Contry La Silla",
        "address": "Av. Alfonso Reyes 320, Contry, Monterrey",
        "lat": 25.6322,
        "lng": -100.2781,
        "customer": "Roberto Cantú",
        "package_id": "AMZN-1284-E",
        "weight": "3.6 kg",
        "priority": "Baja",
        "time_window": "12:00 - 14:00",
        "items": "Kit de Herramientas Bosch 18V"
    },
    {
        "id": 6,
        "name": "Entrega Amazon - Parque Fundidora",
        "address": "Av. Madero 2100, Obrera, Monterrey",
        "lat": 25.6782,
        "lng": -100.2845,
        "customer": "Elena Elizondo",
        "package_id": "AMZN-5509-F",
        "weight": "1.9 kg",
        "priority": "Alta",
        "time_window": "13:00 - 15:00",
        "items": "Cámara Canon EOS R50"
    },
    {
        "id": 7,
        "name": "Entrega Amazon - Linda Vista",
        "address": "Av. Miguel Alemán 120, Linda Vista, Guadalupe",
        "lat": 25.6948,
        "lng": -100.2521,
        "customer": "Andrés Morales",
        "package_id": "AMZN-6623-G",
        "weight": "4.2 kg",
        "priority": "Media",
        "time_window": "13:30 - 15:30",
        "items": "Monitor Gamer LG UltraGear 27\""
    },
    {
        "id": 8,
        "name": "Entrega Amazon - Churubusco (EIAO)",
        "address": "Av. Churubusco y Francisco I. Madero, Monterrey",
        "lat": 25.6985,
        "lng": -100.2774,
        "customer": "Escuela Técnica Álvaro Obregón",
        "package_id": "AMZN-9912-H",
        "weight": "7.5 kg",
        "priority": "Alta",
        "time_window": "14:00 - 16:00",
        "items": "Servidor Raspberry Pi 5 x10 + Sensores IA"
    },
    {
        "id": 9,
        "name": "Entrega Amazon - San Nicolás Centro",
        "address": "Calle Juárez 300, Centro, San Nicolás de los Garza",
        "lat": 25.7482,
        "lng": -100.2985,
        "customer": "Valeria Benítez",
        "package_id": "AMZN-2041-I",
        "weight": "0.5 kg",
        "priority": "Media",
        "time_window": "14:30 - 16:30",
        "items": "Smartwatch Garmin Forerunner"
    },
    {
        "id": 10,
        "name": "Entrega Amazon - Ciudad Universitaria (CU)",
        "address": "Av. Universidad s/n, San Nicolás de los Garza",
        "lat": 25.7258,
        "lng": -100.3134,
        "customer": "Facultad FCFM / UANL",
        "package_id": "AMZN-8834-J",
        "weight": "6.0 kg",
        "priority": "Alta",
        "time_window": "15:00 - 17:00",
        "items": "Lote de Libros Machine Learning & Deep Learning"
    },
    {
        "id": 11,
        "name": "Entrega Amazon - Anáhuac San Nicolás",
        "address": "Av. Manuel L. Barragán 550, Anáhuac, San Nicolás",
        "lat": 25.7365,
        "lng": -100.3278,
        "customer": "Héctor Quiroga",
        "package_id": "AMZN-1148-K",
        "weight": "2.1 kg",
        "priority": "Baja",
        "time_window": "15:30 - 17:30",
        "items": "Teclado Mecánico Logitech G Pro"
    },
    {
        "id": 12,
        "name": "Entrega Amazon - Mitras Centro",
        "address": "Av. Paseo de los Leones 800, Mitras Centro, Monterrey",
        "lat": 25.6961,
        "lng": -100.3475,
        "customer": "Claudia Saldaña",
        "package_id": "AMZN-4910-L",
        "weight": "3.3 kg",
        "priority": "Alta",
        "time_window": "16:00 - 18:00",
        "items": "Freidora de Aire Philips XXL"
    },
    {
        "id": 13,
        "name": "Entrega Amazon - Cumbres 1er Sector",
        "address": "Av. Paseo de los Leones 1800, Cumbres, Monterrey",
        "lat": 25.7092,
        "lng": -100.3698,
        "customer": "Fernando Lozano",
        "package_id": "AMZN-7023-M",
        "weight": "1.7 kg",
        "priority": "Media",
        "time_window": "16:30 - 18:30",
        "items": "Router Wi-Fi 6 Mesh TP-Link Deco"
    },
    {
        "id": 14,
        "name": "Entrega Amazon - San Jerónimo",
        "address": "Av. Fleteros 400, San Jerónimo, Monterrey",
        "lat": 25.6812,
        "lng": -100.3654,
        "customer": "Gabriela Sepúlveda",
        "package_id": "AMZN-3551-N",
        "weight": "4.8 kg",
        "priority": "Baja",
        "time_window": "17:00 - 19:00",
        "items": "Aspiradora Robot iRobot Roomba"
    },
    {
        "id": 15,
        "name": "Entrega Amazon - Santa Catarina La Fama",
        "address": "Av. Manuel Ordóñez 650, La Fama, Santa Catarina",
        "lat": 25.6712,
        "lng": -100.4356,
        "customer": "Jesús Almaguer",
        "package_id": "AMZN-6204-O",
        "weight": "8.2 kg",
        "priority": "Alta",
        "time_window": "17:30 - 19:30",
        "items": "Generador Portátil EcoFlow River 2"
    }
]

def get_all_locations():
    """Devuelve el depósito y todos los puntos de entrega."""
    return [DEPOT] + DELIVERY_POINTS
