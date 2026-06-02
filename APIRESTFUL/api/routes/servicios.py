from flask import jsonify, request, Blueprint
#from api.db import get_connection #estaba antes
from api.utils import construir_error_api
from api.db_funciones import obtener_servicios_extra, actualizar_servicio_extra,eliminar_servicio_extra,agregar_servicio_extra, obtener_servicio_por_id


servicios_extra_bp= Blueprint("servicios_extra",__name__)


@servicios_extra_bp.route("/")
def obtener_servicios():
    servicios= obtener_servicios_extra()

    return jsonify(servicios),200
    


@servicios_extra_bp.route("/<int:id_servicio>", methods=['GET'])
def obtener_servicio_id(id_servicio):
    servicio= obtener_servicio_por_id(id_servicio)

    if servicio:
        return jsonify(servicio)
    return jsonify(construir_error_api(
        "SERVICE_NOT_FOUND",
        "Servicio inexistente",
        "No existe ningun servicio con el ID proporcionado")), 404



@servicios_extra_bp.route("/", methods=['POST'])
def agregar_servicio():
    data= request.json

    nombre= data.get("nombre")
    descripcion= data.get("descripcion")

    if not nombre or not descripcion:
     return jsonify(
         {"error": "Faltan datos"}
     ), 400

    servicio_nuevo= agregar_servicio_extra(nombre,descripcion)

    return jsonify({
    "mensaje": "Servicio agregado correctamente",
    "id_servicio": servicio_nuevo
    }), 201



@servicios_extra_bp.route("/<int:id_servicio>", methods=['PATCH'])
def actualizar_servicio(id_servicio):

    data= request.json

    nombre= data.get("nombre")
    descripcion= data.get("descripcion")

    if not nombre or not descripcion:
        return jsonify(
         construir_error_api(
             "INVALID_DATA",
             "Datos inválidos",
             "Debe enviar nombre y descripción"
         )
     ), 400
     

    servicio_actualizado= actualizar_servicio_extra(id_servicio,nombre,descripcion)

    if servicio_actualizado==0:
        return jsonify(construir_error_api("SERVICE_NOT_FOUND","Servicio inexistente","El servicio con el id porpocionado no existe")), 404
    return jsonify({'mensaje':'Servicio actualizado correctamente'}), 200



@servicios_extra_bp.route("/<int:id_servicio>",  methods=['DELETE'])
def eliminar_servicio(id_servicio):
    delete_servicio= eliminar_servicio_extra(id_servicio)

    if delete_servicio==0:
        return jsonify(construir_error_api("SERVICE_NOT_FOUND","Servicio inexistente","El servicio con el id porpocionado no existe")), 404
    return jsonify({'mensaje':'Servicio eliminado correctamente'}), 200

