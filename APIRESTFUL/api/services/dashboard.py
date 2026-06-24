from api.db import get_db_connection

def obtener_metricas_dashboard(filtros):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    f_inicio = filtros.get('fecha_inicio', '2026-05-01')
    f_fin = filtros.get('fecha_fin', '2026-05-31')
    incluir_canceladas = filtros.get('incluir_canceladas', False)
    
    page = int(filtros.get('page', 1))
    per_page = int(filtros.get('per_page', 10))
    offset = (page - 1) * per_page

    estados = "('confirmada', 'pendiente')"
    if incluir_canceladas:
        estados = "('confirmada', 'pendiente', 'cancelada')"

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

    total_paginas = (total_reservas + per_page - 1) // per_page if total_reservas > 0 else 1

    query_precio_promedio = "SELECT IFNULL(AVG(precio), 0) as promedio FROM menu"
    cursor.execute(query_precio_promedio)
    res_precio = cursor.fetchone()
    precio_promedio = float(res_precio['promedio']) if res_precio else 0.0

    ingreso_estimado = float(total_cubiertos) * precio_promedio

    query_plato = "SELECT nombre FROM menu ORDER BY precio DESC LIMIT 1"
    cursor.execute(query_plato)
    res_plato = cursor.fetchone()
    plato_estrella = res_plato['nombre'] if res_plato else "No disponible"

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
        LIMIT %s OFFSET %s
    """

    cursor.execute(query_ultimas, (f_inicio, f_fin, per_page, offset))
    res_ultimas = cursor.fetchall()

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

    return {
        "fecha_analisis_inicio": f_inicio,
        "fecha_analisis_fin": f_fin,
        "total_paginas": total_paginas,
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