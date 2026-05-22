import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la página web
st.set_page_config(page_title="Dashboard de Ozaru", layout="wide")

st.title("📊 Dashboard de Control de Tickets")
st.markdown("Sube tu archivo de Excel para actualizar las gráficas automáticamente.")

# 2. Selector de archivos en la barra lateral
st.sidebar.header("Configuración")
uploaded_file = st.sidebar.file_uploader("Sube tu Excel aquí", type=["xlsx", "xls"])

# Si el usuario sube un archivo, usamos ese. Si no, intentamos leer el de prueba local
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, sheet_name="Datos de Soporte")
else:
    try:
        # Intenta buscar el archivo de prueba si lo guardaste en la misma carpeta
        df = pd.read_excel("datos_prueba_dashboard.xlsx", sheet_name="Datos de Soporte")
        st.info("💡 Mostrando los datos del archivo de prueba 'datos_prueba_dashboard.xlsx'.")
    except FileNotFoundError:
        df = None
        st.warning("⚠️ Por favor, sube un archivo de Excel en la barra lateral para ver la gráfica.")

# 3. Renderizar la gráfica si hay datos disponibles
if df is not None:
    # Vista previa opcional de los datos
    if st.checkbox("Mostrar tabla de datos brutos"):
        st.dataframe(df)

    st.subheader("📈 Volumen de Tickets por Módulo y Estado")
    
    # Crear la gráfica de barras con Plotly
    fig_barras = px.histogram(
        df, 
        x="Módulo / Sistema",         # El eje X agrupa por sistema
        color="Estado",                # Colorea las barras según si está Resuelto o Pendiente
        barmode="group",               # Pone las barras una al lado de la otra (en lugar de apiladas)
        title="Tickets Totales por Plataforma",
        labels={"Módulo / Sistema": "Plataforma/Módulo", "count": "Cantidad de Tickets"},
        color_discrete_map={"Resuelto": "#2ecc71", "Pendiente": "#e74c3c"} # Colores personalizados (Verde y Rojo)
    )
    
    # Ajustes estéticos a la gráfica
    fig_barras.update_layout(
        xaxis_title="Sistemas Afectados",
        yaxis_title="Número de Incidentes",
        legend_title="Estatus del Ticket"
    )

    # Mostrar la gráfica en la pantalla
    st.plotly_chart(fig_barras, use_container_width=True)