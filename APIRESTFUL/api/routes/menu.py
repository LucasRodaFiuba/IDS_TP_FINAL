from flask import Blueprint, request, jsonify
from api.utils import construir_error_api, validar_string_no_vacio, validar_entero
from api.validators.menu import validar_paginacion, validar_precio,validar_id
from api.services.menu import obtener_platos, obtener_plato_por_nombre, obtener_plato_por_id,actualizar_plato, insertar_plato, eliminar_plato_por_nombre
from ..constantes import RESTRICCIONES_VALIDAS, CATEGORIAS_VALIDAS
 
menu_bp = Blueprint('menu', __name__)
 

@menu_bp.route('/menu', methods=['GET'])
def obtener_menu():
    try:
        try:
            limit, offset = validar_paginacion(
                request.args.get('_limit', 20),
                request.args.get('_offset', 0)
            )
        except ValueError as e:
            return jsonify(e.args[0]), 400
    
        platos = obtener_platos(limit, offset)
        if not platos:
            return '', 204
 
        return jsonify({"platos": platos}), 200
 
    except Exception as e:
        return jsonify(construir_error_api(
            code='internal.server.error',
            message='Se produjo un error inesperado en el servidor',
            description=str(e)
        )), 500
         
@menu_bp.route('/admin/plato', methods=['POST'])
def crear_plato():
    try:
        data = request.get_json()

        try:
            nombre      = validar_string_no_vacio(data.get('nombre'), 'nombre')
            descripcion = validar_string_no_vacio(data.get('descripcion'), 'descripcion')
            precio      = validar_precio(data.get('precio'))
        except ValueError as e:
            return jsonify(e.args[0]), 400

        if obtener_plato_por_nombre(nombre):
            return jsonify(construir_error_api(
                code='conflict.nombre',
                message='Ya existe',
                description=f"Ya existe un plato con el nombre '{nombre}'"
            )), 409

        insertar_plato(
            nombre,
            descripcion,
            precio,
            data.get('restriccion'),
            data.get('categoria'),
            data.get('imagen', None)
        )
        return '', 201

    except Exception as e:
        return jsonify(construir_error_api(
            code='internal.server.error',
            message='Se produjo un error inesperado en el servidor',
            description=str(e)
        )), 500
        
        
@menu_bp.route('/admin/plato/actualizar', methods=['PATCH'])
def actualizar_parcialmente_plato():
    try:
        data = request.get_json()
        try:
            id = validar_id(data.get('id'))
        except ValueError as e:
            return jsonify(e.args[0]), 400

        plato = obtener_plato_por_id(id)
        if not plato:
            return jsonify(construir_error_api(
                code='not.found',
                message='No fue encontrada en nuestra base de datos',
                description=f"No existe ningún plato con id {id}"
            )), 404

        nuevo_precio = data.get('precio')
        if nuevo_precio is not None:
            try:
                precio = validar_precio(nuevo_precio)
            except ValueError as e:
                return jsonify(e.args[0]), 400
        else:
            precio = plato['precio']

        actualizar_plato(
            plato['id_plato'],
            data.get('nombre')      or plato['nombre'],
            data.get('descripcion') or plato['descripcion'],
            precio,
            data.get('restriccion') or plato['restriccion'],
            data.get('categoria')   or plato['categoria'],
            data.get('imagen')      or plato['imagen']
        )
        return '', 204

    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify(construir_error_api(
            code='internal.server.error',
            message='Se produjo un error inesperado en el servidor',
            description=str(e)
        )), 500

@menu_bp.route('/menu/plato/eliminar', methods=['DELETE'])
def eliminar_plato():
    try:
        data = request.get_json()
        
        try:
            nombre = validar_string_no_vacio(data.get('nombre'), 'nombre')
        except ValueError as e:
            return jsonify(e.args[0]), 400

        if not obtener_plato_por_nombre(nombre):
            return jsonify(construir_error_api(
                code='not.found',
                message='No fue encontrada en nuestra base de datos',
                description=f'No existe ningún plato con ese nombre {nombre}'
            )), 404

        eliminar_plato_por_nombre(nombre)
        return '', 204

    except Exception as e:
        return jsonify(construir_error_api(
            code='internal.server.error',
            message='Se produjo un error inesperado en el servidor',
            description=str(e)
        )), 500