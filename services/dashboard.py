from flask import Flask
import requests
import logging
from constants import API_BASE_URL

logger = logging.getLogger(__name__)

def obtener_estadisticas(filtros):
    try:
        response = requests.get(f"{API_BASE_URL}/dashboard", params=filtros)

        print(f"--- [DEBUG] Status Code del Backend: {response.status_code} ---")
        
        if response.status_code == 200:
            return {"ok": True, "data": response.json()}
        else:
            res_json = response.json()
            print(f"--- [DEBUG] El Backend respondió con error: {res_json} ---")
            errores = [err.get("message", "Error en el formato") for err in res_json.get("errors", [])]
            return {"ok": False, "errores": errores}

    except Exception as e:
        print(f"--- [DEBUG] Error crítico de excepción: {str(e)} ---")
        return {"ok": False, "errores": [f"No se pudo conectar con el backend: {str(e)}"]}