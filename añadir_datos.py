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
            datos_csv = pd.read_csv(csv_filename)
            datos_csv['Fecha'] = pd.to_datetime(datos_csv['Fecha'])
            last_date = datos_csv['Fecha'].max()
        except FileNotFoundError:
            datos_csv = pd.DataFrame()
            last_date = datetime.now() - timedelta(days=30)  # Si no existe el archivo, tomar datos de los últimos 70 días
            last_date = last_date.replace(day=1)
        
        # Rango de fechas para obtener nuevos datos
        fecha_actual = datetime.now()
        timestamp_inicio = int((last_date - timedelta(hours=2)).timestamp()) * 1000
        timestamp_actual = int(fecha_actual.timestamp()) * 1000

        url = "https://sensecap.seeed.cc/openapi/list_telemetry_data"
        dispositivo = '2CF7F1C04430015D'

        # Diccionario de códigos de sensores
        codigos = {
            "4097": "Temperatura",
            "4098": "Humedad",
            "4099": "Intensidad de la luz",
            "4101": "Presión",
            "4104": "Dirección del viento",
            "4105": "Velocidad del viento",
            "4113": "Lluvia a la hora",
            "4190": "Índice UV"
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
                data = respuesta.json()
                if 'data' in data and data['data'] and 'list' in data['data']:
                    # Buscar la posición del código
                    codigo_index = data['data']['list'][0].index([1, codigo])
                    for sublist in data['data']['list'][1][codigo_index]:
                        valor = sublist[0]
                        fecha_iso = sublist[1]
                        fecha_actual = parser.parse(fecha_iso)
                        fecha_actual += timedelta(hours=2)  # Ajustar por la diferencia horaria
                        fecha_cercana = fecha_actual.replace(second=0).strftime('%Y-%m-%d %H:%M:%S')

                        for delta in [-30, 0, 30]:
                            fecha_comparacion = fecha_actual + timedelta(seconds=delta)
                            if fecha_comparacion in datos:
                                datos[fecha_comparacion.strftime('%Y-%m-%d %H:%M:%S')][nombre] = valor
                                break
                        else:
                            # Si no se encuentra una fecha cercana, crear una nueva fila
                            datos[fecha_cercana][nombre] = valor

        # Convertir diccionarios a DataFrame
        df_datos = pd.DataFrame.from_dict(datos, orient='index').reset_index()
        df_datos.rename(columns={"index": "Fecha"}, inplace=True)
        df_datos['Fecha'] = pd.to_datetime(df_datos['Fecha'])  # Convertir a datetime

        # Filtrar df_datos para excluir las filas que ya están presentes en datos_csv
        df_datos = df_datos[~df_datos['Fecha'].isin(datos_csv['Fecha'])]
        
        # Concatenar datos nuevos con los existentes
        updated_data = pd.concat([datos_csv, df_datos], ignore_index=True)
        updated_data = updated_data.sort_values(by='Fecha')#para que no añadan primero los más recientes

        # Guardar en un archivo CSV
        updated_data.to_csv(csv_filename, index=False, encoding='utf-8')
        print(f"Datos almacenados en el archivo CSV: {csv_filename}")

    except Exception as e:
        print(f"Error: {e}")

# Llamada a la función para obtener y guardar los datos
obtener_datos()
