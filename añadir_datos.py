import pandas as pd
from datetime import datetime
import paho.mqtt.client as mqtt
import json

# Configuración MQTT
HOST = "sensecap-openstream.seeed.cc"
PORT = 1883
USERNAME = "org-434181208382464"
PASSWORD = "6552EBDADED14014B18359DB4C3B6D4B3984D0781C2545B6A33727A4BBA1E46E"
TOPIC = "/device_sensor_data/434181208382464/2CF7F1C04430015D/1/vs/+"
CLIENT_ID = "org-434181208382464-7"

# Ruta al archivo CSV
file_path = "mediciones.csv"

def on_message(client, userdata, message):
    new_data = json.loads(message.payload.decode("utf-8"))
    new_row = {
        'Fecha': datetime.now(),
        'Temperatura del Aire': new_data.get('temperature', None),
        'Humedad del Aire': new_data.get('humidity', None),
        'Intensidad de Luz': new_data.get('light', None),
        'Presión Barométrica': new_data.get('pressure', None),
        'Dirección del Viento': new_data.get('wind_direction', None),
        'Velocidad del Viento': new_data.get('wind_speed', None),
        'Lluvia Horaria': new_data.get('rainfall', None),
        'Índice UV': new_data.get('uv', None)
    }
    userdata.append(new_row)

def fetch_new_data():
    new_data = []

    client = mqtt.Client(client_id=CLIENT_ID, userdata=new_data)
    client.username_pw_set(USERNAME, PASSWORD)
    client.on_message = on_message

    client.connect(HOST, PORT, 60)
    client.subscribe(TOPIC)

    # Procesar mensajes entrantes durante un breve período de tiempo (ej. 5 segundos)
    client.loop_start()
    client.loop_stop()

    return new_data

def update_csv():
    # Leer el CSV existente
    data = pd.read_csv(file_path)
    data['Fecha'] = pd.to_datetime(data['Fecha'])

    # Encontrar la última fecha de medición
    last_date = data['Fecha'].max()

    # Obtener nuevas mediciones
    new_data = fetch_new_data()

    if new_data:
        # Crear un DataFrame con las nuevas mediciones
        new_df = pd.DataFrame(new_data)
        # Filtrar datos que son posteriores a la última fecha de medición
        new_df = new_df[new_df['Fecha'] > last_date]
        # Añadir las nuevas mediciones al CSV existente
        updated_data = pd.concat([data, new_df], ignore_index=True)
        updated_data.to_csv(file_path, index=False)

if __name__ == "__main__":
    update_csv()
