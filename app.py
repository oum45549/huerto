import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import subprocess

# Ejecutar añadir_datos.py
subprocess.run(["python", "añadir_datos.py"]) #este .py añade los datos nuevos al CSV

# Cargar los datos desde el archivo CSV
file_path = "mediciones.csv"
data = pd.read_csv(file_path)

# Convertir la columna 'Fecha' a datetime
data['Fecha'] = pd.to_datetime(data['Fecha'])

# Excluir la columna de fecha y obtener los nombres de las columnas restantes
nombres_columnas = [col for col in data.columns if col != 'Fecha']

# Opción para seleccionar qué columna graficar
columna_seleccionada = st.selectbox("Selecciona la columna para graficar:", nombres_columnas)

# Opciones de visualización
opciones_visualizacion = {
    'Todos los tiempos': data,
    'Últimos 30 días': data[data['Fecha'] >= datetime.now() - timedelta(days=30)],
    'Mes actual': data[data['Fecha'].dt.month == datetime.now().month],
    'Últimos 7 días': data[data['Fecha'] >= datetime.now() - timedelta(days=7)],
    'Día actual': data[data['Fecha'].dt.date == datetime.now().date()]
}
opcion_visualizacion = st.selectbox("Selecciona la opción de visualización:", list(opciones_visualizacion.keys()))

# Obtener los datos para la opción seleccionada
datos_visualizacion = opciones_visualizacion[opcion_visualizacion]

# Crear la gráfica
st.title(f'Gráfico de {columna_seleccionada} - {opcion_visualizacion}')
fig, ax = plt.subplots()

# Verificar si la opción de visualización es para el día actual
if opcion_visualizacion == 'Día actual':
    # Ordenar los datos cronológicamente
    datos_visualizacion = datos_visualizacion.sort_values(by='Fecha')
    # Formatear la fecha para mostrar solo la hora
    datos_visualizacion['Hora'] = datos_visualizacion['Fecha'].dt.strftime('%H:%M')
    ax.plot(datos_visualizacion['Hora'], datos_visualizacion[columna_seleccionada])
    ax.set_xlabel('Hora')
    # Ajustar las etiquetas del eje X para mostrar solo cada hora
    x_ticks = datos_visualizacion['Hora'].iloc[::12]  # Cada 12*5 = 60 minutos = 1 hora
    ax.set_xticks(x_ticks)
else:
    ax.plot(datos_visualizacion['Fecha'], datos_visualizacion[columna_seleccionada])
    ax.set_xlabel('Fecha')

ax.set_ylabel(columna_seleccionada)
plt.xticks(rotation=45)
plt.tight_layout()

# Mostrar la gráfica en Streamlit
st.pyplot(fig)