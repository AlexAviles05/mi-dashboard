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
        
        header_row_idx = None
        for i, row in enumerate(df_ent_raw.values[:10]):
            row_str = [str(x).strip().lower() for x in row]
            if 'plaza' in row_str:
                header_row_idx = i
                break
        
        if header_row_idx is not None:
            df_entrenamiento = pd.read_excel(uploaded_file, sheet_name="CONCENTRADO", header=header_row_idx + 1)
            df_entrenamiento.columns = df_entrenamiento.columns.astype(str).str.strip().str.lower()
            df_entrenamiento = df_entrenamiento.dropna(subset=['plaza'])
        else:
            df_ent_raw.columns = df_ent_raw.columns.astype(str).str.strip().str.lower()
            if 'plaza' in df_ent_raw.columns:
                df_entrenamiento = df_ent_raw.dropna(subset=['plaza'])

        # BLINDAJE ANTIDUPLICADOS DESDE LA CARGA RAÍZ
        if df_vacantes is not None and 'plaza' in df_vacantes.columns:
            df_vacantes['plaza'] = df_vacantes['plaza'].astype(str).str.strip().str.upper().str.replace('Í', 'I', regex=False)

        if df_entrenamiento is not None:
            if 'plaza' in df_entrenamiento.columns:
                df_entrenamiento['plaza'] = df_entrenamiento['plaza'].astype(str).str.strip().str.upper().str.replace('Í', 'I', regex=False)
            if 'zona' in df_entrenamiento.columns:
                df_entrenamiento['zona'] = (
                    df_entrenamiento['zona']
                    .fillna("SIN ZONA")
                    .astype(str)
                    .str.strip()
                    .str.upper()
                    .str.replace('Í', 'I', regex=False)
                    .str.replace('Á', 'A', regex=False)
                    .str.replace('É', 'E', regex=False)
                    .str.replace('Ó', 'O', regex=False)
                    .str.replace('Ú', 'U', regex=False)
                )

    except Exception as e:
        st.sidebar.error(f"Error al procesar las pestañas del Excel: {e}")

# 3. Renderizar Dashboard
if df_vacantes is not None and df_entrenamiento is not None:
    
    if 'plaza' in df_vacantes.columns and 'plaza' in df_entrenamiento.columns:
        
        # Combinar plazas homologadas
        plazas_totales = sorted(list(set(df_vacantes['plaza'].dropna().unique().tolist() + df_entrenamiento['plaza'].dropna().unique().tolist())))
        plaza_seleccionada = st.sidebar.multiselect("Filtrar por Plaza:", plazas_totales, default=plazas_totales)
        
        estatus_col = 'estatus' if 'estatus' in df_vacantes.columns else df_vacantes.columns[0]
        estatus_disponibles = sorted(df_vacantes[estatus_col].dropna().unique().tolist())
        estatus_seleccionado = st.sidebar.multiselect("Estatus de Vacante:", estatus_disponibles, default=estatus_disponibles)

        # Filtrar sets de datos
        df_vac_filtrado = df_vacantes[
            (df_vacantes['plaza'].isin(plaza_seleccionada)) & 
            (df_vacantes[estatus_col].isin(estatus_seleccionado))
        ]
        df_ent_filtrado = df_entrenamiento[df_entrenamiento['plaza'].isin(plaza_seleccionada)].copy()

        # --- SECCIÓN 1: METRICS ---
        st.subheader("📌 Resumen Ejecutivo General")
        col1, col2, col3, col4 = st.columns(4)
        
        dias_col =
