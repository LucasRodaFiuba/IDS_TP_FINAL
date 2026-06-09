from api.db import get_db_connection

def obtener_metricas_dashboard(filtros):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # 1. Recuperar los filtros del Frontend
    f_inicio = filtros.get('fecha_inicio', '2026-05-01')
    f_fin = filtros.get('fecha_fin', '2026-05-31')
    incluir_canceladas = filtros.get('incluir_canceladas', False)

    # Definir la lógica de estados según el checkbox
    estados = "('confirmada', 'pendiente', 'finalizada')"
    if incluir_canceladas:
        estados = "('confirmada', 'pendiente', 'finalizada', 'cancelada')"

    # 2. Métrica: Total de reservas y cubiertos proyectados
    query_reservas = f"""
        SELECT 
            COUNT(*) as total_reservas,
            IFNULL(SUM(cantidad_personas), 0) as total_cubiertos
        FROM reservas
        WHERE fecha_reserva BETWEEN %s AND %s
          AND estado IN {estados}
    """
    cursor.execute(query_reservas, (f_inicio, f_fin))
    res_reservas = cursor.fetchone()

    total_reservas = res_reservas['total_reservas'] if res_reservas else 0
    total_cubiertos = res_reservas['total_cubiertos'] if res_reservas else 0

    # 3. Métrica: Precio promedio de la carta
    query_precio_promedio = "SELECT IFNULL(AVG(precio), 0) as promedio FROM menu"
    cursor.execute(query_precio_promedio)
    res_precio = cursor.fetchone()
    precio_promedio = float(res_precio['promedio']) if res_precio else 0.0

    ingreso_estimado = float(total_cubiertos) * precio_promedio

    # 4. Métrica: Plato estrella de la carta
    query_plato = "SELECT nombre FROM menu ORDER BY precio DESC LIMIT 1"
    cursor.execute(query_plato)
    res_plato = cursor.fetchone()
    plato_estrella = res_plato['nombre'] if res_plato else "No disponible"

    # 5. Métrica: Servicio extra más solicitado
    query_servicio = f"""
        SELECT 
            se.nombre,
            COUNT(*) as total_solicitudes
        FROM reserva_servicios rs
        INNER JOIN reservas r 
            ON rs.id_reserva = r.id_reserva
        INNER JOIN servicios_extra se 
            ON rs.id_servicio = se.id
        WHERE r.fecha_reserva BETWEEN %s AND %s
          AND r.estado IN {estados}
        GROUP BY se.id, se.nombre
        ORDER BY total_solicitudes DESC
        LIMIT 1
    """

    cursor.execute(query_servicio, (f_inicio, f_fin))
    res_servicio = cursor.fetchone()

    servicio_mas_solicitado = (
        res_servicio["nombre"]
        if res_servicio
        else "No disponible"
    )

    # 6. Tabla: Últimas 5 reservas uniendo la tabla 'usuarios' para sacar el nombre real
    query_ultimas = f"""
        SELECT 
            CONCAT(u.nombre, ' ', u.apellido) as cliente, 
            r.fecha_reserva, 
            r.hora_reserva, 
            r.cantidad_personas as comensales, 
            r.estado
        FROM reservas r
        INNER JOIN usuarios u ON r.id_usuario = u.id_usuario
        WHERE r.fecha_reserva BETWEEN %s AND %s
          AND r.estado IN {estados}
        ORDER BY r.fecha_reserva DESC, r.hora_reserva DESC
        LIMIT 10
    """
    cursor.execute(query_ultimas, (f_inicio, f_fin))
    res_ultimas = cursor.fetchall()

    # Formatear el resultado procesando los objetos de MySQL a strings limpios
    ultimas_reservas = []
    for r in res_ultimas:
        ultimas_reservas.append({
            "nombre_cliente": r["cliente"],
            "fecha": str(r["fecha_reserva"]),
            "hora": str(r["hora_reserva"])[:5] if r["hora_reserva"] else "00:00",
            "comensales": r["comensales"],
            "estado": r["estado"]
        })

    cursor.close()
    connection.close()

    # Estructura devuelta que encaja al 100% con tu frontend
    return {
        "fecha_analisis_inicio": f_inicio,
        "fecha_analisis_fin": f_fin,
        "resumen_operaciones": {
            "total_reservas_activas": total_reservas,
            "total_cubiertos_proyectados": int(total_cubiertos),
            "ingreso_estimado_ars": round(ingreso_estimado, 2)
        },
        "rendimiento_carta": {
            "plato_estrella": plato_estrella,
            "servicio_mas_solicitado": servicio_mas_solicitado
        },
        "ultimas_reservas": ultimas_reservas
    }