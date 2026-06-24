from flask import Flask, Blueprint, render_template, request, redirect, url_for,flash, session
from services.mis_reservas import obtener_reservas,cancelar_reserva_service
from datetime import datetime
from constants import MESES

mis_reservas_bp = Blueprint('mis_reservas', __name__)

@mis_reservas_bp.route('/mis_reservas', methods=['GET'])
def pagina_mis_reservas():
    #Obtengo email logeado
    usuario = session.get("usuario")

    if not usuario:
        flash("Tenés que iniciar sesión primero", "error")
        return redirect(url_for("auth.iniciar_sesion"))

    email = usuario.get("email")

    if not email:
        flash("Tenés que iniciar sesión primero", "error")
        return redirect(url_for("auth.iniciar_sesion"))

    #uso services para realizar la conexión con el backend.
    resultado = obtener_reservas(email)
    
    if resultado.get("ok"):
        flash("Reservas obtenidas", "success")
        reservas = resultado['response']

        #Agrego dos campos para mostrar en el frontend el mes y el dia.
        for reserva in reservas:
            fecha = datetime.strptime(reserva['fecha_reserva'], "%Y-%m-%d")
            reserva['mes_abreviado'] = MESES[fecha.month - 1]
            reserva['dia'] = fecha.day

        return render_template("mis_reservas.html",reservas=resultado['response'])
        
    errores = resultado.get("errores", [])
    
    for e in errores:
        flash(e, "error")

    return render_template("mis_reservas.html", reservas=None)

@mis_reservas_bp.route('/cancelar_reserva/<int:id_reserva>', methods=['POST'])
def cancelar_reserva(id_reserva):
    cancelar_reserva_service(id_reserva)
    return redirect(url_for("mis_reservas.pagina_mis_reservas"))
