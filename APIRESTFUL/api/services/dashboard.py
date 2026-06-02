from api.db import get_db_connection

def obtener_metricas_dashboard(filtros):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    f_inicio = filtros['fecha_inicio']
    f_fin = filtros['fecha_fin']
    incluir_canceladas = filtros['incluir_canceladas']
    restriccion = filtros['restriccion']

    # 1. Definir estados a considerar para las métricas
    estados = "('confirmada', 'pendiente', 'finalizada')"
    if incluir_canceladas:
        estados = "('confirmada', 'pendiente', 'finalizada', 'cancelada')"

    # Query para totalizar reservas y cubiertos (cantidad de personas)
    query_reservas = f"""
        SELECT 
            COUNT(*) as total_reservas,
            SUM(cantidad_personas) as total_cubiertos
        FROM reservas
        WHERE fecha_reserva BETWEEN %s AND %s
          AND estado IN {estados}
    """
    cursor.execute(query_reservas, (f_inicio, f_fin))
    res_reservas = cursor.fetchone()

    total_reservas = res_reservas['total_reservas'] or 0
    total_cubiertos = res_reservas['total_cubiertos'] or 0

    # 2. Calcular ingreso estimado basado en el precio promedio de la carta
    query_precio_promedio = "SELECT AVG(precio) as promedio FROM menu"
    cursor.execute(query_precio_promedio)
    res_precio = cursor.fetchone()
    precio_promedio = float(res_precio['promedio'] or 0)

    ingreso_estimado = total_cubiertos * precio_promedio

    # 3. Determinar el plato estrella filtrado por restricción alimenticia (si aplica)
    where_restriccion = ""
    if restriccion in ['vegetariano', 'vegano', 'sin_tacc', 'sin_lactosa']:
        where_restriccion = f"WHERE {restriccion} = TRUE"

    # Como no hay detalle de pedidos, selecciona de forma simulada el plato más representativo/caro de esa sección
    query_plato = f"""
        SELECT nombre FROM menu 
        {where_restriccion} 
        ORDER BY precio DESC 
        LIMIT 1
    """
    cursor.execute(query_plato)
    res_plato = cursor.fetchone()
    plato_estrella = res_plato['nombre'] if res_plato else "No disponible"

    cursor.close()
    connection.close()

    # Retorna la estructura para el frontend
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
            "servicio_mas_solicitado": "Maridaje Exclusivo con Sommelier"
        }
    }