from flask import Flask
import requests
import logging
from constants import API_BASE_URL

logger = logging.getLogger(__name__)

def enviar_reserva(datos):
    #Asumo que está bien validado el contenido del formulario.
    nombre = datos.get('nombre_cliente')
    email = datos.get('correo_electronico')
    #telefono = datos['telefono']
    fecha = datos.get('fecha_reserva')
    hora = datos.get('horario_reserva')
    comensales = datos.get('cantidad_personas')
    #servicios_extras_id = datos['servicios_extras_id']

    try:
        print("PAYLOAD FINAL:", {
            'nombre_cliente': nombre,
            'email': email,
            'telefono': "+541112344321",
            'fecha': fecha,
            'hora': hora,
            'comensales': comensales,
            'servicios_extras_id': [],
            'notas_especiales': "su"
        })

        response = requests.post(f'{API_BASE_URL}/reservas',json={'nombre_cliente': nombre,'email': email,'telefono':"+541112344321", 'fecha': fecha, 'hora': hora,'comensales' : int(comensales),"servicios_extras_id":[],"notas_especiales":"su"},timeout=10,)

        if response.status_code == 201:
            return {'ok': True}
        else:
            print("STATUS:", response.status_code)
            print("BODY:", response.text)

            return {
                'ok': False,
                'errores': [
                f"Error API {response.status_code}: {response.text}"
            ]
        }
        
    except requests.exceptions.ConnectionError:
        logger.error(f"No se pudo conectar con la API en {API_BASE_URL}")
        return {'errores': ['No se pudo conectar con el servidor. Verifica que la API esté corriendo.']}

    except Exception as e:
        print(e)
        print(response.status_code)
        print(response.text)
        return {'errores': [str(e)]}