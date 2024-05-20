import requests
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
from dateutil import parser

def obtenerDatos():
    try:
        # Rango de fechas
        fechaActual = datetime.now()
        fechaMesAntes = fechaActual - timedelta(days=70)
        fechaMesAntes = fechaMesAntes.replace(day=1)
        timestampInicio = int(fechaMesAntes.timestamp()) * 1000
        timestampActual = int(fechaActual.timestamp()) * 1000


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
                "time_start": str(timestampInicio),
                "time_end": str(timestampActual)
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
        
        # Guardar en un archivo CSV
        csv_filename = "mediciones.csv"
        df_datos.to_csv(csv_filename, index=False)
        print(f"Datos almacenados en el archivo CSV: {csv_filename}")

    except Exception as e:
        print(f"Error: {e}")

# Llamada a la función para obtener y guardar los datos
obtenerDatos()
