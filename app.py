import pandas as pd
from datetime import datetime
import streamlit as st

# --- Cargar archivo Excel ---
@st.cache_data
def cargar_datos():
    return pd.read_excel("Mercaderia del Local.xlsx")

df = cargar_datos()

# --- Inicializar estado de los productos (checkboxes) ---
if "estado_productos" not in st.session_state:
    st.session_state.estado_productos = {str(row["Codigo"]): False for _, row in df.iterrows()}

# --- Título ---
st.title("📦 Gestión de Mercadería")

# --- Filtros ---
clasificaciones = ["Todas"] + sorted(df["Clasificacion"].dropna().unique())
locales = ["Todos"] + sorted(df["Local"].dropna().unique())

col1, col2 = st.columns(2)
filtro_clasificacion = col1.selectbox("Filtrar por clasificación", clasificaciones)
filtro_local = col2.selectbox("Filtrar por local", locales)
busqueda = st.text_input("🔍 Buscar producto por nombre o código")

# --- Aplicar filtros ---
df_filtrado = df.copy()
if filtro_clasificacion != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Clasificacion"] == filtro_clasificacion]
if filtro_local != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Local"] == filtro_local]
if busqueda:
    busqueda = busqueda.strip().lower()
    df_filtrado = df_filtrado[
        df_filtrado["Descripcion"].str.lower().str.contains(busqueda, na=False) |
        df_filtrado["Codigo"].astype(str).str.contains(busqueda)
    ]

# --- Mostrar productos con checkboxes ---
st.markdown("### ✅ Productos a pedir")
for _, row in df_filtrado.iterrows():
    key = str(row["Codigo"])
    descripcion = f'{row["Descripcion"]} ({row["Codigo"]}) - {row["Clasificacion"]} - {row["Local"]}'
    st.session_state.estado_productos[key] = st.checkbox(
        descripcion,
        value=st.session_state.estado_productos.get(key, False),
        key=key
    )

# --- Botones ---
col3, col4 = st.columns(2)

if col3.button("🧹 Limpiar selección"):
    for key in st.session_state.estado_productos:
        st.session_state.estado_productos[key] = False
    st.experimental_rerun()

# --- Exportar selección a TXT ---
productos_seleccionados = df[df["Codigo"].astype(str).isin(
    [k for k, v in st.session_state.estado_productos.items() if v]
)]
if not productos_seleccionados.empty:
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    contenido_txt = "\n".join(
        f'{row["Codigo"]} - {row["Descripcion"]} ({row["Clasificacion"]} - {row["Local"]})'
        for _, row in productos_seleccionados.iterrows()
    )
    archivo_txt = f"productos_a_pedir_{fecha_hoy}.txt"
    st.download_button("⬇️ Descargar selección en .txt", contenido_txt, file_name=archivo_txt)

# --- Agregar nuevo producto ---
st.markdown("### ➕ Agregar nuevo producto")

with st.form("formulario_agregar"):
    nuevo_codigo = st.text_input("🔢 Código")
    nueva_descripcion = st.text_input("📝 Descripción")
    nueva_clasificacion = st.text_input("🏷️ Clasificación")
    nuevo_local = st.text_input("📍 Local")
    submitted = st.form_submit_button("Agregar producto")

    if submitted:
        if not nuevo_codigo or not nueva_descripcion:
            st.warning("⚠️ El Código y la Descripción son obligatorios.")
        elif nuevo_codigo in df["Codigo"].astype(str).values:
            st.error("❌ Ya existe un producto con ese código.")
        else:
            nuevo_producto = {
                "Codigo": nuevo_codigo,
                "Descripcion": nueva_descripcion,
                "Clasificacion": nueva_clasificacion,
                "Local": nuevo_local
            }
            df = pd.concat([df, pd.DataFrame([nuevo_producto])], ignore_index=True)
            df.to_excel("Mercaderia del Local.xlsx", index=False)
            st.success("✅ Producto agregado y guardado correctamente.")
            st.experimental_rerun()

# --- Eliminar producto por código con confirmación ---
st.markdown("### 🗑️ Eliminar producto por código")

with st.form("formulario_eliminar"):
    codigo_a_eliminar = st.text_input("🔍 Ingresá el código del producto a eliminar")
    producto_encontrado = df[df["Codigo"].astype(str) == codigo_a_eliminar]
    if not producto_encontrado.empty:
        st.info("🔎 Producto encontrado:")
        st.dataframe(producto_encontrado, use_container_width=True)
    confirmar = st.checkbox("✅ Confirmo que deseo eliminar este producto")
    eliminar = st.form_submit_button("Eliminar producto")

    if eliminar:
        if not codigo_a_eliminar:
            st.warning("⚠️ Tenés que ingresar un código.")
        elif producto_encontrado.empty:
            st.error("❌ No se encontró ningún producto con ese código.")
        elif not confirmar:
            st.warning("⚠️ Tenés que confirmar antes de eliminar.")
        else:
            df = df[df["Codigo"].astype(str) != codigo_a_eliminar]
            df.to_excel("Mercaderia del Local.xlsx", index=False)
            st.success(f"✅ Producto con código {codigo_a_eliminar} eliminado.")
            st.experimental_rerun()
