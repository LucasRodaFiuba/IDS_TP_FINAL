from flask import Blueprint, jsonify, request
from api.services.auth import requiere_auth
from api.services.usuarios import (
    eliminar_usuario_por_id,
    obtener_perfil_usuario,
    puede_operar_sobre_usuario,
    obtener_usuarios,
    agregar_usuario,
    cambiar_rol,
)
from api.utils import (
    construir_error_api,
    validar_entero,
    validar_minimo,
)


usuarios_bp = Blueprint('usuarios', __name__)


def _validar_id_usuario(id_usuario):
    id_validado = validar_entero(id_usuario, 'id')
    return validar_minimo(id_validado, 1, 'id')

@usuarios_bp.route('/usuarios', methods=['POST'])
def crear_usuario():
    data = request.get_json()

    if not data:
        return jsonify(construir_error_api(
            code='invalid.request',
            message='Datos JSON faltantes',
            description='Se esperaba un cuerpo JSON con los datos del usuario'
        )), 400

    try:
        nuevo_usuario = agregar_usuario(data)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400
        return jsonify(e.args[0]), status
    except Exception as e:
        return jsonify(construir_error_api(
            code='internal.server.error',
            message=str(e),
            description='Ocurrio un error inesperado al crear el usuario'
        )), 500

    return jsonify(nuevo_usuario), 201

@usuarios_bp.route('/usuarios/<id_usuario>', methods=['GET'])
@requiere_auth()
def get_usuario(id_usuario):
    try:
        id_validado = _validar_id_usuario(id_usuario)
    except ValueError as e:
        return jsonify(e.args[0]), 400

    if not puede_operar_sobre_usuario(request.usuario_actual, id_validado):
        return jsonify(construir_error_api(
            code='auth.forbidden',
            message='Permisos insuficientes',
            description='Solo puede consultar su propio perfil, salvo que sea administrador'
        )), 403

    try:
        perfil = obtener_perfil_usuario(id_validado)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400
        return jsonify(e.args[0]), status
    except Exception as e:
        return jsonify(construir_error_api(
            code='internal.server.error',
            message=str(e),
            description='Ocurrio un error inesperado al consultar el perfil de usuario'
        )), 500

    return jsonify(perfil), 200


@usuarios_bp.route('/usuarios/<id_usuario>', methods=['DELETE'])
@requiere_auth()
def delete_usuario(id_usuario):
    try:
        id_validado = _validar_id_usuario(id_usuario)
    except ValueError as e:
        return jsonify(e.args[0]), 400

    if not puede_operar_sobre_usuario(request.usuario_actual, id_validado):
        return jsonify(construir_error_api(
            code='auth.forbidden',
            message='Permisos insuficientes',
            description='Solo puede eliminar su propia cuenta, salvo que sea administrador'
        )), 403

    try:
        eliminar_usuario_por_id(id_validado)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400
        return jsonify(e.args[0]), status
    except Exception as e:
        return jsonify(construir_error_api(
            code='internal.server.error',
            message=str(e),
            description='Ocurrio un error inesperado al eliminar el usuario'
        )), 500

    return '', 204


@usuarios_bp.route ('/admin/usuarios', methods=['GET'])
def admin_get_usuarios():

    try:
        usuarios = obtener_usuarios()
    except Exception as e:
        return jsonify(construir_error_api(
            code='internal.server.error',
            message=str(e),
            description='Ocurrio un error inesperado al obtener la lista de usuarios'
        )), 500

    return jsonify(usuarios), 200

@usuarios_bp.route ('/admin/usuarios/actualizar_rol/<int:id_usuario>', methods=['PUT'])
def cambiar_rol_usuario(id_usuario):
    try:
        id_validado = _validar_id_usuario(id_usuario)
    except ValueError as e:
        return jsonify(e.args[0]), 400

    try:
        cambiar_rol(id_validado)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400
        return jsonify(e.args[0]), status
    except Exception as e:
        return jsonify(construir_error_api(
            code='internal.server.error',
            message=str(e),
            description='Ocurrio un error inesperado al cambiar rol del usuario'
        )), 500
    

    return{'mensaje': 'Rol actualizado'}, 200