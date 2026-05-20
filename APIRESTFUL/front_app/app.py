from flask import Flask, render_template

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


@app.route('/reservas')
def pagina_reservas():
    return render_template('reserva.html')


@app.route('/clientes')
def pagina_clientes():
    return render_template('clientes.html')


@app.route('/iniciar_sesion')
def iniciar_sesion():
    return render_template('iniciar_sesion.html')

@app.route('/admin')
def pagina_admin():
    return render_template('admin.html')


if __name__ == "__main__":
    app.run(debug=True)