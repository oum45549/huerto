import requests
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
from dateutil import parser

def obtener_datos():
    try:
        # Leer el CSV existente para encontrar la última fecha de medición
        csv_filename = "mediciones.csv"
        try:
            data = pd.read_csv(csv_filename)
            data['Fecha'] = pd.to_datetime(data['Fecha'])
            last_date = data['Fecha'].max()
        except FileNotFoundError:
            data = pd.DataFrame()
            last_date = datetime.now() - timedelta(days=70)  # Si no existe el archivo, tomar datos de los últimos 70 días
            last_date = last_date.replace(day=1)
        
        # Rango de fechas para obtener nuevos datos
        fecha_actual = datetime.now()
        timestamp_inicio = int(last_date.timestamp()) * 1000
        timestamp_actual = int(fecha_actual.timestamp()) * 1000

        url = "https://sensecap.seeed.cc/openapi/list_telemetry_data"
        dispositivo = '2CF7F1C04430015D'

        codigos = {
            "4097": "Air Temperature",
            "4098": "Air Humidity",
            "4099": "Light Intensity",
            "4101": "Barometric Pressure",
            "4104": "Wind Direction",
            "4105": "Wind Speed",
            "4113": "Rainfall Hourly",
            "4190": "UV Index"
        }

        # Diccionario para almacenar los datos
        datos = defaultdict(lambda: {codigo: None for codigo in codigos.values()})

        for codigo, nombre in codigos.items():
            params = {
                'device_eui': dispositivo,
                'channel_index': 1,
                'telemetry': codigo,
                "time_start": str(timestamp_inicio),
                "time_end": str(timestamp_actual)
            }

            respuesta = requests.get(url, params=params, auth=('93I2S5UCP1ISEF4F', '6552EBDADED14014B18359DB4C3B6D4B3984D0781C2545B6A33727A4BBA1E46E'))

            if respuesta.status_code == 200:
                datos_respuesta = respuesta.json()

                for mediciones in datos_respuesta["data"]["list"][1]:
                    for medicion in mediciones:
                        valor = medicion[0]
                        fecha_str = medicion[1]
                        fecha_actual_str = parser.parse(fecha_str)
                        fecha_cercana_str = fecha_actual_str.replace(second=0)

                        for delta in [-30, 0, 30]:
                            fecha_comparacion = fecha_cercana_str + timedelta(seconds=delta)
                            fecha_comparacion_str = fecha_comparacion.strftime('%Y-%m-%d %H:%M:%S')
                            if fecha_comparacion_str in datos:
                                datos[fecha_comparacion_str][nombre] = valor
                                break
                        else:
                            # Si no se encuentra una fecha cercana, crear una nueva fila
                            datos[fecha_cercana_str.strftime('%Y-%m-%d %H:%M:%S')] = {nombre: valor}

        # Convertir diccionarios a DataFrame
        df_datos = pd.DataFrame.from_dict(datos, orient='index').reset_index()
        df_datos.rename(columns={"index": "Fecha"}, inplace=True)
        df_datos['Fecha'] = pd.to_datetime(df_datos['Fecha'])  # Convertir a datetime


        if not data.empty:
            # Filtrar datos que son posteriores a la última fecha de medición
            df_datos = df_datos[df_datos['Fecha'] > last_date]

        # Concatenar datos nuevos con los existentes
        updated_data = pd.concat([data, df_datos], ignore_index=True)

        # Guardar en un archivo CSV
        updated_data.to_csv(csv_filename, index=False)
        print(f"Datos almacenados en el archivo CSV: {csv_filename}")

    except Exception as e:
        print(f"Error: {e}")

# Llamada a la función para obtener y guardar los datos
obtener_datos()
