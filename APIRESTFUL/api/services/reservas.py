import email
import logging
from ..utils import construir_error_api
from ..validators.reservas import validar_body_nueva_reserva,validar_parametros
from .. import db_funciones
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
    Retorna el diccionario con la consulta o puede retornar errores
    por validación o por conflictos (por medio de propagación)
    """
    datos = validar_parametros(fecha,comensales)

    fecha = datos['fecha']
    comensales = datos['comensales']

    mesas = db_funciones.obtener_mesas_por_capacidad(comensales)
    turnos_disponibles = []

    #Recorro los horarios, y veo si hay alguna mesa disponible en ese horario
    for hora in HORARIOS_PARA_RESERVAR:
        for mesa in mesas:
            if not db_funciones.mesa_ocupada(mesa['numero_mesa'],fecha,hora):
                turnos_disponibles.append(hora)
                break #en caso de que se repita horario

    return {
        'fecha': fecha,
        'turnos_disponibles': turnos_disponibles
    }

def crear_reserva(body):
    """
    Retorna el diccionario con la reserva. O puede retornar errores
    por validación, o por conflictos.
    """
    datos = validar_body_nueva_reserva(body)

    #Obtengo las mesas candidatas a ser ocupadas.
    mesas = db_funciones.obtener_mesas_por_capacidad(datos['comensales'])
    mesa_asignada = None

    if len(datos["hora"]) == 5:
        datos["hora"] += ":00"

    #Busco si hay alguna mesa libre.
    for mesa in mesas:
        if not db_funciones.mesa_ocupada(mesa['numero_mesa'], datos['fecha'], datos['hora']):
            mesa_asignada = mesa
            break

    #Si no hay mesas libres
    if not mesa_asignada:
        raise ValueError(construir_error_api(
            code="no.disponibilidad",
            message="No hay mesas disponibles",
            description="No hay mesas libres para esa fecha y hora"
        ),409)

    #Obtengo el id del usuario
    id_usuario = db_funciones.obtener_usuario_por_email(datos['email'])

    #Casos bordes
    if not id_usuario:
        raise ValueError(construir_error_api(
            code="usuario.no.existe",
            message="Usuario no encontrado",
            description="El email no está registrado en la base de datos"
        ), 404)

    if db_funciones.tiene_muchas_cancelaciones(id_usuario):
        raise ValueError(construir_error_api(
            code="usuario.alcanzo.limite.cancelaciones",
            message="El usuario no puede reservar mas por este mes",
            description="El usuario llego al tope de reservas en el mes debido a alcanzar el tope de cancelaciones."
        ),403)

    #Generar token QR
    token = str(uuid.uuid4())

    #Insertar reserva.
    id_reserva = db_funciones.añadir_reserva(
        id_usuario= id_usuario,
        numero_mesa=mesa_asignada['numero_mesa'],
        fecha=datos['fecha'],
        hora=datos['hora'],
        comensales=datos['comensales'],
        codigo_qr=token
    )

    #Genero QR
    qr_path = generar_qr(token,{
        "id_reserva": id_reserva,
        "token": token
    })

    #Enviar email con QR
    enviar_mail(
    destinatario=datos["email"],
    asunto="Tu reserva",
    cuerpo="Reserva realizada. Adjuntamos el QR.",
    archivo_adjunto=qr_path
    )

    #Devuelvo un diccionario con todos los datos de la reserva realizada.
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

    id_usuario = db_funciones.obtener_id_usuario(id_reserva)

    if not id_usuario:
        raise ValueError("Reserva no existe",404)

    db_funciones.update_reserva(id_reserva, datos)
    db_funciones.update_usuario(id_usuario, datos)

    # Actualizo servicios extra asociados
    servicios_extras = datos.get("servicios_extras_id")

    if servicios_extras is not None:
        db_funciones.actualizar_servicios_reserva(
            id_reserva,
            servicios_extras
        )

    return {
        "message": "Reserva actualizada correctamente",
        "id_reserva": id_reserva
    }

def cancelar_reserva_service(id_reserva):
    """
    Cancela una reserva y devuelve un mensaje
    """
    filas_afectadas = db_funciones.cancelar_reserva(id_reserva)

    #En caso de que el id_reserva no exista
    if filas_afectadas == 0:
        raise ValueError("Reserva no existe", 404)

    return{
        "message": "Reserva cancelada con éxito",
        "id_reserva" : id_reserva
    }



def validar_reserva_service(token):
    reserva = db_funciones.buscar_reserva_por_token(token)

    if not reserva:
        raise ValueError(construir_error_api(
            code="reserva.no.existe",
            message="reserva no encontrado",
            description="Reserva no encontrada"))

    if reserva["estado"] != "pendiente":
        raise ValueError(construir_error_api(
            code="reserva.ya.procesada",
            message="invalido",
            description="No se puede confirmar una reserva que ya lo está o que fue cancelada"))

    #Actualizo el estado en confirmada
    db_funciones.actualizar_estado_reserva(token, "confirmada")

    return {"Hora":reserva["hora_reserva"],"Fecha":reserva["fecha_reserva"],"comensales":reserva["cantidad_personas"],"Estado de la reserva": reserva["estado"]}

#SERVICE PARA MIS_RESERVAS
def obtener_reservas_segun_email(email):
    """
    Retorna una lista de diccionarios si todo sale bien, cada diccionario
    representaría una reserva que se obtiene del usuario (con datos del mismo).
    """
    usuario = db_funciones.obtener_usuario_publico_por_email(email)

    if not usuario:
        raise ValueError(construir_error_api(
            code="email.inexistente",
            message="invalido",
            description="El email no está registrado en la base de datos"),404)

    reservas = db_funciones.obtener_reservas_de_usuario(
        usuario["id_usuario"]
    )

    if len(reservas) == 0:
        return []

    #convierto hora_reserva en string
    for reserva in reservas:
        reserva["hora_reserva"] = str(reserva["hora_reserva"])
        reserva["fecha_reserva"] = str(reserva["fecha_reserva"])
        reserva["fecha_creacion"] = str(reserva["fecha_creacion"])

    return reservas


def crear_reserva_admin(body):
    """
    Retorna el dic con la reserva. O puede retornar errores
    por validación, o por conflictos.
    """
    #Si no hay errores, datos contiene el body validado.
    datos = validar_body_nueva_reserva(body)

    # 1.Obtengo las mesas posibles , es decir
    # podrían entrar esa cantidad de comensales
    # (no significa que esten libres)
    mesas = db_funciones.obtener_mesas_por_capacidad(datos['comensales'])
    mesa_asignada = None

    if len(datos["hora"]) == 5:
        datos["hora"] += ":00"

    # 2.Busco si hay alguna mesa libre. (de las que están disponibles)
    for mesa in mesas:
        if not db_funciones.mesa_ocupada(mesa['numero_mesa'], datos['fecha'], datos['hora']):
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
    id_usuario = db_funciones.obtener_usuario_por_email(datos['email'])

    # 5. generar token QR
    token = str(uuid.uuid4())

    # 6. insertar reserva (debe devolver el id_reserva)
    id_reserva = db_funciones.añadir_reserva(
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


def eliminar_reserva(email, fecha_reserva, hora_reserva):
    reserva = db_funciones.obtener_reservas_email_fecha_hora(email, fecha_reserva, hora_reserva)
    if not reserva:
        raise ValueError(construir_error_api(
            code="reserva.no.existe",
            message="Reserva no encontrada",
            description="No se encontró una reserva con ese email, fecha y hora"
        ), 404)
    db_funciones.eliminar_reserva(email, fecha_reserva, hora_reserva)
    
    

