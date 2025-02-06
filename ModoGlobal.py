import random
import time
import json
from paho.mqtt import client as mqtt_client
from .dron_controls import conectar_dron, despegar_dron, desconectar_dron, armar_y_despegar, aterrizar_dron, ejecutar_mision, rotar_dron, mover_dron

global ultima_respuesta
ultima_respuesta = None

mqtt_client_instance = None
broker = 'broker.emqx.io'
port = 1883
topic = "smartphone/commands"
client_id = f'python-mqtt-{random.randint(0, 1000)}'


def on_message(client, userdata, msg):
    """Maneja los mensajes recibidos del broker MQTT"""
    global ultima_respuesta
    try:
        payload = json.loads(msg.payload.decode())
        comando = payload.get('action')
        print(f"Comando recibido broker: {comando}")

        if comando == "conectar":
            print("DRON INTENTANDO CONECTAR MEDIANTE BROKER")
            result = conectar_dron()
            print(f"DEBUG on_message: Resultado de conectar_dron: {result}")
            ultima_respuesta = result
            print(f"DEBUG on_message: ultima_respuesta actualizada a {ultima_respuesta}")

        elif comando == "despegar":
            altura = payload.get('altura', 5)
            result = armar_y_despegar(altura)
            ultima_respuesta = result

        elif comando == "aterrizar":
            result = aterrizar_dron()
            ultima_respuesta = result

        elif comando == "desconectar":
            result = desconectar_dron()
            ultima_respuesta = result

        elif comando == "mover":
            direccion = payload.get('direccion')
            metros = payload.get('metros', 3)
            if not direccion:
                ultima_respuesta = {"estado": "error", "mensaje": "Dirección no especificada"}
            else:
                result = mover_dron(direccion, metros)
                ultima_respuesta = result

        elif comando == "ejecutar_mision":
            mission = payload.get('mission')
            if mission:
                result = ejecutar_mision(mission)
                ultima_respuesta = result
            else:
                ultima_respuesta = {"estado": "error", "mensaje": "Misión no especificada"}

        else:
            ultima_respuesta = {"estado": "error", "mensaje": "Comando no reconocido"}

        print(f"DEBUG on_message: Respuesta final establecida: {ultima_respuesta}")

    except Exception as e:
        print(f"Error en on_message: {str(e)}")
        ultima_respuesta = {"estado": "error", "mensaje": str(e)}
        print(f"DEBUG on_message: Error respuesta: {ultima_respuesta}")

def connect_mqtt():
    """Establece la conexión con el broker MQTT"""
    global mqtt_client_instance

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("DEBUG connect_mqtt: Conectado exitosamente al broker MQTT")
            client.subscribe(topic)
            print(f"DEBUG connect_mqtt: Suscrito al tópico '{topic}'")
            client.connected_flag = True
        else:
            print(f"DEBUG connect_mqtt: Fallo en conexión, código: {rc}")
            client.connected_flag = False

    try:
        if mqtt_client_instance and mqtt_client_instance.is_connected():
            print("DEBUG connect_mqtt: Ya existe una conexión activa")
            return mqtt_client_instance

        print("DEBUG connect_mqtt: Creando nueva conexión MQTT")
        client_id = f'python-mqtt-{random.randint(0, 1000)}'
        mqtt_client_instance = mqtt_client.Client(client_id)
        mqtt_client_instance.connected_flag = False
        mqtt_client_instance.on_connect = on_connect
        mqtt_client_instance.on_message = on_message

        print("DEBUG connect_mqtt: Intentando conectar al broker")
        mqtt_client_instance.connect(broker, port)
        mqtt_client_instance.loop_start()

        timeout = 5
        start_time = time.time()
        while time.time() - start_time < timeout:
            if hasattr(mqtt_client_instance, 'connected_flag') and mqtt_client_instance.connected_flag:
                print("DEBUG connect_mqtt: Conexión establecida exitosamente")
                return mqtt_client_instance
            time.sleep(0.1)

        print("DEBUG connect_mqtt: Timeout esperando conexión")
        mqtt_client_instance.loop_stop()
        mqtt_client_instance = None
        return None

    except Exception as e:
        print(f"DEBUG connect_mqtt: Error al conectar: {str(e)}")
        if mqtt_client_instance:
            mqtt_client_instance.loop_stop()
            mqtt_client_instance = None
        return None

def publish_command(comando):
    """Publica un comando en el broker MQTT"""
    global mqtt_client_instance
    
    try:
        if not mqtt_client_instance or not mqtt_client_instance.is_connected():
            print("DEBUG publish_command: Reconectando al broker MQTT")
            mqtt_client_instance = connect_mqtt()
            if not mqtt_client_instance:
                print("DEBUG publish_command: No se pudo establecer conexión MQTT")
                return False
            
            time.sleep(0.5)

        if isinstance(comando, dict):
            comando = json.dumps(comando)
        
        print(f"DEBUG publish_command: Publicando comando: {comando}")
        result = mqtt_client_instance.publish(topic, comando)
        
        if result.rc == 0:
            print("DEBUG publish_command: Comando publicado exitosamente")
            return True
        else:
            print(f"DEBUG publish_command: Error al publicar comando, código: {result.rc}")
            return False
            
    except Exception as e:
        print(f"DEBUG publish_command: Error al publicar comando: {str(e)}")
        return False