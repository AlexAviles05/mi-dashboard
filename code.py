import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la Página Web
st.set_page_config(
    page_title="Ozaru - Dashboard Control de KPIs", 
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

if uploaded_file is not None:
    try:
        # --- PROCESAR HOJA 1 (VACANTES) ---
        df_vac_raw = pd.read_excel(uploaded_file, sheet_name="Hoja1")
        df_vac_raw.columns = df_vac_raw.columns.astype(str).str.strip().str.lower()
        
        if 'plaza' in df_vac_raw.columns:
            df_vacantes = df_vac_raw.dropna(subset=['plaza'])
            df_vacantes = df_vacantes[~df_vacantes['plaza'].astype(str).str.contains('seguimiento|contrataciones|requisiciones', na=False)]
        else:
            # Si no está en la fila 1, buscarla dinámicamente
            for i, row in enumerate(df_vac_raw.values[:5]):
                row_str = [str(x).strip().lower() for x in row]
                if 'plaza' in row_str:
                    df_vacantes = pd.read_excel(uploaded_file, sheet_name="Hoja1", header=i+1)
                    df_vacantes.columns = df_vacantes.columns.astype(str).str.strip().str.lower()
                    df_vacantes = df_vacantes.dropna(subset=['plaza'])
                    df_vacantes = df_vacantes[~df_vacantes['plaza'].astype(str).str.contains('seguimiento|contrataciones|requisiciones', na=False)]
                    break

        # --- PROCESAR HOJA CONCENTRADO (ENTRENAMIENTO) ---
        df_ent_raw = pd.read_excel(uploaded_file, sheet_name="CONCENTRADO")
        
        # BUSCADOR DINÁMICO DE ENCABEZADOS DE QA:
        header_row_idx = None
        for i, row in enumerate(df_ent_raw.values[:10]):  # Escanea las primeras 10 filas
            row_str = [str(x).strip().lower() for x in row]
            if 'plaza' in row_str:
                header_row_idx = i
                break
        
        if header_row_idx is not None:
            # Recargar la pestaña usando la fila exacta donde se encontró "Plaza"
            df_entrenamiento = pd.read_excel(uploaded_file, sheet_name="CONCENTRADO", header=header_row_idx + 1)
            df_entrenamiento.columns = df_entrenamiento.columns.astype(str).str.strip().str.lower()
            df_entrenamiento = df_entrenamiento.dropna(subset=['plaza'])
        else:
            # Intento de respaldo a la fuerza si falló el buscador
            df_ent_raw.columns = df_ent_raw.columns.astype(str).str.strip().str.lower()
            if 'plaza' in df_ent_raw.columns:
                df_entrenamiento = df_ent_raw.dropna(subset=['plaza'])

    except Exception as e:
        st.sidebar.error(f"Error al procesar las pestañas del Excel: {e}")

# 3. Renderizar Dashboard SOLO si la estructura pasó el escaneo
if df_vacantes is not None and df_entrenamiento is not None:
    
    if 'plaza' in df_vacantes.columns and 'plaza' in df_entrenamiento.columns:
        
        # Selectores dinámicos basados en columnas normalizadas
        plazas_disponibles = sorted(df_vacantes['plaza'].dropna().unique().tolist())
        plaza_seleccionada = st.sidebar.multiselect("Filtrar por Plaza:", plazas_disponibles, default=plazas_disponibles)
        
        estatus_col = 'estatus' if 'estatus' in df_vacantes.columns else df_vacantes.columns[0]
        estatus_disponibles = sorted(df_vacantes[estatus_col].dropna().unique().tolist())
        estatus_seleccionado = st.sidebar.multiselect("Estatus de Vacante:", estatus_disponibles, default=estatus_disponibles)

        # Filtrado en tiempo real
        df_vac_filtrado = df_vacantes[
            (df_vacantes['plaza'].isin(plaza_seleccionada)) & 
            (df_vacantes[estatus_col].isin(estatus_seleccionado))
        ]
        df_ent_filtrado = df_entrenamiento[df_entrenamiento['plaza'].isin(plaza_seleccionada)]

        # --- SECCIÓN 1: METRICS ---
        st.subheader("📌 Resumen Ejecutivo de Reclutamiento")
        col1, col2, col3, col4 = st.columns(4)
        
        dias_col = [c for c in df_vac_filtrado.columns if 'días vacantes' in c or 'dias' in c]
        dias_col = dias_col[0] if dias_col else None
        
        with col1:
            st.markdown(f'<div class="metric-box"><div class="metric-title">Total Vacantes</div><div class="metric-value">{len(df_vac_filtrado)}</div></div>', unsafe_allow_html=True)
        with col2:
            dias_promedio = int(df_vac_filtrado[dias_col].mean()) if dias_col and not df_vac_filtrado[dias_col].dropna().empty else 0
            st.markdown(f'<div class="metric-box"><div class="metric-title">Días Vacantes Promedio</div><div class="metric-value">{dias_promedio} días</div></div>', unsafe_allow_html=True)
        with col3:
            en_sies = len(df_vac_filtrado[df_vac_filtrado[estatus_col].astype(str).str.upper() == 'SIES'])
            st.markdown(f'<div class="metric-box"><div class="metric-title">Vacantes en SIES</div><div class="metric-value">{en_sies}</div></div>', unsafe_allow_html=True)
        with col4:
            en_atraccion = len(df_vac_filtrado[df_vac_filtrado[estatus_col].astype(str).str.upper() == 'PROCESO DE ATRACCIÓN'])
            st.markdown(f'<div class="metric-box"><div class="metric-title">En Reclutamiento/Atracción</div><div class="metric-value">{en_atraccion}</div></div>', unsafe_allow_html=True)

        st.markdown("---")

        # --- SECCIÓN 2: GRÁFICAS ---
        col_graf1, col_graf2 = st.columns(2)
        
        with col_graf1:
            st.subheader("💼 Estatus de Requisiciones por Plaza")
            fig_vac = px.bar(
                df_vac_filtrado, 
                x="plaza", 
                color=estatus_col,
                barmode="stack",
                title="Distribución de Requerimientos Operativos",
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig_vac.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_vac, use_container_width=True)
            
        with col_graf2:
            st.subheader("🏃‍♂️ Control de Bajas en Entrenamiento")
            tipo_baja_col = [c for c in df_ent_filtrado.columns if 'tipo de baja' in c or 'baja' in c]
            tipo_baja_col = tipo_baja_col[0] if tipo_baja_col else None
            
            if tipo_baja_col and not df_ent_filtrado[tipo_baja_col].dropna().empty:
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
                st.info("No se detectaron columnas o datos válidos de bajas en esta sección.")

        st.markdown("---")

        # --- SECCIÓN 3: DETALLE POR TIENDA ---
        tienda_col = 'tienda' if 'tienda' in df_vac_filtrado.columns else df_vac_filtrado.columns[1]
        tipo_vac_col = [c for c in df_vac_filtrado.columns if 'apertura' in c or 'rotación' in c or 'cuadrilla' in c]
        tipo_vac_col = tipo_vac_col[0] if tipo_vac_col else None

        if tipo_vac_col:
            st.subheader("🏬 Apertura vs Rotación por Tienda/Sucursal")
            fig_tipo = px.histogram(
                df_vac_filtrado, 
                x=tienda_col, 
                color=tipo_vac_col,
                barmode="group",
                title="Naturaleza de las Vacantes Vigentes por Sucursal"
            )
            fig_tipo.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_tickangle=-45)
            st.plotly_chart(fig_tipo, use_container_width=True)

        # Expansores de datos
        with st.expander("🔍 Ver Tablas Completas de Información Limpia"):
            tab1, tab2 = st.tabs(["📋 Requisiciones y Vacantes Activas", "🎓 Detalle de Alumnos en Entrenamiento"])
            with tab1:
                st.dataframe(df_vac_filtrado, use_container_width=True)
            with tab2:
                st.dataframe(df_ent_filtrado, use_container_width=True)
    else:
        st.error("❌ Estructura crítica ausente. Asegúrate de que ambas pestañas del Excel contengan una columna identificada como 'Plaza'.")
else:
    # Mensaje amigable de bienvenida antes de que se suba el archivo
    st.info("👋 ¡Hola! Para desplegar la maqueta de gráficos y KPIs, por favor arrastra el archivo 'Bitácora KPIS.xlsx' en la sección de la barra lateral izquierda.")