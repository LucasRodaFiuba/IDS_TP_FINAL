from flask import Flask, render_template, request, redirect, url_for
from services.reservas import obtener_reservas, enviar_reserva


app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


@app.route('/menu')
def pagina_menu(): 
    return render_template('menu.html')


@app.route('/nosotros')
def pagina_nosotros():
    return render_template('nosotros.html')


@app.route('/reservas', methods=['GET', 'POST'])
def pagina_reservas():
    if request.method == 'POST':
        fecha = request.form.get('fecha_reserva')
        hora = request.form.get('horario_reserva')
        personas = request.form.get('cantidad_personas')
        nombre = request.form.get('nombre_cliente')

        resultado = enviar_reserva(fecha, hora, personas, nombre)

        if 'ok' in resultado:
            return redirect(url_for('reservas.pagina_reservas', exito=True))
        else:
            return render_template('reservas.html', reservas=obtener_reservas(), errores_api=resultado['errores'])

    lista_reservas = obtener_reservas()

    return render_template('reservas.html', reservas=lista_reservas, exito=request.args.get('exito'))


@app.route('/clientes')
def pagina_clientes():
    return render_template('clientes.html')


@app.route('/iniciar_sesion')
def iniciar_sesion():
    return render_template('iniciar_sesion.html')

@app.route('/admin')
def pagina_admin():
    return render_template('admin.html')

@app.route('/admin/reservas')
def admin_reservas():
    return render_template('admin_reservas.html')

@app.route('/admin/clientes')
def admin_clientes():
    return render_template('admin_clientes.html')

@app.route('/admin/menu/entradas', methods=['POST'])
def agregar_entrada():
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    ingredientes = request.form['ingredientes']

@app.route('/admin/menu/plato', methods=['POST'])
def agregar_plato():
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    ingredientes = request.form['ingredientes']

@app.route('/admin/menu/postre', methods=['POST'])
def agregar_postre():
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    ingredientes = request.form['ingredientes']

@app.route('/admin/menu/bebida', methods=['POST'])
def agregar_bebida():
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    ingredientes = request.form['ingredientes']
    
@app.route('/admin/menu/modificar', methods=['UPDATE'])
def modificar_objeto():
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    ingredientes = request.form['ingredientes']

@app.route('/admin/menu/eliminar', methods=['DELETE'])
def eliminar_objeto():
    nombre = request.form['nombre']

@app.route('/admin/reservas/agregar', methods=['POST'])
def agregar_reserva():
    nombre_cliente = request.form['nombre_cliente']
    fecha_hora = request.form['fecha_hora']
    cantidad_personas = request.form['cantidad_personas']

@app.route('/admin/reservas/modificar', methods=['UPDATE'])
def modificar_reserva():
    nombre_cliente = request.form['nombre_cliente']
    fecha_hora_reserva = request.form['fecha_hora_reserva']
    nueva_fecha_hora = request.form['nueva_fecha_hora']

@app.route('/admin/reservas/eliminar', methods=['DELETE'])
def eliminar_reserva():
    nombre_cliente = request.form['nombre_cliente']
    fecha_hora = request.form['fecha_hora']


@app.route('/admin/usuarios/agregar', methods=['POST'])
def agregar_usuario():
    nombre_usuario = request.form['nombre_usuario']
    correo_electronico = request.form['correo_electronico']
    contrase単a = request.form['contrase単a']

@app.route('/admin/usuarios/modificar', methods=['UPDATE'])
def modificar_usuario():
    nombre_usuario = request.form['nombre_usuario']
    nuevo_nombre_usuario = request.form['nuevo_nombre_usuario']
    nuevo_correo_electronico = request.form['nuevo_correo_electronico']
    nueva_contrase単a = request.form['nueva_contrase単a']

@app.route('/admin/usuarios/eliminar', methods=['DELETE'])
def eliminar_usuario():
    nombre_usuario = request.form['nombre_usuario']

if __name__ == "__main__":
    app.run(debug=True)
