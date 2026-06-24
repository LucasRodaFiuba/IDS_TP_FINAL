from api.utils import (
    validar_string_no_vacio, 
    validar_formato_fecha_o_horario, 
    construir_error_api
)
from datetime import datetime

def validar_parametros_dashboard(args):
    """
    Valida los query params del dashboard.
    Retorna una tupla (datos_validados, error_dict). Si hay error, datos_validados es None.
    """
    try:
        # 1. Validar presencia de campos obligatorios
        fecha_inicio_raw = validar_string_no_vacio(args.get('fecha_inicio'), 'fecha_inicio')
        fecha_fin_raw = validar_string_no_vacio(args.get('fecha_fin'), 'fecha_fin')
        
        # 2. Validar formato correcto YYYY-MM-DD
        f_inicio = validar_formato_fecha_o_horario(fecha_inicio_raw, '%Y-%m-%d', 'fecha_inicio')
        f_fin = validar_formato_fecha_o_horario(fecha_fin_raw, '%Y-%m-%d', 'fecha_fin')
        
        # 3. Lógica de negocio: Inicio no puede ser mayor que fin
        if f_inicio > f_fin:
            return None, construir_error_api(
                code='invalid.date.range',
                message='Rango de fechas invalido',
                description='La fecha_inicio no puede ser posterior a la fecha_fin'
            )
            
        # Parámetros opcionales
        restriccion = args.get('restriccion_popular', 'ninguno')
        incluir_canceladas = args.get('incluir_canceladas', 'false').lower() == 'true'
        
        try:
            page = int(args.get('page', 1))
            if page < 1:
                page = 1
        except (ValueError, TypeError):
            page = 1

        try:
            per_page = int(args.get('per_page', 10))
            if per_page < 1:
                per_page = 10
        except (ValueError, TypeError):
            per_page = 10
        
        return { 'fecha_inicio': fecha_inicio_raw, 'fecha_fin': fecha_fin_raw, 'restriccion': restriccion, 'incluir_canceladas': incluir_canceladas, 'page': page,}, None

    except ValueError as e:
        return None, e.args[0]