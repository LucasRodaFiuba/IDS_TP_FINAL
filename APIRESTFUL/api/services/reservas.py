import logging
from ..utils import construir_error_api
from ..validators.reservas import validar_body_nueva_reserva,validar_parametros
from .. import db
from ..constantes import HORARIOS_PARA_RESERVAR

#UTIL PARA LO DEL QR
import uuid
from ..utils import generar_qr
from ..services.email_service import enviar_mail
#from ..db import reservas as db
#from ..utils.errores import construir_error_api
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
    mesas = db.obtener_mesas_por_capacidad(datos['comensales'])
    mesa_asignada = None

    if len(datos["hora"]) == 5:
        datos["hora"] += ":00"

    # 2.Busco si hay alguna mesa libre. (de las que están disponibles)
    for mesa in mesas:
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

    #4. Obtengo el id del usuario
    id_usuario = db.obtener_usuario_por_email(datos['email'])

    #Muestro mensaje de error sino existe usuario
    if not id_usuario:
        raise ValueError(construir_error_api(
            code="usuario.no.existe",
            message="Usuario no encontrado",
            description="El email no está registrado en la base de datos"
        ), 404)

    # 5. generar token QR
    token = str(uuid.uuid4())

    # 6. insertar reserva (debe devolver el id_reserva)
    id_reserva = db.añadir_reserva(
        id_usuario= id_usuario,
        numero_mesa=mesa_asignada['numero_mesa'],
        fecha=datos['fecha'],
        hora=datos['hora'],
        comensales=datos['comensales'],
        codigo_qr=token
    )

    # 7. Genero QR
    qr_path = generar_qr(token,{
        "id_reserva": id_reserva,
        "token": token
    })

    # 8. Enviar email con QR + link cancelar
    enviar_mail(
    destinatario=datos["email"],
    asunto="Tu reserva",
    cuerpo="Tu reserva fue confirmada. Adjuntamos el QR.",
    archivo_adjunto=qr_path
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
    "estado": "pendiente",
    "codigo_qr": token,
    "id_reserva" : id_reserva
    }

def cambiar_reserva(id_reserva,body):
    """
    Retorna un diccionario mostrando mensajes válidos 
    o puede retornar errores por validación.
    """
    datos = validar_body_nueva_reserva(body)

    id_usuario = db.obtener_id_usuario(id_reserva)

    if not id_usuario:
        raise ValueError("Reserva no existe",404)

    db.update_reserva(id_reserva, datos)
    db.update_usuario(id_usuario, datos)

    return {
        "message": "Reserva actualizada correctamente",
        "id_reserva": id_reserva
    }

def cancelar_reserva_service(id_reserva):
    """
    Cancela una reserva y devuelve un mensaje
    """
    #el id_reserva ya viene validado

    filas_afectadas = db.cancelar_reserva(id_reserva)

    #En caso de que el id_reserva no exista
    if filas_afectadas == 0:
        raise ValueError("Reserva no existe", 404)

    return{
        "message": "Rerserva cancelada con éxito",
        "id_reserva" : id_reserva
    }



#Services para todo el tema del QR
def validar_reserva_service(token):
    print("TOKEN:", token)
    reserva = db.buscar_reserva_por_token(token)
    print("RESERVA:", reserva)

    if not reserva:
        raise ValueError(construir_error_api(
            code="reserva.no.existe",
            message="reserva no encontrado",
            description="Reserva no encontrada"))

    if reserva["estado"] != "pendiente":
        raise ValueError(construir_error_api(
            code="reserva.invalida",
            message="invlaido",
            description="El email no está registrado en la base de datos"))

    #Actualizo el estado en confirmada
    db.actualizar_estado_reserva(token, "confirmada")

    return {"message": "Reserva confirmada"}