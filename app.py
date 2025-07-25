import streamlit as st
import pandas as pd

# Cargar archivo Excel
@st.cache_data
def cargar_datos():
    df = pd.read_excel("Mercaderia del Local.xlsx", sheet_name="Hoja1")
    df = df[['Codigo', 'Descripcion', 'Clasificacion', 'Local']].drop_duplicates()
    return df

df = cargar_datos()

st.title("🛒 Lista de Productos a Pedir")

# Filtros
clasificaciones = st.multiselect("Filtrar por Clasificación", options=sorted(df['Clasificacion'].unique()))
locales = st.multiselect("Filtrar por Ubicación (Local)", options=sorted(df['Local'].unique()))

# Aplicar filtros
df_filtrado = df.copy()
busqueda = st.text_input("Buscar producto por nombre")
if busqueda:
    df_filtrado = df_filtrado[df_filtrado['Descripcion'].str.contains(busqueda, case=False)]
if clasificaciones:
    df_filtrado = df_filtrado[df_filtrado['Clasificacion'].isin(clasificaciones)]
if locales:
    df_filtrado = df_filtrado[df_filtrado['Local'].isin(locales)]

# Estado de productos
if "productos_pedidos" not in st.session_state:
    st.session_state.productos_pedidos = {}

# Botón para limpiar selección sin usar experimental_rerun
if st.button("🧹 Limpiar selección de productos"):
    for key in st.session_state.productos_pedidos:
        st.session_state.productos_pedidos[key] = False


st.subheader("🧾 Productos filtrados")
for _, row in df_filtrado.iterrows():
    key = str(row['Codigo'])
    estado = st.session_state.productos_pedidos.get(key, False)
    check = st.checkbox(f"[{row['Codigo']}] {row['Descripcion']}", value=estado, key=key)
    st.session_state.productos_pedidos[key] = check

# Mostrar resumen
st.markdown("---")
st.subheader("📦 Productos marcados para pedir")
seleccionados = [k for k, v in st.session_state.productos_pedidos.items() if v]
df_seleccionados = df[df['Codigo'].astype(str).isin(seleccionados)]
st.write(f"🧮 Total marcados: {len(seleccionados)} / {len(df_filtrado)}")

st.dataframe(df_seleccionados[['Codigo', 'Descripcion', 'Clasificacion', 'Local']])

# Exportar productos marcados a .txt
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
