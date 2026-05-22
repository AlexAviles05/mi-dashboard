import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la página web
st.set_page_config(page_title="Mi Dashboard de Ozaru", layout="wide")

st.title("📊 Dashboard Interactivo desde Excel")
st.markdown("Bienvenido al panel de control. Sube tu archivo para comenzar.")

# 2. Selector de archivos (Para que subas el Excel directamente en la web)
uploaded_file = st.file_uploader("Elige tu archivo de Excel", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Leer el Excel usando Pandas
    df = pd.read_excel(uploaded_file)
    
    # Mostrar una vista previa de la tabla de datos
    st.subheader("👀 Vista previa de los datos")
    st.dataframe(df.head())
    
    # --- Ejemplo de Gráfica 1 (Métricas clave) ---
    st.subheader("📈 Análisis de Datos")
    
    # Asumiendo que tu Excel tiene columnas, puedes crear selectores interactivos:
    columnas = df.columns.tolist()
    eje_x = st.selectbox("Selecciona la columna para el Eje X:", columnas)
    eje_y = st.selectbox("Selecciona la columna para el Eje Y:", columnas)
    
    # Crear gráfica interactiva con Plotly
    fig = px.bar(df, x=eje_x, y=eje_y, title=f"Gráfico de Barras: {eje_y} vs {eje_x}")
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Por favor, sube un archivo de Excel para desplegar los gráficos.")