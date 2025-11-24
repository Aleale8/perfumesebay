import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. CONFIGURACIÓN Y CARGA DE DATOS ---
st.set_page_config(page_title="Perfumes eBay - Proyecto Final", layout="wide")

@st.cache_data
def cargar_datos():
    try:
        df_m = pd.read_csv('ebay_mens_perfume.csv')
        df_w = pd.read_csv('ebay_womens_perfume.csv')
        df_m['Genero'] = 'Hombre'
        df_w['Genero'] = 'Mujer'
        df_unido = pd.concat([df_m, df_w], ignore_index=True)
        df_unido = df_unido.rename(columns={
            'brand': 'Marca', 'title': 'Titulo', 'price': 'Precio_Texto', 
            'available': 'Disponibles', 'sold': 'Vendidos_Texto', 'itemLocation': 'Ubicacion'
        })
        return df_unido
    except FileNotFoundError as e:
        st.error(f"Error: Archivos no encontrados. {str(e)}")
        return None

# Funciones de Limpieza
def limpiar_precio(texto):
    if pd.isna(texto): 
        return 0.0
    texto_limpio = ''.join(filter(lambda x: x.isdigit() or x == '.', str(texto)))
    try: 
        return float(texto_limpio)
    except: 
        return 0.0

def limpiar_vendidos(texto):
    if pd.isna(texto): 
        return 0
    texto_limpio = ''.join(filter(str.isdigit, str(texto)))
    return int(texto_limpio) if texto_limpio else 0

df = cargar_datos()

if df is not None:
    df['Precio'] = df['Precio_Texto'].apply(limpiar_precio)
    df['Vendidos'] = df['Vendidos_Texto'].apply(limpiar_vendidos)
else:
    st.error("Error: No se pudieron cargar los datos. Verifica que los archivos CSV existan.")
    st.stop()

# --- 2. BARRA LATERAL (FILTROS GLOBALES) ---
st.sidebar.title("🔍 Panel de Control")
st.sidebar.markdown("Filtros para analizar el mercado.")

genero_selec = st.sidebar.radio("Género:", ["Ambos", "Hombre", "Mujer"])

# Aplicar filtro global
if genero_selec == "Hombre": 
    df_global = df[df['Genero'] == 'Hombre']
elif genero_selec == "Mujer": 
    df_global = df[df['Genero'] == 'Mujer']
else: 
    df_global = df

# --- 3. CONTENIDO PRINCIPAL ---

# Bienvenida
with st.container():
    st.title("✨ Análisis de Mercado: Perfumes eBay")
    st.markdown("Dashboard interactivo para visualizar tendencias de precios y ventas.")
    
    # Métricas Globales
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Productos", df_global.shape[0])
    
    # Validar que hay datos antes de calcular
    precio_promedio = df_global['Precio'].mean() if len(df_global) > 0 else 0
    col2.metric("Precio Promedio", f"${precio_promedio:.2f}")
    
    vendidos_total = df_global['Vendidos'].sum() if len(df_global) > 0 else 0
    col3.metric("Total Ventas", f"{vendidos_total:,.0f}")
    
    marcas_unicas = df_global['Marca'].nunique() if len(df_global) > 0 else 0
    col4.metric("Marcas Únicas", marcas_unicas)
    
    st.markdown("---")

# --- SECCIÓN 1: DISTRIBUCIÓN (Gráfico de Torta - NUEVO) ---
st.subheader("1. Composición del Mercado")
col_pie1, col_pie2 = st.columns([1, 2])

with col_pie1:
    st.info("Este gráfico muestra la proporción de productos en la base de datos según el género.")

with col_pie2:
    # GRÁFICO 1 DE 4: TORTA (PIE CHART)
    if genero_selec == "Ambos":
        fig_pie = px.pie(
            df_global, 
            names='Genero', 
            title='Distribución de Productos por Género',
            color='Genero',
            color_discrete_map={'Hombre':'#3366CC', 'Mujer':'#FF66B2'},
            hole=0.4 # Lo convierte en una Donut (más moderno)
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("Selecciona 'Ambos' en el filtro de Género para ver la comparación en el gráfico de torta.")

st.divider()

# --- SECCIÓN 2: ANÁLISIS DE VENTAS (Gráfico de Barras) ---
st.subheader("2. Ranking de Ventas")
col_bar1, col_bar2 = st.columns([1, 3])

with col_bar1:
    st.markdown("Explora las marcas líderes.")
    lista_marcas = sorted(df_global['Marca'].astype(str).unique())
    marca_ventas = st.selectbox("Selecciona Marca:", ["Todas"] + lista_marcas)

with col_bar2:
    # GRÁFICO 2 DE 4: BARRAS
    if marca_ventas == "Todas":
        data_ventas = df_global.groupby('Marca')['Vendidos'].sum().sort_values(ascending=False).head(10).reset_index()
        fig_bar = px.bar(data_ventas, x='Marca', y='Vendidos', color='Vendidos', 
                         title="Top 10 Marcas Más Vendidas", color_continuous_scale='Viridis')
    else:
        data_ventas = df_global[df_global['Marca'] == marca_ventas].sort_values('Vendidos', ascending=False).head(10)
        fig_bar = px.bar(data_ventas, x='Vendidos', y='Titulo', orientation='h', 
                         title=f"Top Productos: {marca_ventas}", color='Vendidos')
    
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# --- SECCIÓN 3: PRECIOS Y TENDENCIAS (Cajas y Dispersión) ---
st.subheader("3. Análisis de Precios y Tendencias")

tab1, tab2 = st.tabs(["📊 Comparador de Precios", "📉 Relación Precio vs. Ventas"])

with tab1:
    st.markdown("**Comparativa de rangos de precio entre marcas**")
    top_marcas_default = df_global['Marca'].value_counts().head(5).index.tolist()
    marcas_comparar = st.multiselect("Marcas a comparar:", options=lista_marcas, default=top_marcas_default)
    
    if marcas_comparar:
        df_comp = df_global[df_global['Marca'].isin(marcas_comparar)]
        # GRÁFICO 3 DE 4: CAJA (BOX PLOT)
        fig_box = px.box(df_comp, x='Marca', y='Precio', color='Marca', points="outliers",
                         title="Distribución de Precios (Box Plot)")
        st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.info("Selecciona marcas para comparar.")

with tab2:
    st.markdown("#### 📉 Análisis de Correlación: Precio vs. Ventas")
    
    # 1. Calculamos la correlación matemática (Requisito: Análisis de datos)
    # Usamos todo el dataframe global, no solo el filtrado por precio visual
    correlacion = df_global['Precio'].corr(df_global['Vendidos'])
    
    # Interpretación automática para el usuario
    if correlacion < 0:
        texto_corr = "Negativa (A mayor precio, menor venta)"
    elif correlacion > 0:
        texto_corr = "Positiva (A mayor precio, mayor venta)"
    else:
        texto_corr = "Neutra (No hay relación aparente)"

    # Mostramos la métrica grande
    col_metric, col_text = st.columns([1, 3])
    col_metric.metric("Coeficiente de Pearson (r)", f"{correlacion:.4f}")
    col_text.info(f"**Interpretación:** La correlación es **{texto_corr}**. En datos de retail, es común ver valores cercanos a 0 o negativos débiles, ya que el precio no es el único factor de compra. Otros factores como la marca, disponibilidad y demanda también influyen.")

    # 2. Gráfico Mejorado (Escala Logarítmica)
    # Filtramos precios extremos solo para el gráfico, no para el cálculo
    df_scatter = df_global[(df_global['Precio'] < 500) & (df_global['Precio'] > 0)]
    
    if len(df_scatter) > 0:
        try:
            fig_scatter = px.scatter(
                df_scatter, 
                x='Precio', 
                y='Vendidos', 
                color='Genero',
                title="Dispersión: Precio vs. Unidades Vendidas (Escala Log)",
                opacity=0.5,
                trendline="ols", # Agrega línea de tendencia automática (Necesita statsmodels)
                log_y=True # <--- ESTO ES CLAVE: Escala logarítmica para ver mejor los datos
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            st.caption("Nota: Se aplicó escala logarítmica en el eje vertical para visualizar mejor la distribución de productos con pocas y muchas ventas.")
        except Exception as e:
            st.warning(f"No se pudo generar el gráfico de dispersión: {str(e)}")
            st.info("Intenta instalar: pip install statsmodels")
    else:
        st.warning("No hay datos disponibles para mostrar el gráfico de dispersión.")
    
# --- DATOS CRUDOS ---
with st.expander("Ver Base de Datos Completa"):
    st.dataframe(df_global)
