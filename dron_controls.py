from flask import jsonify
from dronLink.Dron import Dron
from pymavlink import mavutil
import time


dron = Dron()

def conectar_dron():
    if dron.state != "connected":
        connection_string = 'tcp:127.0.0.1:5763'
        baud = 115200
        freq=10
        dron.connect(connection_string, baud)
        print("CONECTADOOOOOOOOOOOOOOOOOOOO")
        return {"estado": "success"}
    else:      
        return {"estado": "error"}
    
def desconectar_dron():
    try:
        dron.disconnect()
        return {"estado": "success"}
    except Exception as e:
        return {"estado": "error"}


def armar_dron():
    print(dron.state)
    if dron.state == "connected" or dron.state == "arming" or dron.state == "armed" or dron.state == "takingOff":
        dron.arm(blocking=True)
        print(dron.state)
        return {"estado":"success"}    
    else:
        print("error armar")
        return {"estado": "error"}


def despegar_dron(metros):
    print(dron.state)
    if dron.state != "armed" :
        return {"estado": "error"}
    try:
        dron.takeOff(int(metros, blocking=True))
        return {"estado": "success"}
    except Exception as e:
        return {"estado": "error"}
            

def aterrizar_dron():
    print(dron.state)
    dron.Land(blocking=True)
    return {'estado': 'success', 'message': 'Dron aterrizado'}
    
def mover_dron(direccion, metros):
    print(dron.state)
    try:
        dron.move_distance(direccion, metros, blocking=False)
        return {'estado': 'success'}
    except Exception as e:
        return {'estado': 'error'}

def cambiar_estado(estado):
    print(f"Estado anterior: {dron.state}")
    try:
        dron.state = estado
        print(f"Estado cambiado a: {dron.state}")
        return {'estado': 'success'}
    except Exception as e:
        return {'estado': 'error'}
    
def detener_dron():
    try:
       
        dron.setMoveSpeed(0)  
        return {'estado': 'success'}
    except Exception as e:
        return {'estado': f'Error al detener el movimiento del dron: {e}'}
    
    

def obtener_coordenadas():
    try:
        lat = dron.lat
        lon = dron.lon
        alt = dron.alt
        return {"lat": lat, "lon": lon, "alt": alt}
    except Exception as e:
        return {"error": f"Error al obtener las coordenadas: {str(e)}"}
    

import threading #? no hace falta

datos_telemetria = {}


def obtener_datos_telemetria():
    try:
      
        lat = dron.lat
        lon = dron.lon
        alt = dron.alt
        velocidad = dron.groundSpeed  
        direccion = dron.heading   
        estado = dron.state

    
        datos_telemetria = {
            "lat": lat,
            "lon": lon,
            "alt": alt,
            "velocidad": velocidad,
            "direccion": direccion,
            "estado": estado
        }
        return {"estado": "success", "data": datos_telemetria}
    except Exception as e:
        return {"estado": "error", "message": str(e)}




def armar_y_despegar(metros):
    try:
        print("armar_y_despegar ejecutado")
        armar_dron()  
        if dron.state != "armed" :
            return {"estado": "error"}
        try:
            dron.takeOff(metros, blocking=False)
            return {"estado": "success"}
        except Exception as e:
            return {"estado": "error"}
        
    except Exception as e:
        return {"estado": "error"}

    
def rotar_dron(grados):
    try:
        heading_actual = dron.heading
        nuevo_heading = (heading_actual + grados) % 360  
        dron.changeHeading(nuevo_heading)
        return {"estado": "success"}
    except Exception as e:
        print(f"Error al rotar el dron: {e}")
        return {"estado": "error"}

def ejecutar_mision(mission):
    """Ejecuta la misión proporcionada, manejando tanto waypoints como rotaciones"""
    try:
        print("Iniciando ejecución de misión")
        
        if mission['waypoints']:
            mission_waypoints = {
                "takeOffAlt": mission['takeOffAlt'],
                "waypoints": mission['waypoints']
            }
            dron.uploadMission(mission_waypoints)
            dron.executeMission()

        if 'rotations' in mission and mission['rotations']:
            for rotation in mission['rotations']:
                print(f"Rotando {rotation['degrees']} grados")
                dron.changeHeading(rotation['degrees'])

        return {"estado": "success"}
    except Exception as e:
        print(f"Error ejecutando misión: {str(e)}")
        return {"estado": "error", "mensaje": str(e)}

    
