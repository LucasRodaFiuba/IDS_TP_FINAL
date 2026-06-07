from flask import Blueprint, jsonify, request

from api.services.auth import (
    autenticar_usuario,
    registrar_usuario,
    solicitar_recuperacion_password,
)
from api.utils import construir_error_api


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/auth/register', methods=['POST'])
def post_register():
    body = request.get_json(silent=True)

    try:
        resultado = registrar_usuario(body)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400
        return jsonify(e.args[0]), status
    except Exception as e:
        return jsonify(construir_error_api(
            code='internal.server.error',
            message=str(e),
            description='Ocurrio un error inesperado en el registro de usuario'
        )), 500

    return jsonify(resultado), 201


@auth_bp.route('/auth/login', methods=['POST'])
def post_login():
    body = request.get_json(silent=True)

    try:
        resultado = autenticar_usuario(body)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400
        return jsonify(e.args[0]), status
    except Exception as e:
        return jsonify(construir_error_api(
            code='internal.server.error',
            message=str(e),
            description='Ocurrio un error inesperado en el login de usuario'
        )), 500

    return jsonify(resultado), 200


@auth_bp.route('/auth/forgot-password', methods=['POST'])
def post_forgot_password():
    body = request.get_json(silent=True)

    try:
        resultado = solicitar_recuperacion_password(body)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400
        return jsonify(e.args[0]), status
    except Exception as e:
        return jsonify(construir_error_api(
            code='internal.server.error',
            message=str(e),
            description='Ocurrio un error inesperado en la solicitud de recuperacion de password'
        )), 500

    return jsonify(resultado), 200
