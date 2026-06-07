from flask import Blueprint, jsonify

from api.db_funciones import obtener_resenas

resenas_bp = Blueprint(
    "resenas",
    __name__
)

@resenas_bp.route(
    "/resenas",
    methods=["GET"]
)
def get_resenas():

    resenas = obtener_resenas()

    return jsonify(resenas), 200