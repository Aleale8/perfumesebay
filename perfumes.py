import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. CONFIGURACIÓN Y CARGA DE DATOS ---
st.set_page_config(page_title="Perfumes eBay - Proyecto Final", layout="wide")

@st.cache_data
def cargar_datos():
    try:
        # Cargar archivos
        df_m = pd.read_csv('ebay_mens_perfume.csv')
        df_w = pd.read_csv('ebay_womens_perfume.csv')
        
        # Etiquetar género
        df_m['Genero'] = 'Hombre'
        df_w['Genero'] = 'Mujer'
        
        # Unir
        df_unido = pd.concat([df_m, df_w], ignore_index=True)
        
        # Renombrar columnas al Español
        df_unido = df_unido.rename(columns={
            'brand': 'Marca', 
            'title': 'Titulo', 
            'price': 'Precio_Texto', 
            'available': 'Disponibles', 
            'sold': 'Vendidos_Texto', 
            'itemLocation': 'Ubicacion'
        })
        return df_unido
    except FileNotFoundError:
        return None

# Funciones de limpieza
def limpiar_precio(texto):
    if pd.isna(texto): return 0.0
    # Deja solo números y punto decimal
    texto_limpio = ''.join(filter(lambda x: x.isdigit() or x == '.', str(texto)))
    try: return float(texto_limpio)
    except: return 0.0

def limpiar_vendidos(texto):
    if pd.isna(texto): return 0
    # Deja solo números
    texto_limpio = ''.join(filter(str.isdigit, str(texto)))
    return int(texto_limpio) if texto_limpio else 0

# Ejecutar carga
df = cargar_datos()

# Validar carga
if df is not None:
    df['Precio'] = df['Precio_Texto'].apply(limpiar_precio)
    df['Vendidos'] = df['Vendidos_Texto'].apply(limpiar_vendidos)
else:
    st.error("⚠️ Error Crítico: No se encuentran los archivos CSV en la carpeta.")
    st.stop()


# --- 2. BARRA LATERAL (FILTROS) ---
st.sidebar.title("🔍 Panel de Control")
st.sidebar.markdown("Filtros globales para el análisis.")

# Filtro de Género
genero_selec = st.sidebar.radio("Género:", ["Ambos", "Hombre", "Mujer"])

# Aplicar filtro global a los datos
if genero_selec == "Hombre":
    df_global = df[df['Genero'] == 'Hombre']
elif genero_selec == "Mujer":
    df_global = df[df['Genero'] == 'Mujer']
else:
    df_global = df


# --- 3. CONTENIDO PRINCIPAL ---

# Encabezado y Bienvenida
with st.container():
    st.markdown("""
        <div style='
            background-color: #FEEFEF; 
            padding: 30px; 
            border-radius: 15px; 
            border: 2px solid #6F4E37;
            box-shadow: 5px 5px 15px rgba(0, 0, 0, 0.1);
        '>
            <h1 style='text-align: center; color: #6F4E37; font-family: Georgia, serif; font-size: 2.5em;'>
                ✨ Análisis de Mercado de Perfumes eBay 💖
            </h1>
            <p style='text-align: center; font-size: 1.2em; color: #333333; font-family: Georgia, serif; margin-top: 10px;'>
                Bienvenido a la herramienta de visualización interactiva. Utiliza los filtros de la izquierda para explorar datos de perfumes de hombre y mujer. 🐰
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---") 

    # KPIs / Métricas
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Productos", df_global.shape[0])
    kpi2.metric("Precio Promedio", f"${df_global['Precio'].mean():.2f}")
    kpi3.metric("Total Ventas", f"{df_global['Vendidos'].sum():,.0f}")
    kpi4.metric("Marcas Registradas", df_global['Marca'].nunique())
    
    st.divider()

# --- SECCIÓN GRÁFICA 1: TORTA (PIE CHART) ---
st.subheader("1. Composición del Mercado")
col_pie1, col_pie2 = st.columns([1, 2])

with col_pie1:
    st.info("Este gráfico visualiza la proporción de productos en la base de datos según el género seleccionado.")

with col_pie2:
    if genero_selec == "Ambos":
        # GRÁFICO 1: TORTA
        fig_pie = px.pie(
            df_global, 
            names='Genero', 
            title='Distribución por Género',
            color='Genero',
            color_discrete_map={'Hombre':'#3366CC', 'Mujer':'#FF66B2'},
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning(f"Estás viendo solo datos de **{genero_selec}**. Selecciona 'Ambos' para ver el gráfico de torta comparativo.")

st.divider()

# --- SECCIÓN GRÁFICA 2: BARRAS (BAR CHART) ---
st.subheader("2. Ranking de Ventas")
col_bar1, col_bar2 = st.columns([1, 3])

with col_bar1:
    st.markdown("**Explora las marcas líderes.**")
    lista_marcas = sorted(df_global['Marca'].astype(str).unique())
    # Selector de marca
    marca_ventas = st.selectbox("Selecciona una Marca:", ["Todas"] + lista_marcas)

with col_bar2:
    # GRÁFICO 2: BARRAS
    if marca_ventas == "Todas":
        data_ventas = df_global.groupby('Marca')['Vendidos'].sum().sort_values(ascending=False).head(10).reset_index()
        fig_bar = px.bar(
            data_ventas, x='Marca', y='Vendidos', color='Vendidos', 
            title="Top 10 Marcas Más Vendidas", color_continuous_scale='Viridis'
        )
    else:
        data_ventas = df_global[df_global['Marca'] == marca_ventas].sort_values('Vendidos', ascending=False).head(10)
        fig_bar = px.bar(
            data_ventas, x='Vendidos', y='Titulo', orientation='h', 
            title=f"Top Productos: {marca_ventas}", color='Vendidos'
        )
    
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# --- SECCIÓN GRÁFICA 3, 4 y 5: PESTAÑAS (TABS) ---
st.subheader("3. Análisis Detallado de Precios")

# Definimos 3 pestañas: Cajas, Puntos y Violín
tab1, tab2, tab3 = st.tabs(["📊 Comparador (Cajas)", "📍 Distribución (Puntos)", "🎻 Densidad (Violín)"])

# PESTAÑA 1: BOX PLOT
with tab1:
    st.markdown("**Comparativa de precios entre marcas**")
    top_marcas_default = df_global['Marca'].value_counts().head(5).index.tolist()
    marcas_comparar = st.multiselect("Marcas a comparar:", options=lista_marcas, default=top_marcas_default, key="multi_box")
    
    if marcas_comparar:
        df_comp = df_global[df_global['Marca'].isin(marcas_comparar)]
        # GRÁFICO 3: BOX PLOT
        fig_box = px.box(
            df_comp, x='Marca', y='Precio', color='Marca', 
            points="outliers", 
            title="Distribución de Precios (Box Plot)"
        )
        st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.info("Selecciona al menos una marca para comparar.")

# PESTAÑA 2: STRIP PLOT (PUNTOS)
with tab2:
    st.markdown("**Visualización de densidad de precios (Puntos)**")
    top_10_marcas = df_global['Marca'].value_counts().head(10).index.tolist()
    marcas_puntos = st.multiselect(
        "Selecciona Marcas:", 
        options=lista_marcas, 
        default=top_10_marcas,
        key="multi_strip"
    )
    
    if marcas_puntos:
        df_strip = df_global[df_global['Marca'].isin(marcas_puntos)]
        # GRÁFICO 4: STRIP PLOT
        fig_strip = px.strip(
            df_strip, x='Marca', y='Precio', color='Genero', 
            hover_data=['Titulo', 'Vendidos'],
            title="Detalle de Puntos por Marca",
            stripmode='overlay'
        )
        fig_strip.update_layout(height=500)
        fig_strip.update_traces(marker=dict(size=5, opacity=0.6))
        st.plotly_chart(fig_strip, use_container_width=True)
    else:
        st.warning("Selecciona marcas para visualizar los puntos.")

# PESTAÑA 3: VIOLIN PLOT (NUEVO)
with tab3:
    st.markdown("**Densidad de Precios por Género (Violín)**")
    
    # Filtramos extremos para ver mejor la forma
    df_violin = df_global[df_global['Precio'] < 300]
    
    if not df_violin.empty:
        # GRÁFICO 5: VIOLIN PLOT
        fig_violin = px.violin(
            df_violin, y="Precio", x="Genero", color="Genero",
            box=True, points="all",
            hover_data=['Marca', 'Titulo'],
            title="Densidad de Precios: Hombres vs Mujeres"
        )
        fig_violin.update_layout(yaxis_title="Precio ($)")
        st.plotly_chart(fig_violin, use_container_width=True)
        st.caption("Nota: Se han filtrado productos > $300 para mejorar la visualización.")
    else:
        st.warning("No hay suficientes datos para generar el gráfico.")

# --- DATOS FINALES ---
with st.expander("Ver Base de Datos Completa"):
    st.dataframe(df_global)
