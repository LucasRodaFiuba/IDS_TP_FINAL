from flask import Flask, Blueprint,redirect,url_for,request,render_template
from services.servicios_extra import obtener_servicios_extra,agregar_servicio_extra,eliminar_servicio_extra


servicios_extra_bp= Blueprint('servicios_extra',__name__)



@servicios_extra_bp.route('/nosotros')
def pagina_nosotros():
    servicios= obtener_servicios_extra()

    return render_template('nosotros.html',servicios=servicios)


@servicios_extra_bp.route('/admin/servicios/agregar', methods=['POST'])
def agregar_servicio():
    nombre= request.form.get("nombre")
    descripcion= request.form.get("descripcion")

    resultado= agregar_servicio_extra(nombre,descripcion)

    return redirect(url_for('pagina_admin'))


@servicios_extra_bp.route('/admin/servicios/eliminar', methods=['POST'])
def eliminar_servicio():
    id_servicio = request.form['id_servicio']

    resultado= eliminar_servicio_extra(id_servicio)

    return redirect(url_for('pagina_admin'))



