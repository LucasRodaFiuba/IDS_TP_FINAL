import logging
from ..utils import construir_error_api
from ..validators.reservas import validar_body_nueva_reserva,validar_parametros
from .. import db
from ..constantes import HORARIOS_PARA_RESERVAR
logger = logging.getLogger(__name__)

def consultar_disponibilidad(fecha,comensales):
    """
    Retorna el dic con la consulta o puede retornar errores
    por validación o por conflictos
    """
    datos = validar_parametros(fecha,comensales)

    fecha = datos['fecha']
    comensales = datos['comensales']

    mesas = db.obtener_mesas_por_capacidad(comensales)
    print("MESAS:", mesas)
    turnos_disponibles = []

    #Recorro los horarios, con que haya al menos una mesa disponible
    #entra en mesas_disponibles
    for hora in HORARIOS_PARA_RESERVAR:
        for mesa in mesas:
            print("MESA:", mesa)
            if not db.mesa_ocupada(mesa['numero_mesa'],fecha,hora):
                #No está ocupada
                turnos_disponibles.append(hora)
                break #en caso de que se repita horario

    #Retorno respetando el swagger
    return {
        'fecha': fecha,
        'turnos_disponibles': turnos_disponibles
    }


    
#agregar_reserva la voy a utilizar en routes en crear_reserva.
def crear_reserva(body):
    """
    Retorna el dic con la reserva. O puede retornar errores
    por validación, o por conflictos.
    """
    #Si no hay errores, datos contiene el body validado.
    datos = validar_body_nueva_reserva(body)

    # 1.Obtengo las mesas posibles , es decir
    # podrían entrar esa cantidad de comensales
    # (no significa que esten libres)
    print("COMENSALES FINAL:", datos['comensales'], type(datos['comensales']))
    mesas = db.obtener_mesas_por_capacidad(datos['comensales'])
    print(mesas)
    mesa_asignada = None

    if len(datos["hora"]) == 5:
        datos["hora"] += ":00"

    print("DEBUG MESAS:", mesas)
    # 2.Busco si hay alguna mesa libre. (de las que están disponibles)
    for mesa in mesas:
        print("MESA:", mesa['numero_mesa'])
        print("OCUPADA:", db.mesa_ocupada(mesa['numero_mesa'], datos['fecha'], datos['hora']))
        if not db.mesa_ocupada(mesa['numero_mesa'], datos['fecha'], datos['hora']):
            mesa_asignada = mesa
            break

    # 3.Si no hay mesas libres
    if not mesa_asignada:
        raise ValueError(construir_error_api(
            code="no.disponibilidad",
            message="No hay mesas disponibles",
            description="No hay mesas libres para esa fecha y hora"
        ),409)

    #Obtengo el id del usuario
    id_usuario = db.obtener_usuario_por_email(datos['email'])

    # 4. insertar reserva
    db.añadir_reserva(
        id_usuario= id_usuario,
        numero_mesa=mesa_asignada['numero_mesa'],
        fecha=datos['fecha'],
        hora=datos['hora'],
        comensales=datos['comensales']
    )

    # 5. devolver DTO
    return {
    "nombre_cliente": datos["nombre_cliente"],
    "email": datos["email"],
    "telefono": datos["telefono"],
    "fecha": datos["fecha"],
    "hora": datos["hora"],
    "comensales": datos["comensales"],
    "servicios_extras_id": datos["servicios_extras_id"],
    "notas_especiales": datos["notas_especiales"],
    "numero_mesa": mesa_asignada["numero_mesa"],
    "estado": "pendiente"
    }