from flask import Blueprint, jsonify, request
from ..utils import construir_error_api,validar_email
from ..services.reservas import (
    consultar_disponibilidad,
    crear_reserva,
    cambiar_reserva,
    cancelar_reserva_service,
    crear_reserva_admin,
    validar_reserva_service,
    obtener_reservas_segun_email,
    eliminar_reserva

)
from ..validators.reservas import validar_id

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

@reservas_bp.route('/reservas/<int:id>', methods = ['PUT'])
def modificar_reserva(id):
    #Valido id
    try:
        id = validar_id(id)
    except ValueError as e:
        return jsonify(e.args[0]), 400

    #se recibe un body
    body = request.get_json(silent = True)

    try:
        cambiar_reserva(id,body)
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

    return "", 204


@reservas_bp.route('/reservas/<int:id>', methods = ['POST'])
def cancelar_reserva(id):
    #Valido id
    try:
        id = validar_id(id)
    except ValueError as e:
        return jsonify(e.args[0]), 400

    #Cancelo la reserva
    try:
        cancelar_reserva_service(id)
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

    return "", 204

@reservas_bp.route("/reservas/validar/<token>")
def validar_reserva(token):
    # buscar reserva por token
    try:
        resultado = validar_reserva_service(token)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400
        return jsonify(e.args[0]), status
    except Exception as e:
        print("ERROR REAL:", e)
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

    return jsonify(resultado), 200

@reservas_bp.route('/reservas/usuario/<email>')
def obtener_reservas(email):
    """
    Devuelve todas las reservas de un usuario logeado
    """
    #validar email
    try:
        email = validar_email(email,"email")
    except ValueError as e:
        return jsonify(e.args[0]), 400

    #con el email consigo el id_usuario.
    try:
        resultado = obtener_reservas_segun_email(email)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400
        return jsonify(e.args[0]), status
    except Exception as e:
        print("ERROR REAL:", e)
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

    return jsonify(resultado), 200


@reservas_bp.route('/admin/reservas' , methods = ['POST'])
def agregar_reservar_admin():
    #obtengo el body completado por el usuario.
    body = request.get_json(silent=True)

    try:
        reserva = crear_reserva_admin(body)
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


@reservas_bp.route('/admin/reservas', methods = ['DELETE'])
def eliminar_reserva_admin():
    body = request.get_json(silent=True)

    if not body:
        return jsonify({"errors": [{"message": "Faltan datos"}]}), 400

    email = body.get('email')
    fecha_reserva = body.get('fecha_reserva')
    hora_reserva = body.get('hora_reserva')

    try:
        # Se las pasamos a la base de datos
        eliminar_reserva(email, fecha_reserva, hora_reserva)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400
        return jsonify(e.args[0]), status
    except Exception as e:
        return jsonify({'errors': [{'code': 'internal.server.error', 'message': str(e)}]}), 500

    return "", 204
