from api.utils import construir_error_api , validar_entero , validar_minimo
from flask import jsonify
 
 
def validar_paginacion(limit, offset):
    try:
        limit  = int(limit)
        offset = int(offset)
    except (ValueError, TypeError):
        raise ValueError(construir_error_api(
            code='invalid.pagination',
            message='Parámetros inválidos',
            description="Los campos '_limit' y '_offset' deben ser números enteros"
        ))

    if offset < 0:
        raise ValueError(construir_error_api(
            code='invalid.pagination',
            message='Parámetros de paginacion invalidos',
            description='El offset no puede ser un numero negativo'
        ))

    return limit, offset
 
def validar_precio(precio):
    try:
        precio = float(precio)
    except (ValueError, TypeError):
        raise ValueError(construir_error_api(
            code='invalid.precio',
            message='Parámetros inválidos',
            description="El campo 'precio' debe ser un número válido"
        ))

    validar_minimo(precio, 0.01, 'precio')
    return precio

def validar_id(valor):
    if not valor:
        raise ValueError(construir_error_api(
            code='required.id',
            message='Parámetros inválidos',
            description="El campo 'id' es obligatorio"
        ))
    return validar_entero(valor, 'id')