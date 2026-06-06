from flask import Blueprint, request, jsonify
from api.db import get_db_connection
from api.utils import construir_error_api
from ..constantes import RESTRICCIONES_VALIDAS, CATEGORIAS_VALIDAS
 
menu_bp = Blueprint('menu', __name__)
 

@menu_bp.route('/menu', methods=['GET'])
def obtener_menu():
    try:
        restriccion = request.args.get('restriccion', 'ninguno')
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
            query = f"SELECT id_plato AS id, nombre, precio, descripcion, categoria, restriccion, imagen FROM menu WHERE restriccion = %s LIMIT %s OFFSET %s"
            cursor.execute(query, (restriccion, limit, offset))
        else:
            query = "SELECT id_plato AS id, nombre, precio, descripcion, categoria, restriccion, imagen FROM menu LIMIT %s OFFSET %s"
            cursor.execute(query, (limit, offset))
     
        platos = cursor.fetchall()
        cursor.close()
        connection.close()
        
        if not platos:
            return '', 204

        resultado = [
        {
            "id": p["id"],
            "nombre": p["nombre"],
            "descripcion": p["descripcion"],
            "precio": p["precio"],
            "restriccion":p["restriccion"],
            "categoria":p["categoria"],
            "imagen":p["imagen"]
            
        }
        for p in platos
        ]
        return jsonify({"platos": resultado}), 200
       
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
        imagen= data.get('imagen', None)
        
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
            )), 400
 
        cursor.execute("""
            INSERT INTO menu (nombre, descripcion, precio, restriccion, categoria, imagen)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (data['nombre'], data['descripcion'], float(data['precio']), restriccion , categoria, imagen))
 
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

@menu_bp.route('/menu/plato/<int:id>', methods=['GET'])
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

@menu_bp.route('/admin/plato/actualizar', methods=['PATCH'])
def actualizar_parcialmente_plato():
    try:
        data = request.get_json()
        id = data.get('id')
        
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
        nombre      = data.get('nombre')      or plato['nombre']
        descripcion = data.get('descripcion') or plato['descripcion']
        precio      = float(data.get('precio'))
        restriccion = data.get('restriccion') or plato['restriccion']
        categoria   = data.get('categoria')   or plato['categoria']
        imagen      = data.get('imagen')      or plato['imagen']

        if precio <= 0:
            return jsonify(construir_error_api(
                code='invalid.precio',
                message='Parámetros inválidos.',
                description="El campo 'precio' debe ser mayor a 0"
            )), 400
        if precio == None:
            precio = plato['precio']
        else:
            precio = float(precio)
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
        query = "UPDATE menu SET nombre = %s, descripcion = %s, precio = %s, restriccion = %s, categoria = %s WHERE id_plato = %s"
        cursor.execute(query, (nombre, descripcion, precio, restriccion, categoria, id))

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

@menu_bp.route('/menu/plato/eliminar', methods=['DELETE'])
def eliminar_plato():
    nombre = request.json.get('nombre') 

    if not nombre:
        return jsonify(construir_error_api(
            code='bad.request',
            message='El nombre es obligatorio',
            description='Debe enviar el nombre del plato'
        )), 400
    try:
        
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT nombre FROM menu WHERE nombre = %s", (nombre,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify(construir_error_api(
                code='not.found',
                message='No fue encontrada en nuestra de base de datos',
                description=f'No existe ningún plato con ese nombre {nombre}'
            )), 404

        cursor.execute("DELETE FROM menu WHERE nombre = %s", (nombre,))
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