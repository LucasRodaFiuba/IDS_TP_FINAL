from flask import Flask, Blueprint, render_template, request, redirect, url_for,flash, session
from services.reservas import enviar_reserva, eliminar_reserva, obtener_disponibilidad
from services.servicios_extra import obtener_servicios_extra

reservas_bp = Blueprint('reservas', __name__)

@reservas_bp.route('/reservas', methods=['GET', 'POST'])
def pagina_reservas():

    usuario = session.get("usuario")

    if not usuario:
        flash("Tenés que iniciar sesión primero", "error")
        return redirect(url_for("auth.iniciar_sesion"))

    email = usuario.get("email")

    if not email:
        flash("Tenés que iniciar sesión primero", "error")
        return redirect(url_for("auth.iniciar_sesion"))

    if request.method == 'POST':
        data = request.form.to_dict()
        data['servicios_extras'] = request.form.getlist('servicios_extras')
        resultado = enviar_reserva(data)

        if resultado.get('ok'):
            flash("¡Tu reserva en Le Maison Gourmet ha sido registrada con éxito!", "success")
            return redirect(url_for('mis_reservas.pagina_mis_reservas'))
        else:
            errores = resultado.get('errores', ['Error desconocido al procesar la reserva.'])
            for e in errores:
                flash(f"Hubo un problema: {e}", "error")
            return redirect(url_for('reservas.pagina_reservas'))
    

    fecha_seleccionada = request.args.get('fecha')
    comensales = request.args.get('comensales')
    
    horarios_disponibles = []
    
    if fecha_seleccionada:
        resultado = obtener_disponibilidad(fecha=fecha_seleccionada, comensales=comensales)
        
        if resultado.get('ok'):
            horarios_disponibles = resultado['data'].get('turnos_disponibles', [])
        else:
            for e in resultado.get('errores', []):
                flash(f"No se pudieron cargar los horarios: {e}", "error")

    servicios_extra = obtener_servicios_extra()

    return render_template("reservas.html", horarios=horarios_disponibles, comensales_seleccionados=comensales, fecha_seleccionada=fecha_seleccionada, servicios_extra=servicios_extra)

@reservas_bp.route('/admin/reservas/eliminar', methods=['POST'])
def eliminar_reserva_admin():
    if request.method == 'POST':
        data = request.form.to_dict()

        response = eliminar_reserva(data)

        if response.get("ok"):
            flash("Reserva eliminada con éxito.", "success")
        else:
            errores = response.get("errores", ["Error desconocido al eliminar."])
            for error in errores:
                flash(error, "error")

        return redirect(url_for('pagina_admin'))
