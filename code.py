import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la Página Web
st.set_page_config(
    page_title="People analytics HR - Dashboard Control de KPIs", 
    page_icon="📊", 
    layout="wide"
)

# Estilo personalizado para las tarjetas de métricas
st.markdown("""
    <style>
    .metric-box {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #38bdf8;
        color: #f8fafc;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        text-align: center;
    }
    .metric-title { font-size: 16px; font-weight: bold; color: #94a3b8; }
    .metric-value { font-size: 32px; font-weight: bold; color: #38bdf8; margin-top: 5px; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Panel de Control Operativo - KPIs & Entrenamiento")
st.markdown("Consumo de datos automatizado desde *Bitácora KPIS.xlsx*")

# 2. Configuración en la Barra Lateral
st.sidebar.header("🎯 Filtros Globales")
uploaded_file = st.sidebar.file_uploader("Actualizar archivo de Bitácora (Excel)", type=["xlsx"])

df_vacantes = None
df_entrenamiento = None

# Intentar leer desde el archivo subido por el usuario
if uploaded_file is not None:
    try:
        df_vacantes = pd.read_excel(uploaded_file, sheet_name="Hoja1")
        df_entrenamiento = pd.read_excel(uploaded_file, sheet_name="CONCENTRADO", header=1)
        
        # Limpieza inicial de filas basura del Excel
        df_vacantes = df_vacantes.dropna(subset=['PLAZA'])
        df_vacantes = df_vacantes[~df_vacantes['PLAZA'].astype(str).str.contains('SEGUIMIENTO|CONTRATACIONES|REQUISICIONES', na=False)]
        df_entrenamiento = df_entrenamiento.dropna(subset=['Plaza'])
    except Exception as e:
        st.sidebar.error(f"Error al procesar las pestañas del Excel: {e}")

# 3. Renderizar Dashboard SOLO si los datos ya existen y están listos
if df_vacantes is not None and df_entrenamiento is not None:
    
    # Selectores dinámicos en la barra lateral
    plazas_disponibles = sorted(df_vacantes['PLAZA'].dropna().unique().tolist())
    plaza_seleccionada = st.sidebar.multiselect("Filtrar por Plaza:", plazas_disponibles, default=plazas_disponibles)
    
    estatus_disponibles = sorted(df_vacantes['ESTATUS'].dropna().unique().tolist())
    estatus_seleccionado = st.sidebar.multiselect("Estatus de Vacante:", estatus_disponibles, default=estatus_disponibles)

    # Filtrado en tiempo real
    df_vac_filtrado = df_vacantes[
        (df_vacantes['PLAZA'].isin(plaza_seleccionada)) & 
        (df_vacantes['ESTATUS'].isin(estatus_seleccionado))
    ]
    df_ent_filtrado = df_entrenamiento[df_entrenamiento['Plaza'].isin(plaza_seleccionada)]

    # --- SECCIÓN 1: METRICS ---
    st.subheader("📌 Resumen Ejecutivo de Reclutamiento")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_vacantes = len(df_vac_filtrado)
        st.markdown(f'<div class="metric-box"><div class="metric-title">Total Vacantes</div><div class="metric-value">{total_vacantes}</div></div>', unsafe_allow_html=True)
    with col2:
        dias_promedio = int(df_vac_filtrado['DÍAS VACANTES '].mean()) if not df_vac_filtrado['DÍAS VACANTES '].dropna().empty else 0
        st.markdown(f'<div class="metric-box"><div class="metric-title">Días Vacantes Promedio</div><div class="metric-value">{dias_promedio} días</div></div>', unsafe_allow_html=True)
    with col3:
        en_sies = len(df_vac_filtrado[df_vac_filtrado['ESTATUS'] == 'SIES'])
        st.markdown(f'<div class="metric-box"><div class="metric-title">Vacantes en SIES</div><div class="metric-value">{en_sies}</div></div>', unsafe_allow_html=True)
    with col4:
        en_atraccion = len(df_vac_filtrado[df_vac_filtrado['ESTATUS'] == 'PROCESO DE ATRACCIÓN'])
        st.markdown(f'<div class="metric-box"><div class="metric-title">En Reclutamiento/Atracción</div><div class="metric-value">{en_atraccion}</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    # --- SECCIÓN 2: GRÁFICAS ---
    col_graf1, col_graf2 = st.columns(2)
    
    with col_graf1:
        st.subheader("💼 Estatus de Requisiciones por Plaza")
        fig_vac = px.bar(
            df_vac_filtrado, 
            x="PLAZA", 
            color="ESTATUS",
            barmode="stack",
            title="Distribución de Requerimientos Operativos",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_vac.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_vac, use_container_width=True)
        
    with col_graf2:
        st.subheader("🏃‍♂️ Control de Bajas en Entrenamiento")
        tipo_baja_col = 'Tipo de baja \n(No show o Entrenamiento)'
        if tipo_baja_col in df_ent_filtrado.columns:
            df_bajas = df_ent_filtrado[tipo_baja_col].dropna().value_counts().reset_index()
            df_bajas.columns = ['Tipo de Baja', 'Cantidad']
            
            fig_bajas = px.pie(
                df_bajas, 
                values='Cantidad', 
                names='Tipo de Baja', 
                hole=0.4,
                title="Motivos de Deserción en Capacitación",
                color_discrete_sequence=["#e74c3c", "#f39c12", "#3498db"]
            )
            fig_bajas.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_bajas, use_container_width=True)
        else:
            st.info("No se detectaron bajas registradas en las plazas seleccionadas.")

    st.markdown("---")

    # --- SECCIÓN 3: DETALLE POR TIENDA ---
    st.subheader("🏬 Apertura vs Rotación por Tienda/Sucursal")
    fig_tipo = px.histogram(
        df_vac_filtrado, 
        x="TIENDA", 
        color="Apertura/ Rotación / Cuadrilla",
        barmode="group",
        title="Naturaleza de las Vacantes Vigentes por Sucursal"
    )
    fig_tipo.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_tickangle=-45)
    st.plotly_chart(fig_tipo, use_container_width=True)

    # Expansores de auditoría de datos
    with st.expander("🔍 Ver Tablas Completas de Información Limpia"):
        tab1, tab2 = st.tabs(["📋 Requisiciones y Vacantes Activas", "🎓 Detalle de Alumnos en Entrenamiento"])
        with tab1:
            st.dataframe(df_vac_filtrado, use_container_width=True)
        with tab2:
            st.dataframe(df_ent_filtrado, use_container_width=True)

else:
    # Mensaje amigable de bienvenida antes de que se suba el archivo
    st.info("👋 ¡Hola! Para desplegar la maqueta de gráficos y KPIs, por favor arrastra el archivo 'Bitácora KPIS.xlsx' en la sección de la barra lateral izquierda.")