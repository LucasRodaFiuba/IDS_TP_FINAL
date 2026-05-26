from flask import Blueprint, request, jsonify
from api.db import get_db_connection
from api.utils import construir_error_api
 
menu_bp = Blueprint('menu', __name__)
 
RESTRICCIONES_VALIDAS = {'vegetariano', 'vegano', 'sin_tacc', 'sin_lactosa', 'ninguno'}
CATEGORIAS_VALIDAS    = {'bebida', 'entrada', 'postre', 'plato_principal'}
 
@menu_bp.route('/menu', methods=['GET'])
def obtener_menu():
    try:
        restriccion = request.args.get('restriction', 'ninguno')
        try:
            limit  = int(request.args.get('_limit', 20))
            offset = int(request.args.get('_offset', 0))
        except(ValueError,TypeError):
            return jsonify(construir_error_api(
                code='invalid.pagination',
                message='Parámetros inválidos',
                description="Los campos '_limit' y '_offset' deben ser números enteros"
            )), 400
        
        if offset < 0:
               return jsonify(construir_error_api(
                code='invalid.pagination',
                message='Parámetros de paginacion invalidos',
                description='El offset no puede ser un numero negativo'
            )), 400
               
        if restriccion not in RESTRICCIONES_VALIDAS:
            return jsonify(construir_error_api(
                code='invalid.restriction',
                message='Parámetros invalidos',
                description=f"La restriccion'{restriccion}' es invalida, las restricciones validas: {', '.join(RESTRICCIONES_VALIDAS)}"
            )), 400
 
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
 
        if restriccion != 'ninguno':
            query = f"SELECT id_plato AS id, nombre, precio FROM menu WHERE {restriccion} = TRUE LIMIT %s OFFSET %s"
        else:
            query = "SELECT id_plato AS id, nombre, precio FROM menu LIMIT %s OFFSET %s"
 
        cursor.execute(query, (limit, offset))
        platos = cursor.fetchall()
 
        cursor.close()
        connection.close()
 
        if not platos:
            return '', 204
 
        return jsonify( {"platos": platos}), 200
 
    except Exception as e:
        return jsonify(construir_error_api(
            code='internal.server.error',
            message='Se produjo un error inesperado en el servidor',
            description=str(e)
        )), 500
        
@menu_bp.route('/menu/<string:categoria>', methods=['GET'])
def obtener_menu_por_categoria(categoria):
    try:
        if categoria not in CATEGORIAS_VALIDAS:
            return jsonify(construir_error_api(
                code='invalid.categoria',
                message='categoría invalida',
                description=f"La categoría '{categoria}' no existe, ejemplos de categorias: {', '.join(CATEGORIAS_VALIDAS)}"
            )), 404

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT id_plato AS id, nombre, precio FROM menu WHERE categoria = %s",
            (categoria,)
        )
        platos = cursor.fetchall()

        cursor.close()
        connection.close()

        if not platos:
            return '', 204

        return jsonify({"platos": platos}), 200

    except Exception as e:
        return jsonify(construir_error_api(
            code='internal.server.error',
            message='Se produjo un error inesperado en el servidor',
            description=str(e)
        )), 500
 
 
@menu_bp.route('/plato', methods=['POST'])
def crear_plato():
    try:
        data = request.get_json()
 
        if not data.get('nombre') or not data.get('descripcion') or not data.get('precio'):
            return jsonify(construir_error_api(
                code='invalid.request',
                message='Parámetros inválidos',
                description='Los campos nombre, descripcion y precio son obligatorios'
            )), 400
 
        if float(data['precio']) <= 0:
            return jsonify(construir_error_api(
                code='invalid.precio',
                message='Parámetros inválidos',
                description="El campo 'precio' debe ser mayor a 0"
            )), 400
            
        categoria = data.get('categoria', None)
        if not categoria or categoria not in CATEGORIAS_VALIDAS:
            return jsonify(construir_error_api(
                code='invalid.categoria',
                message='categoria invalida',
                description=f"El campo categoria es obligatorio, ejemplos de categorias : {', '.join(CATEGORIAS_VALIDAS)}"
            )), 400
    
        restriccion = data.get('restriccion', 'ninguno')
        if restriccion not in RESTRICCIONES_VALIDAS:
            return jsonify(construir_error_api(
                code='invalid.restriction',
                message='Parámetros invalidos.',
                description=f"La restriccion'{restriccion}' es invalida, las restricciones validas: {', '.join(RESTRICCIONES_VALIDAS)}"
            )), 400
 
        
        vegetariano = restriccion == 'vegetariano'
        vegano      = restriccion == 'vegano'
        sin_tacc    = restriccion == 'sin_tacc'
        sin_lactosa = restriccion == 'sin_lactosa'
 
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
 
        cursor.execute("SELECT id_plato FROM menu WHERE nombre = %s", (data['nombre'],))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify(construir_error_api(
                code='conflict.nombre',
                message='Parametro ingresados ya consta en la base de datos ',
                description=f"Ya existe un plato con el nombre '{data['nombre']}'"
            )), 409
 
        cursor.execute("""
            INSERT INTO menu (nombre, descripcion, precio, vegetariano, vegano, sin_tacc, sin_lactosa, categoria)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (data['nombre'], data['descripcion'], float(data['precio']), vegetariano, vegano, sin_tacc, sin_lactosa, categoria))
 
        connection.commit()
        cursor.close()
        connection.close()
 
        return '', 201
    
    except Exception as e:
        return jsonify(construir_error_api(
            code='internal.server.error',
            message='Se produjo un error inesperado en el servidor',
            description=str(e)
        )), 500

@menu_bp.route('/plato/<int:id>', methods=['GET'])
def obtener_plato_por_id(id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM menu WHERE id_plato = %s", (id,))
        plato = cursor.fetchone()

        cursor.close()
        connection.close()

        if not plato:
            return jsonify(construir_error_api(
                code='not.found',
                message='No fue encontrada en nuestra base de datos',
                description=f'No existe ningún plato con id {id}'
            )), 404

        return jsonify(plato), 200

    except Exception as e:
        return jsonify(construir_error_api(
            code='internal.server.error',
            message='Se produjo un error inesperado en el servidor',
            description=str(e)
        )), 500


@menu_bp.route('/plato/<int:id>', methods=['PUT'])
def actualizar_plato(id):
    try:
        data = request.get_json()

        if not data.get('nombre') or not data.get('descripcion') or not data.get('precio'):
            return jsonify(construir_error_api(
                code='invalid.request',
                message='Parámetros inválidos',
                description='Los campos nombre, descripcion y precio son obligatorios'
            )), 400

        if float(data['precio']) <= 0:
            return jsonify(construir_error_api(
                code='invalid.precio',
                message='Parámetros inválidos',
                description="El campo 'precio' debe ser mayor a 0"
            )), 400
            
        categoria = data.get('categoria', None)
        if not categoria or categoria not in CATEGORIAS_VALIDAS:
            return jsonify(construir_error_api(
                code='invalid.categoria',
                message='Parámetros inválidos',
                description=f"El campo categoria es obligatorio, ejemplos de categorias : {', '.join(CATEGORIAS_VALIDAS)}"
            )), 400
            
        restriccion = data.get('restriccion', 'ninguno')
        if restriccion not in RESTRICCIONES_VALIDAS:
            return jsonify(construir_error_api(
                code='invalid.restriction',
                message='Parámetros invalidos.',
                description=f"La restriccion'{restriccion}' es invalida, las restricciones validas: {', '.join(RESTRICCIONES_VALIDAS)}"
            )), 400

        vegetariano = restriccion == 'vegetariano'
        vegano      = restriccion == 'vegano'
        sin_tacc    = restriccion == 'sin_tacc'
        sin_lactosa = restriccion == 'sin_lactosa'

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT id_plato FROM menu WHERE id_plato = %s", (id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify(construir_error_api(
                code='not.found',
                message='No fue encontrada en nuestra base de datos',
                description=f'No existe ningún plato con id {id}'
            )), 404

        cursor.execute("""
            UPDATE menu
            SET nombre = %s, descripcion = %s, precio = %s, vegetariano = %s, vegano = %s, sin_tacc = %s, sin_lactosa = %s, categoria = %s
            WHERE id_plato = %s
        """, (data['nombre'], data['descripcion'], float(data['precio']), vegetariano, vegano, sin_tacc, sin_lactosa, categoria, id ))

        connection.commit()
        cursor.close()
        connection.close()

        return '', 204

    except Exception as e:
        return jsonify(construir_error_api(
            code='internal.server.error',
            message='Se produjo un error inesperado en el servidor',
            description=str(e)
        )), 500

@menu_bp.route('/plato/<int:id>', methods=['PATCH'])
def actualizar_parcialmente_plato(id):
    try:
        data = request.get_json()

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM menu WHERE id_plato = %s", (id,))
        plato = cursor.fetchone()

        if not plato:
            cursor.close()
            connection.close()
            return jsonify(construir_error_api(
                code='not.found',
                message='No fue encontrada en nuestra de base de datos',
                description=f'No existe ningún plato con id {id}'
            )), 404

        nombre      = data.get('nombre',      plato['nombre'])
        descripcion = data.get('descripcion', plato['descripcion'])
        precio      = float(data.get('precio', plato['precio']))
        categoria = data.get('categoria', plato['categoria'])
        restriccion = data.get('restriccion', None)

        if precio <= 0:
            return jsonify(construir_error_api(
                code='invalid.precio',
                message='Parámetros inválidos.',
                description="El campo 'precio' debe ser mayor a 0"
            )), 400
    
        if categoria not in CATEGORIAS_VALIDAS:
            return jsonify(construir_error_api(
                code='invalid.categoria',
                message='categoria invalida',
                description=f"El campo categoria es obligatorio, ejemplos de categorias : {', '.join(CATEGORIAS_VALIDAS)}"
            )), 400
            
        if restriccion:
            if restriccion not in RESTRICCIONES_VALIDAS:
                return jsonify(construir_error_api(
                    code='invalid.restriccion',
                    message='Parámetros inválidos.',
                    description=f"La restriccion'{restriccion}' es invalida, las restricciones validas: {', '.join(RESTRICCIONES_VALIDAS)}"
                )), 400
            vegetariano = restriccion == 'vegetariano'
            vegano      = restriccion == 'vegano'
            sin_tacc    = restriccion == 'sin_tacc'
            sin_lactosa = restriccion == 'sin_lactosa'
        else:
            vegetariano = plato['vegetariano']
            vegano      = plato['vegano']
            sin_tacc    = plato['sin_tacc']
            sin_lactosa = plato['sin_lactosa']

        cursor.execute("""
            UPDATE menu
            SET nombre = %s, descripcion = %s, precio = %s,
                vegetariano = %s, vegano = %s, sin_tacc = %s, sin_lactosa = %s, categoria= %s
            WHERE id_plato = %s
        """, (nombre, descripcion, precio, vegetariano, vegano, sin_tacc, sin_lactosa, categoria, id))

        connection.commit()
        cursor.close()
        connection.close()

        return '', 204

    except Exception as e:
        return jsonify(construir_error_api(
            code='internal.server.error',
            message='Se produjo un error inesperado en el servidor',
            description=str(e)
        )), 500

@menu_bp.route('/plato/<int:id>', methods=['DELETE'])
def eliminar_plato(id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT id_plato FROM menu WHERE id_plato = %s", (id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify(construir_error_api(
                code='not.found',
                message='No fue encontrada en nuestra de base de datos',
                description=f'No existe ningún plato con id {id}'
            )), 404

        cursor.execute("DELETE FROM menu WHERE id_plato = %s", (id,))
        connection.commit()

        cursor.close()
        connection.close()

        return '', 204

    except Exception as e:
        return jsonify(construir_error_api(
            code='internal.server.error',
            message='Se produjo un error inesperado en el servidor',
            description=str(e)
        )), 500
