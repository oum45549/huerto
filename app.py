import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Cargar los datos desde el archivo CSV
file_path = "mediciones.csv"
data = pd.read_csv(file_path)

# Convertir la columna 'Fecha' a datetime
data['Fecha'] = pd.to_datetime(data['Fecha'])

# Opción para seleccionar qué columna graficar
columna_seleccionada = st.selectbox("Selecciona la columna para graficar:", data.columns[1:])

# Crear la gráfica
st.title('Gráfico de {}'.format(columna_seleccionada))
fig, ax = plt.subplots()
ax.plot(data['Fecha'], data[columna_seleccionada])
ax.set_xlabel('Fecha')
ax.set_ylabel(columna_seleccionada)
plt.xticks(rotation=45)
plt.tight_layout()

# Mostrar la gráfica en Streamlit
st.pyplot(fig)