import sys
import os
from flask import Flask

# Buscar módulos en la carpeta donde esté app.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.routes import registrar_rutas

app = Flask(__name__)

# Registrar los endpoints distribuidos en la carpeta routes
registrar_rutas(app)

if __name__ == '__main__':
    app.run(debug=True, port=5000)