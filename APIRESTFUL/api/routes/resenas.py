from flask import Blueprint, jsonify, request
from api.db_funciones import obtener_resenas, insertar_resena

resenas_bp = Blueprint("resenas", __name__)

@resenas_bp.route("/resenas", methods=["GET"])
def get_resenas():
    resenas = obtener_resenas()
    return jsonify(resenas), 200

@resenas_bp.route("/resenas", methods=["POST"])
def post_resena():
    data = request.get_json()
    insertar_resena(
        data['id_usuario'],
        data['id_reserva'],
        data['puntuacion'],
        data['comentario']
    )
    return jsonify({"mensaje": "Reseña creada"}), 201