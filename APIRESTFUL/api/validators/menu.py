from api.utils import construir_error_api , validar_entero , validar_minimo
from flask import jsonify
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