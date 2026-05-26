import sys
import os
from flask import Flask
from .constantes import BASE_URL
#agregar importaciones para los blueprints u otras cosas importantes
from .routes.reservas import reservas_bp


# Buscar módulos en la carpeta donde esté app.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.routes import registrar_rutas

app = Flask(__name__)

# Registrar los endpoints distribuidos en la carpeta routes
registrar_rutas(app)
#agregar blueprints
app.register_blueprint(reservas_bp, url_prefix=BASE_URL)


if __name__ == '__main__':
    app.run(debug=True, port=5000)