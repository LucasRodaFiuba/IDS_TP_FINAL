from flask import Flask
from .constantes import BASE_URL
#agregar importaciones para los blueprints u otras cosas importantes
from .routes.reservas import reservas_bp


app =Flask(__name__)

#agregar blueprints
app.register_blueprint(reservas_bp, url_prefix=BASE_URL)


if __name__ == '__main__':
    app.run(debug=True, port=5000)