import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la Página Web (Diseño Extenso/Wide)
st.set_page_config(
    page_title="People analytics HR - Dashboard Control de KPIs", 
    page_icon="📊", 
    layout="wide"
)

# Estilo personalizado para las tarjetas de métricas (KPIS)
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

# 2. Configuración e Ingesta de Datos (Barra Lateral)
st.sidebar.image("https://via.placeholder.com/150x50/1e293b/38bdf8?text=Ozaru+One", width=150) # Cambiar por tu logo real
st.sidebar.header("🎯 Filtros Globales")

uploaded_file = st.sidebar.file_uploader("Actualizar archivo de Bitácora (Excel)", type=["xlsx"])

# Dataframes por defecto (Carga segura)
df_vacantes = None
df_entrenamiento = None

if uploaded_file is not None:
    try:
        df_vacantes = pd.read_excel(uploaded_file, sheet_name=0) # Hoja 1
        df_entrenamiento = pd.read_excel(uploaded_file, sheet_name="CONCENTRADO", header=2) # Encabezados reales fila 3
    except Exception as e:
        st.sidebar.error(f"Error al leer las pestañas: {e}")
else:
    # Respaldos usando los CSV procesados en tu entorno
    try:
        df_vacantes = pd.read_csv("Bitácora KPIS.xlsx - Hoja1.csv")
        # Limpiar filas informativas al final de la Hoja1
        df_vacantes = df_vacantes.dropna(subset=['PLAZA'])
        df_vacantes = df_vacantes[~df_vacantes['PLAZA'].str.contains('SEGUIMIENTO|CONTRATACIONES|REQUISICIONES', na=False)]
        
        # Cargar concentrado saltando las filas de títulos decorativos
        df_entrenamiento = pd.read_csv("Bitácora KPIS.xlsx - CONCENTRADO.csv", header=1)
        df_entrenamiento.columns = df_entrenamiento.iloc[0] # Forzar fila de nombres reales
        df_entrenamiento = df_entrenamiento[1:].dropna(subset=['Plaza'])
    except Exception:
        st.warning("⚠️ Esperando archivo físico. Por favor sube 'Bitácora KPIS.xlsx' en la barra lateral.")

# 3. Construcción del Dashboard Interactivo
if df_vacantes is not None and df_entrenamiento is not None:
    
    # Filtros dinámicos en barra lateral basados en tus columnas reales
    plazas_disponibles = sorted(df_vacantes['PLAZA'].dropna().unique().tolist())
    plaza_seleccionada = st.sidebar.multiselect("Filtrar por Plaza:", plazas_disponibles, default=plazas_disponibles)
    
    estatus_disponibles = sorted(df_vacantes['ESTATUS'].dropna().unique().tolist())
    estatus_seleccionado = st.sidebar.multiselect("Estatus de Vacante:", estatus_disponibles, default=estatus_disponibles)

    # Filtrar dataframes basados en la selección del usuario
    df_vac_filtrado = df_vacantes[
        (df_vacantes['PLAZA'].isin(plaza_seleccionada)) & 
        (df_vacantes['ESTATUS'].isin(estatus_seleccionado))
    ]
    
    df_ent_filtrado = df_entrenamiento[df_entrenamiento['Plaza'].isin(plaza_seleccionada)]

    # --- SECCIÓN 1: MAQUETA DE TARJETAS (KPI METRICS) ---
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

    # --- SECCIÓN 2: GRÁFICAS DEL REPORTE EXTENSO ---
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
        # Analizar tipos de baja en la bitácora de entrenamiento
        if 'Tipo de baja \n(No show o Entrenamiento)' in df_ent_filtrado.columns:
            df_bajas = df_ent_filtrado['Tipo de baja \n(No show o Entrenamiento)'].dropna().value_counts().reset_index()
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
            st.info("No se encontraron registros de columnas de bajas en este set de datos.")

    st.markdown("---")

    # --- SECCIÓN 3: MONITOREO DE TIENDAS Y DETALLE ---
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

    # Tablas de auditoría al fondo de la maqueta
    with st.expander("🔍 Ver Tablas Completas de Información Limpia"):
        tab1, tab2 = st.tabs(["📋 Requisiciones y Vacantes Activas", "🎓 Detalle de Alumnos en Entrenamiento"])
        with tab1:
            st.dataframe(df_vac_filtrado, use_container_width=True)
        with tab2:
            st.dataframe(df_ent_filtrado, use_container_width=True)