import streamlit as st
import pandas as pd
import json
import os

# -------------------- Configuración --------------------
st.set_page_config(page_title="Lista de Productos", page_icon="🛒", layout="centered")

# -------------------- Archivos --------------------
EXCEL_FILE = "Mercaderia del Local.xlsx"
ESTADO_FILE = "estado_guardado.json"

# -------------------- Funciones --------------------
@st.cache_data
def cargar_datos():
    df = pd.read_excel(EXCEL_FILE, sheet_name="Hoja1")
    df = df[['Codigo', 'Descripcion', 'Clasificacion', 'Local']].drop_duplicates()
    return df

def cargar_estado():
    if os.path.exists(ESTADO_FILE):
        with open(ESTADO_FILE, "r") as f:
            return json.load(f)
    return {}

def guardar_estado(estado):
    with open(ESTADO_FILE, "w") as f:
        json.dump(estado, f)

# -------------------- Carga de datos --------------------
df = cargar_datos()

# -------------------- Estado inicial --------------------
if "productos_pedidos" not in st.session_state:
    st.session_state.productos_pedidos = cargar_estado()

# -------------------- Título --------------------
st.title("🛒 Lista de Productos a Pedir")

# -------------------- Filtros --------------------
clasificaciones = st.multiselect("Filtrar por Clasificación", options=sorted(df['Clasificacion'].unique()))
locales = st.multiselect("Filtrar por Ubicación (Local)", options=sorted(df['Local'].unique()))
busqueda = st.text_input("🔍 Buscar producto por nombre")

df_filtrado = df.copy()
if clasificaciones:
    df_filtrado = df_filtrado[df_filtrado['Clasificacion'].isin(clasificaciones)]
if locales:
    df_filtrado = df_filtrado[df_filtrado['Local'].isin(locales)]
if busqueda:
    busqueda = busqueda.strip().lower()
    df_filtrado = df_filtrado[
        df_filtrado["Descripcion"].str.lower().str.contains(busqueda, na=False) |
        df_filtrado["Codigo"].astype(str).str.contains(busqueda)
    ]

# -------------------- Botón limpiar --------------------
if st.button("🧹 Limpiar selección de productos"):
    for key in st.session_state.productos_pedidos:
        st.session_state.productos_pedidos[key] = False
    guardar_estado(st.session_state.productos_pedidos)
    st.success("Selección borrada correctamente.")

# -------------------- Checkboxes --------------------
st.subheader("🧾 Productos filtrados")

for _, row in df_filtrado.iterrows():
    key = str(row['Codigo'])
    estado_actual = st.session_state.productos_pedidos.get(key, False)
    check = st.checkbox(f"[{row['Codigo']}] {row['Descripcion']}", value=estado_actual, key=key)
    st.session_state.productos_pedidos[key] = check
    guardar_estado(st.session_state.productos_pedidos)

# -------------------- Resultado --------------------
seleccionados = [k for k, v in st.session_state.productos_pedidos.items() if v]
df_seleccionados = df[df['Codigo'].astype(str).isin(seleccionados)]

st.markdown("---")
st.subheader(f"📦 Productos marcados ({len(seleccionados)})")
st.dataframe(df_seleccionados[['Codigo', 'Descripcion', 'Clasificacion', 'Local']])

# -------------------- Botón para descargar TXT --------------------
if not df_seleccionados.empty:
    contenido_txt = "\n".join(
        f"[{row['Codigo']}] {row['Descripcion']} - {row['Clasificacion']} ({row['Local']})"
        for _, row in df_seleccionados.iterrows()
    )
    st.download_button(
        label="⬇️ Descargar lista como .txt",
        data=contenido_txt,
        file_name="productos_a_pedir.txt",
        mime="text/plain"
    )
else:
    st.info("No hay productos marcados para descargar.")
