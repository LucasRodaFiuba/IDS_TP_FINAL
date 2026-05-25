from flask import Blueprint, jsonify, request
from ..utils import construir_error_api
from ..services.reservas import (
    consultar_disponibilidad,
    crear_reserva
)

reservas_bp = Blueprint('reservas', __name__)

@reservas_bp.route('/reservas/disponibilidad', methods = ['GET'])
def obtener_turnos_disponibles():
    #Obtengo los dos paŕametros completados por el usuario
    fecha = request.args.get('fecha')
    comensales = request.args.get('comensales',type=int)

    try:
        turnos_disponibles = consultar_disponibilidad(fecha,comensales)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400
        return jsonify(e.args[0]), status
    except Exception as e:
        return jsonify({
            'errors': [
                {
                    'code': 'internal.server.error',
                    'message': str(e),
                    'description': 'Ocurrio un error inesperado, estoy en routes'
                }
            ]
        }), 500

    return jsonify(turnos_disponibles), 200

@reservas_bp.route('/reservas' , methods = ['POST'])
def agregar_reservar():
    #obtengo el body completado por el usuario.
    body = request.get_json(silent=True)

    try:
        reserva = crear_reserva(body)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400
        return jsonify(e.args[0]), status
    except Exception as e:
        #Para cualquier error inesperado del servidor.
        return jsonify({
            'errors': [
                {
                    'code': 'internal.server.error',
                    'message': str(e),
                    'description': 'Ocurrio un error inesperado, estoy en routes'
                }
            ]
        }), 500

    return jsonify(reserva), 201
