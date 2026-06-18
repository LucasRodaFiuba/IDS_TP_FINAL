from sqlalchemy.exc import IntegrityError
from api import db_funciones
from api.utils import construir_error_api


def construir_usuario_dto(usuario):
    nombre_completo = f"{usuario.get('nombre', '')} {usuario.get('apellido', '')}".strip()
    return {
        'id': usuario['id_usuario'],
        'nombre': nombre_completo,
        'email': usuario['email'],
        'rol': usuario['rol'],
    }


def puede_operar_sobre_usuario(usuario_actual, id_usuario):
    return (
        usuario_actual.get('rol') == 'admin'
        or str(usuario_actual.get('sub')) == str(id_usuario)
    )


def obtener_perfil_usuario(id_usuario):
    usuario = db_funciones.obtener_usuario_publico_por_id(id_usuario)

    if not usuario:
        raise ValueError(construir_error_api(
            code='usuario.not.found',
            message='Usuario no encontrado',
            description=f"No existe un usuario con id '{id_usuario}'"
        ), 404)

    reservas = db_funciones.obtener_reservas_de_usuario(id_usuario)

    return {
        'usuario': {
            'id': usuario['id_usuario'],
            'nombre': usuario['nombre'],
            'apellido': usuario['apellido'],
            'email': usuario['email'],
            'telefono': usuario['telefono'],
            'fecha_registro': usuario['fecha_registro'].isoformat() if usuario['fecha_registro'] else None,
            'rol': usuario['rol'],
        },
        'reservas': [
            {
                'id': reserva['id_reserva'],
                'numero_mesa': reserva['numero_mesa'],
                'fecha': reserva['fecha_reserva'].isoformat() if reserva['fecha_reserva'] else None,
                'hora': str(reserva['hora_reserva']) if reserva['hora_reserva'] else None,
                'comensales': reserva['cantidad_personas'],
                'estado': reserva['estado'],
                'codigo_qr': reserva['codigo_qr'],
                'fecha_creacion': reserva['fecha_creacion'].isoformat() if reserva['fecha_creacion'] else None,
            }
            for reserva in reservas
        ],
    }


def eliminar_usuario_por_id(id_usuario):
    usuario = db_funciones.obtener_usuario_publico_por_id(id_usuario)

    if not usuario:
        raise ValueError(construir_error_api(
            code='usuario.not.found',
            message='Usuario no encontrado',
            description=f"No existe un usuario con id '{id_usuario}'"
        ), 404)

    try:
        db_funciones.eliminar_usuario_por_id(id_usuario)
    except IntegrityError:
        raise ValueError(construir_error_api(
            code='usuario.delete.bad_request',
            message='No se puede eliminar el usuario',
            description='El usuario tiene datos relacionados, por ejemplo reservas o resenas. Para borrado real hace falta definir una politica de baja logica o cascada.'
        ), 400)

def obtener_usuarios():
    lista_usuarios = db_funciones.obtener_usuarios()
    datos = [construir_usuario_dto(usuario) for usuario in lista_usuarios]
    return {"usuarios": datos}
