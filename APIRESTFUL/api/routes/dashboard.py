from flask import Blueprint, request, jsonify
from api.validators.dashboard import validar_parametros_dashboard
from api.services.dashboard import obtener_metricas_dashboard

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    # 1. Enviar los argumentos de la URL al validador
    filtros, error = validar_parametros_dashboard(request.args)
    
    # Si la validación falló, responde con el formato de error estándar de utils.py
    if error:
        return jsonify(error), 400
        
    try:
        # 2. Obtener los resultados llamando directamente a la función
        respuesta = obtener_metricas_dashboard(filtros)
        return jsonify(respuesta), 200
        
    except Exception as e:
        return jsonify({
            "errors": [{
                "code": "internal.server.error",
                "message": "Error interno al procesar las metricas",
                "description": str(e)
            }]
        }), 500