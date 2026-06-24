from flask import Flask, Blueprint, render_template, request, redirect, url_for,flash, session
from services.resenas import obtener_resenas, enviar_resena, eliminar_resena

resenas_bp = Blueprint('resenas', __name__)

@resenas_bp.route('/resenas', methods=['GET', 'POST'])
def pagina_resenas():
    origen = request.form.get('origen', url_for('resenas.pagina_resenas'))
    if request.method == 'POST':
        usuario = session.get('usuario')
        token = session.get('token')

        if not usuario or not token:
            flash('Tenés que iniciar sesión para dejar una reseña.', 'error')
            return redirect(url_for('auth.iniciar_sesion'))
        print(request.form)
        print(request.form.get("id_plato"))
        resultado = enviar_resena(
            id_usuario=usuario['id'],
            id_reserva=None,
            id_plato=request.form.get('id_plato') or None, 
            puntuacion=int(request.form.get('puntuacion')),
            comentario=request.form.get('comentario'),
            token=token
        )
        print(f"ID_PLATO ENVIADO: {request.form.get('id_plato')}") 

        if resultado.get('ok'):
            flash('¡Reseña enviada!', 'success')
        else:
            for e in resultado.get('errores', []):
                flash(e, 'error')

        return redirect(origen)

    # GET
    resultado = obtener_resenas()
    if resultado.get('ok'):
        return render_template('reseñas.html', resenas=resultado['response'],platos=[])
    for e in resultado.get('errores', []):
        flash(e, 'error')
    return render_template('reseñas.html', resenas=[], platos=[])

@resenas_bp.route('/resenas/eliminar/<int:id_resena>', methods=['POST'])
def eliminar_resena_view(id_resena):
    origen = request.form.get('origen', url_for('resenas.pagina_resenas'))
    usuario = session.get('usuario')
    token = session.get('token')

    if not usuario or usuario.get('rol') != 'admin':
        flash('No tenés permisos para esto.', 'error')
        return redirect(url_for('resenas.pagina_resenas'))

    resultado = eliminar_resena(id_resena, token)

    if resultado.get('ok'):
        flash('Reseña eliminada.', 'success')
    else:
        for e in resultado.get('errores', []):
            flash(e, 'error')

    return redirect(origen)