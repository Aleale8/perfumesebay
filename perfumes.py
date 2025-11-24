import streamlit as st
import pandas as pd
import plotly.express as px # <--- LA CLAVE DE LA INTERACTIVIDAD

# --- 1. CONFIGURACIÓN Y CARGA ---
st.set_page_config(page_title="Perfumes eBay - Interactivo", layout="wide")

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

# --- 2. BIENVENIDA ---
with st.container():
    st.title("✨ Buscador Interactivo de Perfumes")
    st.markdown("Ahora los gráficos son **interactivos**. Pasa el mouse sobre las barras para ver detalles.")
    st.markdown("---")

# --- 3. FILTROS EN CASCADA ---
st.sidebar.header("🔍 Filtros")

# Nivel 1: Género
genero_selec = st.sidebar.radio("1. Género:", ["Ambos", "Hombre", "Mujer"])
if genero_selec == "Hombre": df_1 = df[df['Genero'] == 'Hombre']
elif genero_selec == "Mujer": df_1 = df[df['Genero'] == 'Mujer']
else: df_1 = df

# Nivel 2: Marca
lista_marcas = sorted(df_1['Marca'].astype(str).unique())
marca_selec = st.sidebar.selectbox("2. Marca:", ["Todas"] + lista_marcas)
if marca_selec != "Todas": df_2 = df_1[df_1['Marca'] == marca_selec]
else: df_2 = df_1

# Nivel 3: Precio
if not df_2.empty:
    min_p, max_p = int(df_2['Precio'].min()), int(df_2['Precio'].max())
    if min_p < max_p:
        rango = st.sidebar.slider("3. Presupuesto ($):", min_p, max_p, (min_p, max_p))
        df_final = df_2[(df_2['Precio'] >= rango[0]) & (df_2['Precio'] <= rango[1])]
    else: df_final = df_2
else: df_final = df_2

# --- 4. VISUALIZACIÓN INTERACTIVA (PLOTLY) ---
st.subheader(f"📊 Análisis: {genero_selec} > {marca_selec}")

# Métricas
col1, col2, col3 = st.columns(3)
col1.metric("Perfumes", df_final.shape[0])
col2.metric("Precio Promedio", f"${df_final['Precio'].mean():.2f}")
col3.metric("Total Vendidos", f"{df_final['Vendidos'].sum():,.0f}")

st.divider()

if not df_final.empty:
    if marca_selec == "Todas":
        # GRÁFICO 1: Barras Verticales (Comparando Marcas)
        data_graf = df_final.groupby('Marca')['Vendidos'].sum().sort_values(ascending=False).head(10).reset_index()
        
        fig = px.bar(
            data_graf, 
            x='Marca', 
            y='Vendidos', 
            color='Vendidos', # Colorear según intensidad de ventas
            title=f"Top 10 Marcas más vendidas ({genero_selec})",
            color_continuous_scale='Viridis', # Escala de colores profesional
            text_auto=True # Muestra el número automáticamente
        )
        fig.update_layout(xaxis_title="Marca", yaxis_title="Unidades Vendidas")
        
    else:
        # GRÁFICO 2: Barras Horizontales (Productos específicos)
        data_graf = df_final.groupby('Titulo')['Vendidos'].sum().sort_values(ascending=False).head(10).reset_index()
        
        fig = px.bar(
            data_graf, 
            x='Vendidos', 
            y='Titulo', 
            orientation='h', # Horizontal
            color='Vendidos',
            title=f"Top Productos de {marca_selec}",
            color_continuous_scale='Bluyl',
            text_auto=True
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'}) # Ordenar bonito

    # RENDERIZAR EN STREAMLIT
    # use_container_width=True hace que se ajuste al ancho de la pantalla
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("💡 Tip: Puedes hacer zoom en el gráfico o descargar la imagen con la cámara que aparece al pasar el mouse.")

else:
    st.warning("No hay datos para mostrar.")

# Tabla
with st.expander("Ver Datos Detallados"):
    st.dataframe(df_final)
