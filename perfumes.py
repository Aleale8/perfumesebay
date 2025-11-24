import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. CONFIGURACIÓN Y CARGA ---
st.set_page_config(page_title="Perfumes eBay - Avanzado", layout="wide")

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
    except FileNotFoundError:
        return None

# Limpieza
def limpiar_precio(texto):
    if pd.isna(texto): return 0.0
    texto_limpio = ''.join(filter(lambda x: x.isdigit() or x == '.', str(texto)))
    try: return float(texto_limpio)
    except: return 0.0

def limpiar_vendidos(texto):
    if pd.isna(texto): return 0
    texto_limpio = ''.join(filter(str.isdigit, str(texto)))
    return int(texto_limpio) if texto_limpio else 0

df = cargar_datos()

if df is not None:
    df['Precio'] = df['Precio_Texto'].apply(limpiar_precio)
    df['Vendidos'] = df['Vendidos_Texto'].apply(limpiar_vendidos)
else:
    st.error("Error: Archivos no encontrados.")
    st.stop()

# --- 2. SIDEBAR (FILTROS PRINCIPALES) ---
st.sidebar.header("🔍 Filtros Generales")
genero_selec = st.sidebar.radio("Género:", ["Ambos", "Hombre", "Mujer"])

# Aplicar filtro de género globalmente
if genero_selec == "Hombre": df_global = df[df['Genero'] == 'Hombre']
elif genero_selec == "Mujer": df_global = df[df['Genero'] == 'Mujer']
else: df_global = df

# --- 3. CONTENIDO PRINCIPAL ---

# Bienvenida
with st.container():
    st.title("✨ Dashboard de Mercado de Perfumes")
    st.markdown("Análisis interactivo de ventas y precios.")
    st.markdown("---")

# SECCIÓN 1: ANÁLISIS DE VENTAS (Gráfico de Barras)
st.subheader("📊 Top Ventas")
col_filtros, col_grafico = st.columns([1, 3])

with col_filtros:
    st.markdown("**Configuración de Ventas:**")
    lista_marcas = sorted(df_global['Marca'].astype(str).unique())
    marca_ventas = st.selectbox("Filtrar Marca (Ventas):", ["Todas"] + lista_marcas)

with col_grafico:
    if marca_ventas == "Todas":
        data_ventas = df_global.groupby('Marca')['Vendidos'].sum().sort_values(ascending=False).head(10).reset_index()
        fig_ventas = px.bar(data_ventas, x='Marca', y='Vendidos', color='Vendidos', 
                            title="Top 10 Marcas Más Vendidas", color_continuous_scale='Viridis')
    else:
        data_ventas = df_global[df_global['Marca'] == marca_ventas].sort_values('Vendidos', ascending=False).head(10)
        fig_ventas = px.bar(data_ventas, x='Vendidos', y='Titulo', orientation='h', 
                            title=f"Top Productos: {marca_ventas}", color='Vendidos')
    
    st.plotly_chart(fig_ventas, use_container_width=True)

st.divider()

# SECCIÓN 2: COMPARADOR DE PRECIOS (NUEVO - Gráfico de Caja)
st.subheader("💸 Comparador de Precios entre Marcas")
st.markdown("Selecciona varias marcas para comparar sus rangos de precios (Mínimo, Máximo y Promedio).")

# Filtro específico para este gráfico (Multiselect)
# Usamos df_global para que respete si eligió "Hombre" o "Mujer" arriba
top_marcas_default = df_global['Marca'].value_counts().head(5).index.tolist() # Pre-seleccionamos las top 5
marcas_comparar = st.multiselect(
    "Selecciona las marcas a comparar:",
    options=lista_marcas,
    default=top_marcas_default # Empieza con 5 marcas seleccionadas
)

if marcas_comparar:
    # Filtramos los datos solo para las marcas seleccionadas
    df_comparacion = df_global[df_global['Marca'].isin(marcas_comparar)]
    
    # GRÁFICO DE CAJA (BOX PLOT) - Requisito: Estilo diferente
    # Points='all' muestra también los puntos individuales (perfumes)
    fig_precios = px.box(
        df_comparacion, 
        x='Marca', 
        y='Precio', 
        color='Marca',
        title="Distribución de Precios por Marca",
        points="outliers" # Muestra puntos atípicos (perfumes muy caros)
    )
    
    fig_precios.update_layout(xaxis_title="Marca", yaxis_title="Precio ($ USD)")
    
    st.plotly_chart(fig_precios, use_container_width=True)
    
    # Explicación para la defensa oral
    with st.expander("ℹ️ ¿Cómo leer este gráfico?"):
        st.write("""
        - La **caja** muestra dónde están la mayoría de los precios (del 25% al 75%).
        - La **línea dentro de la caja** es la Mediana (el precio central).
        - Los **bigotes (líneas)** muestran el rango normal de precios.
        - Los **puntos sueltos** son "Outliers" (perfumes inusualmente caros o baratos).
        """)
else:
    st.info("Selecciona al menos una marca para ver la comparación.")

# Tabla de datos al final
with st.expander("Ver Datos Crudos"):
    st.dataframe(df_global)
