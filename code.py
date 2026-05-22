import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la página web
st.set_page_config(page_title="Dashboard de Ozaru", layout="wide")

st.title("📊 Dashboard de Control de Tickets")
st.markdown("Sube tu archivo de Excel o usa el archivo predeterminado del repositorio.")

# 2. Configuración en la barra lateral
st.sidebar.header("Configuración")
uploaded_file = st.sidebar.file_uploader("Sube tu Excel aquí", type=["xlsx", "xls"])

df = None

# Intentar cargar los datos (Prioriza el archivo subido; si falla, usa el local)
if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file, sheet_name="Datos de Soporte")
    except Exception:
        st.sidebar.error("Error al procesar el archivo subido. Usando respaldo...")

# Si no hay archivo subido o falló el cargador web, lee el archivo del repositorio
if df is None:
    try:
        df = pd.read_excel("datos_prueba_dashboard.xlsx", sheet_name="Datos de Soporte")
        st.info("💡 Mostrando datos del archivo de respaldo en el repositorio: 'datos_prueba_dashboard.xlsx'")
    except FileNotFoundError:
        st.warning("⚠️ Por favor, sube un archivo de Excel o añade 'datos_prueba_dashboard.xlsx' a tu repositorio de GitHub.")

# 3. Procesar datos y renderizar gráfica (Filtro Anti-Unnamed)
if df is not None:
    # 🚨 LIMPIEZA CRÍTICA: Eliminar columnas 'Unnamed' que rompen los selectores
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # Mostrar tabla si el usuario quiere auditar datos
    if st.checkbox("Mostrar tabla de datos limpios"):
        st.dataframe(df)

    st.subheader("📈 Volumen de Tickets por Módulo y Estado")
    
    # Validar que existan las columnas correctas antes de graficar
    columnas_requeridas = ["Módulo / Sistema", "Estado"]
    if all(col in df.columns for col in columnas_requeridas):
        fig_barras = px.histogram(
            df, 
            x="Módulo / Sistema", 
            color="Estado", 
            barmode="group",
            title="Tickets Totales por Plataforma",
            labels={"Módulo / Sistema": "Plataforma/Módulo", "count": "Cantidad de Tickets"},
            color_discrete_map={"Resuelto": "#2ecc71", "Pendiente": "#e74c3c"}
        )
        
        fig_barras.update_layout(
            xaxis_title="Sistemas Afectados",
            yaxis_title="Número de Incidentes",
            legend_title="Estatus del Ticket"
        )
        
        st.plotly_chart(fig_barras, use_container_width=True)
    else:
        # Si las columnas no se llaman exactamente así en tu Excel real, te permite elegirlas de forma segura
        st.info("Estructura de columnas diferente detectada. Selecciona manualmente:")
        columnas_disponibles = df.columns.tolist()
        eje_x = st.selectbox("Selecciona columna para Eje X (Categoría):", columnas_disponibles)
        color_col = st.selectbox("Selecciona columna para Agrupación/Color:", columnas_disponibles)
        
        fig_dinamica = px.histogram(df, x=eje_x, color=color_col, barmode="group")
        st.plotly_chart(fig_dinamica, use_container_width=True)