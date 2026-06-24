from flask import Flask, Blueprint,redirect,url_for,request,render_template, flash
from services.servicios_extra import obtener_servicios_extra,agregar_servicio_extra,eliminar_servicio_extra,actualizar_servicio_extra
from services.resenas import obtener_resenas
from services.menu import obtener_menu

servicios_extra_bp= Blueprint('servicios_extra',__name__)



@servicios_extra_bp.route('/nosotros')
def pagina_nosotros():
    servicios = obtener_servicios_extra()

    resultado = obtener_resenas()

    if resultado.get('ok'):
        resenas = resultado['response']
    else:
        resenas = []
    menu = obtener_menu()
    platos = menu.get('platos', [])
    return render_template(
        'nosotros.html',
        servicios=servicios,
        resenas=resenas,
        platos=platos
    )

@servicios_extra_bp.route('/admin/servicios/agregar', methods=['POST'])
def agregar_servicio():
    nombre= request.form.get("nombre")
    descripcion= request.form.get("descripcion")

    if not nombre or not descripcion:
       flash('Por favor completar todos los campos','error')
       return redirect(url_for('pagina_admin'))

    resultado= agregar_servicio_extra(nombre,descripcion)

    if resultado['ok']:
       flash('El servicio se agrego correctamente','success')
    elif resultado['error'] == 'server_down':
       flash('Servidor caido, por favor intente mas tarde','error')
    else:
       flash('Hubo un error, por favor intente otra vez')


    return redirect(url_for('pagina_admin'))

@servicios_extra_bp.route('/admin/servicios/actualizar', methods=['POST'])
def actualizar_servicio():
   id_servicio = request.form.get('id_servicio')
   nuevo_nombre= request.form.get('nuevo_nombre')
   nueva_descripcion= request.form.get('nueva_descripcion')

   if not id_servicio:
       flash('Campo vacio, por favor ingrese un ID','error')
       return redirect(url_for('pagina_admin'))
   
   if not nuevo_nombre or not nueva_descripcion:
      flash('Completar campos','error')
      return redirect(url_for('pagina_admin'))


   resultado= actualizar_servicio_extra(id_servicio,nuevo_nombre,nueva_descripcion)

   if resultado['ok']:
       flash('El servicio se actualizo correctamente','success')
   elif resultado['error'] == 'server_down':
       flash('Servidor caído','error')
   elif resultado['error'] == 'not_found' :
       flash('El servicio con ese id no existe o hubo un error','error')
   else:
       flash('Error desconocido, lo sentimos...','error')


   return redirect(url_for('pagina_admin'))






@servicios_extra_bp.route('/admin/servicios/eliminar', methods=['POST'])
def eliminar_servicio():
    id_servicio = request.form.get('id_servicio')

    if not id_servicio:
       flash('Campo vacio, por favor ingrese un ID','error')
       return redirect(url_for('pagina_admin'))

    resultado= eliminar_servicio_extra(id_servicio)

    if resultado['ok']:
       flash('El servicio se eliminó correctamente','success')
    elif resultado['error'] == 'server_down':
       flash('Servidor caído','error')
    elif resultado['error'] == 'not_found' :
       flash('El servicio con ese id no existe o hubo un error','error')
    else:
       flash('Error desconocido, lo sentimos...','error')


    return redirect(url_for('pagina_admin'))



