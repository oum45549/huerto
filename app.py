import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Cargar los datos desde el archivo CSV
file_path = "mediciones.csv"
data = pd.read_csv(file_path)

# Convertir la columna 'Fecha' a datetime
data['Fecha'] = pd.to_datetime(data['Fecha'])

# Traducción de los nombres de las columnas
nombres_columnas = {
    'Air Temperature': 'Temperatura',
    'Air Humidity': 'Humedad',
    'Light Intensity': 'Intensidad de Luz',
    'Barometric Pressure': 'Presión',
    'Wind Direction': 'Dirección del Viento',
    'Wind Speed': 'Velocidad del Viento',
    'Rainfall Hourly': 'Lluvia',
    'UV Index': 'Índice UV'
}
data = data.rename(columns=nombres_columnas)

# Opción para seleccionar qué columna graficar
columna_seleccionada = st.selectbox("Selecciona la columna para graficar:", list(nombres_columnas.values()))

# Opciones de visualización
opciones_visualizacion = {
    'Todos los datos': data,
    'Últimos 30 días': data[data['Fecha'] >= datetime.now() - timedelta(days=30)],
    'Mes actual': data[data['Fecha'].dt.month == datetime.now().month],
    'Últimos 7 días': data[data['Fecha'] >= datetime.now() - timedelta(days=7)],
    'Semana actual': data[data['Fecha'].dt.isocalendar().week == datetime.now().isocalendar().week],
    'Día actual': data[data['Fecha'].dt.date == datetime.now().date()]
}
opcion_visualizacion = st.selectbox("Selecciona la opción de visualización:", list(opciones_visualizacion.keys()))

# Obtener los datos para la opción seleccionada
datos_visualizacion = opciones_visualizacion[opcion_visualizacion]

# Formatear la fecha para el gráfico del día actual
if opcion_visualizacion == 'Día actual':
    datos_visualizacion['Hora'] = datos_visualizacion['Fecha'].dt.strftime('%H')
    datos_visualizacion = datos_visualizacion.groupby('Hora').mean().reset_index()

# Crear la gráfica
st.title(f'Gráfico de {columna_seleccionada} - {opcion_visualizacion}')
fig, ax = plt.subplots()
ax.plot(datos_visualizacion['Hora'], datos_visualizacion[columna_seleccionada])
ax.set_xlabel('Hora' if opcion_visualizacion == 'Día actual' else 'Fecha')
ax.set_ylabel(columna_seleccionada)
plt.xticks(rotation=45)
plt.tight_layout()

# Mostrar la gráfica en Streamlit
st.pyplot(fig)