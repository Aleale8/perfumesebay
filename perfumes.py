import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Perfumes eBay - Proyecto Final", layout="wide")

def cargar_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"⚠️ Sin estilos: No se encontró '{file_name}'.")

cargar_css('estilo.css')

# --- CARGA Y LIMPIEZA DE DATOS ---
@st.cache_data
def cargar_datos():
    try:
        df_m = pd.read_csv('ebay_mens_perfume.csv').assign(Genero='Hombre')
        df_w = pd.read_csv('ebay_womens_perfume.csv').assign(Genero='Mujer')
        df = pd.concat([df_m, df_w], ignore_index=True)
        
        return df.rename(columns={
            'brand': 'Marca', 'title': 'Titulo', 'price': 'Precio_Texto', 
            'available': 'Disponibles', 'sold': 'Vendidos_Texto', 'itemLocation': 'Ubicacion'
        })
    except FileNotFoundError:
        return None

def limpiar_numero(texto, es_float=True):
    if pd.isna(texto): return 0.0 if es_float else 0
    # Extrae solo números y puntos. Si falla, devuelve 0.
    limpio = ''.join(filter(lambda x: x.isdigit() or (x == '.' and es_float), str(texto)))
    try: return float(limpio) if es_float else int(limpio)
    except: return 0.0 if es_float else 0

df = cargar_datos()

if df is None:
    st.error("⚠️ Error Crítico: Faltan los archivos CSV.")
    st.stop()

# Aplicar limpieza
df['Precio'] = df['Precio_Texto'].apply(lambda x: limpiar_numero(x, True))
df['Vendidos'] = df['Vendidos_Texto'].apply(lambda x: limpiar_numero(x, False))

# --- SIDEBAR (FILTROS) ---
st.sidebar.title("Cámara de Esencias 🌸")
st.sidebar.markdown("Panel de Control")
genero_filtro = st.sidebar.radio("Género:", ["Ambos", "Hombre", "Mujer"])

# Filtrado Global
df_global = df if genero_filtro == "Ambos" else df[df['Genero'] == genero_filtro]

# --- INTERFAZ PRINCIPAL ---
st.markdown("""
    <div class="main-header" style='text-align: center; color: #6F4E37;'>
        <h1 style='font-family: Georgia;'>🌸 Análisis de Mercado: Perfumes eBay 🌸</h1>
        <p>Exploración interactiva de precios, ventas y tendencias.</p>
    </div>
    <hr>
""", unsafe_allow_html=True)

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Productos", df_global.shape[0])
col2.metric("Precio Promedio", f"${df_global['Precio'].mean():.2f}")
col3.metric("Total Ventas", f"{df_global['Vendidos'].sum():,.0f}")
col4.metric("Marcas Únicas", df_global['Marca'].nunique())
st.divider()

# --- GRÁFICOS ---

# 1. TORTA (Composición)
st.subheader("1. Composición del Mercado")
c1, c2 = st.columns([1, 2])
c1.info("Proporción de productos según género.")
if genero_filtro == "Ambos":
    fig = px.pie(df_global, names='Genero', title='Distribución por Género', 
                 color='Genero', hole=0.4, color_discrete_map={'Hombre':'#ADC6D1', 'Mujer':'#E49AC2'})
    c2.plotly_chart(fig, use_container_width=True)
else:
    c2.warning("Selecciona 'Ambos' para ver la comparación.")

st.divider()

# 2. BARRAS (Ranking)
st.subheader("2. Ranking de Ventas")
c1, c2 = st.columns([1, 3])
c1.markdown("Explora los líderes en ventas.")
marcas = sorted(df_global['Marca'].astype(str).unique())
marca_sel = c1.selectbox("Marca:", ["Todas"] + marcas)

if marca_sel == "Todas":
    data = df_global.groupby('Marca')['Vendidos'].sum().sort_values(ascending=False).head(10).reset_index()
    fig = px.bar(data, x='Marca', y='Vendidos', color='Vendidos', title="Top 10 Marcas", color_continuous_scale='Teal')
else:
    data = df_global[df_global['Marca'] == marca_sel].sort_values('Vendidos', ascending=False).head(10)
    fig = px.bar(data, x='Vendidos', y='Titulo', orientation='h', title=f"Top Productos: {marca_sel}", color='Vendidos', color_continuous_scale='Teal')
c2.plotly_chart(fig, use_container_width=True)

st.divider()

# 3. ANÁLISIS DE PRECIOS (Pestañas)
st.subheader("3. Análisis Detallado de Precios")
tab1, tab2, tab3 = st.tabs(["📊 Cajas (Comparar)", "📍 Puntos (Detalle)", "🎻 Violín (Densidad)"])

with tab1: # Box Plot
    sel = st.multiselect("Marcas a comparar:", options=marcas, default=df_global['Marca'].value_counts().head(5).index.tolist())
    if sel:
        fig = px.box(df_global[df_global['Marca'].isin(sel)], x='Marca', y='Precio', color='Marca', points="outliers", title="Rangos de Precio")
        st.plotly_chart(fig, use_container_width=True)

with tab2: # Strip Plot
    sel = st.multiselect("Ver puntos de:", options=marcas, default=df_global['Marca'].value_counts().head(10).index.tolist(), key="strip")
    if sel:
        fig = px.strip(df_global[df_global['Marca'].isin(sel)], x='Marca', y='Precio', color='Genero', hover_data=['Titulo'], stripmode='overlay')
        st.plotly_chart(fig, use_container_width=True)

with tab3: # Violin Plot
    df_clean = df_global[df_global['Precio'] < 300] # Filtro visual
    if not df_clean.empty:
        fig = px.violin(df_clean, y="Precio", x="Genero", color="Genero", box=True, points="outliers", title="Densidad de Precios")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Sin datos suficientes.")

with st.expander("Ver Datos Crudos"):
    st.dataframe(df_global)
