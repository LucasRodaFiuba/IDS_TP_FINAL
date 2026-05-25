from flask import Blueprint, request, jsonify
from api.db import get_db_connection
from api.utils import construir_error_api
 
menu_bp = Blueprint('menu', __name__)
 
RESTRICCIONES_VALIDAS = {'vegetariano', 'vegano', 'sin_tacc', 'sin_lactosa', 'ninguno'}
 
@menu_bp.route('/menu', methods=['GET'])
def obtener_menu():
    try:
        restriccion = request.args.get('restriction', 'ninguno')
        limit  = request.args.get('_limit', 10)
        offset = request.args.get('_offset', 0)
 
        if restriccion not in RESTRICCIONES_VALIDAS:
            return jsonify(construir_error_api(
                code='invalid.restriction',
                message='Parámetros invalifos.',
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
            message='Se produjo un error inesperado en el servidor.',
            description=str(e)
        )), 500
 
 
@menu_bp.route('/plato', methods=['POST'])
def crear_plato():
    try:
        data = request.get_json()
 
        if not data.get('nombre') or not data.get('descripcion') or not data.get('precio'):
            return jsonify(construir_error_api(
                code='bad.request',
                message='Parámetros inválidos',
                description='Los campos nombre, descripcion y precio son obligatorios'
            )), 400
 
        if float(data['precio']) <= 0:
            return jsonify(construir_error_api(
                code='invalid.precio',
                message='Parámetros inválidos',
                description="El campo 'precio' debe ser mayor a 0"
            )), 400
 
        restriccion = data.get('restriccion', 'ninguno')
        if restriccion not in RESTRICCIONES_VALIDAS:
            return jsonify(construir_error_api(
                code='invalid.restriccion',
                message='Parámetros inválidos',
                description=f"La restriccion'{restriccion}' no es válida,las restricciones validas son :{', '.join(RESTRICCIONES_VALIDAS)}"
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
            INSERT INTO menu (nombre, descripcion, precio, vegetariano, vegano, sin_tacc, sin_lactosa)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (data['nombre'], data['descripcion'], float(data['precio']), vegetariano, vegano, sin_tacc, sin_lactosa))
 
        connection.commit()
        cursor.close()
        connection.close()
 
        return '', 201
 
    except Exception as e:
        return jsonify(construir_error_api(
            code='internal.server.error',
            message='Error inesperado en el servidor',
            description=str(e)
        )), 500
 