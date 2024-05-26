import requests
import csv
from datetime import datetime, timedelta

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

def obtener_datos_sensores():
    try:
        # Rango de fechas
        fechaActual = datetime.now()
        fechaMesAntes = fechaActual - timedelta(days=30)
        fechaMesAntes = fechaMesAntes.replace(day=1)
        timestampInicio = int(fechaMesAntes.timestamp()) * 1000
        timestampActual = int(fechaActual.timestamp()) * 1000

        # URL de la API
        url = "https://sensecap.seeed.cc/openapi/list_telemetry_data"

        # Inicializar diccionario para almacenar datos por fecha y hora
        datos_por_fecha = {}

        for codigo, nombre in codigos.items():
            params = {
                'device_eui': '2CF7F1C04430015D',
                'channel_index': 1,
                'telemetry': codigo,
                "time_start": str(timestampInicio),
                "time_end": str(timestampActual)
            }

            # Realizar la solicitud API
            response = requests.get(url, params=params, auth=('93I2S5UCP1ISEF4F', '6552EBDADED14014B18359DB4C3B6D4B3984D0781C2545B6A33727A4BBA1E46E'))

            # Verificar si la solicitud fue exitosa
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and data['data'] and 'list' in data['data']:
                    # Buscar la posición del código
                    codigo_index = data['data']['list'][0].index([1, codigo])
                    for sublist in data['data']['list'][1][codigo_index]:
                        fecha_iso = sublist[1]
                        fecha = (datetime.strptime(fecha_iso, '%Y-%m-%dT%H:%M:%S.%fZ') + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
                        valor = sublist[0]

                        if fecha not in datos_por_fecha:
                            datos_por_fecha[fecha] = {}
                        datos_por_fecha[fecha][nombre] = valor

                print(f"Los datos del sensor {nombre} se han procesado correctamente.")
            else:
                print(f"Error: No se pudieron obtener los datos del sensor {nombre}. Código de estado: {response.status_code}")

        # Filtrar datos para eliminar duplicados dentro de 30 segundos
        fechas_ordenadas = sorted(datos_por_fecha.keys())
        datos_filtrados = {}
        
        for fecha in fechas_ordenadas:
            fecha_dt = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')
            rango_inferior = fecha_dt - timedelta(seconds=30)
            rango_superior = fecha_dt + timedelta(seconds=30)
            
            dentro_del_rango = {f: datos_por_fecha[f] for f in fechas_ordenadas if rango_inferior <= datetime.strptime(f, '%Y-%m-%d %H:%M:%S') <= rango_superior}
            
            if dentro_del_rango:
                mejor_fecha = max(dentro_del_rango, key=lambda k: len([v for v in dentro_del_rango[k].values() if v != '']))
                datos_filtrados[mejor_fecha] = datos_por_fecha[mejor_fecha]
                for f in dentro_del_rango:
                    if f != mejor_fecha:
                        fechas_ordenadas.remove(f)

        # Nombre del archivo CSV
        csv_filename = "mediciones2.csv"

        # Escribir los valores en el archivo CSV
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Escribir encabezados
            encabezados = ['Fecha'] + list(codigos.values())
            writer.writerow(encabezados)

            # Escribir datos
            for fecha, valores in sorted(datos_filtrados.items()):
                fila = [fecha] + [valores.get(nombre, '') for nombre in codigos.values()]
                writer.writerow(fila)

        print("Los datos de todos los sensores se han guardado correctamente.")

    except Exception as e:
        print(f"Error: {e}")

# Llamar a la función para obtener y guardar los datos de los sensores de hoy
obtener_datos_sensores()
