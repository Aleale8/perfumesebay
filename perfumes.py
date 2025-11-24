import streamlit as st
import pandas as pd
import re
import plotly.express as px  # <--- CAMBIO: Usamos Plotly en vez de Matplotlib

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Perfumes eBay", layout="wide")

# --- 1. CARGA Y LIMPIEZA DE DATOS ---
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
            'type': 'Tipo_Perfume',
            'price': 'Precio_Texto', 
            'available': 'Disponibles', 
            'sold': 'Vendidos_Texto', 
            'itemLocation': 'Ubicacion'
        })
        return df_unido
    except FileNotFoundError:
        return None

# Funciones de limpieza auxiliar
def limpiar_precio(texto):
    if pd.isna(texto): return 0.0
    texto_limpio = re.sub(r'[^\d.]', '', str(texto))
    try: return float(texto_limpio)
    except: return 0.0

def limpiar_vendidos(texto):
    if pd.isna(texto): return 0
    texto_limpio = re.sub(r'[^\d]', '', str(texto))
    try: return int(texto_limpio)
    except: return 0

# Ejecutar carga
df = cargar_datos()

# --- 2. PROCESAMIENTO PRINCIPAL ---
if df is not None:
    # Aplicar limpieza
    df['Precio'] = df['Precio_Texto'].apply(limpiar_precio)
    df['Vendidos'] = df['Vendidos_Texto'].apply(limpiar_vendidos)
    df['Disponibles'] = df['Disponibles'].fillna(0).astype(int)

    # --- 3. BARRA LATERAL (FILTROS) ---
    st.sidebar.header("🔍 Filtros de Búsqueda")
    
    # A) Filtro Género
    genero_selec = st.sidebar.radio("1. Género:", ["Ambos", "Hombre", "Mujer"])
    
    if genero_selec == "Hombre":
        df_f1 = df[df['Genero'] == 'Hombre']
    elif genero_selec == "Mujer":
        df_f1 = df[df['Genero'] == 'Mujer']
    else:
        df_f1 = df

    # B) Filtro Marca
    lista_marcas = sorted(df_f1['Marca'].astype(str).unique())
    marca_selec = st.sidebar.selectbox("2. Marca:", ["Todas"] + lista_marcas)
    
    if marca_selec != "Todas":
        df_final = df_f1[df_f1['Marca'] == marca_selec]
    else:
        df_final = df_f1

    # --- 4. ÁREA PRINCIPAL ---
    
    # SHAPE DE BIENVENIDA
    with st.container():
        st.markdown("""
        <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 20px;'>
            <h1 style='text-align: center; color: #333;'>✨ Análisis de Mercado: Perfumes eBay</h1>
            <p style='text-align: center; font-size: 16px;'>
                Explora precios y tendencias con gráficos interactivos.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # MÉTRICAS
    col1, col2, col3 = st.columns(3)
    col1.metric("Resultados", df_final.shape[0])
    col2.metric("Precio Promedio", f"${df_final['Precio'].mean():.2f}")
    col3.metric("Total Vendidos", f"{df_final['Vendidos'].sum():,.0f}")
    
    st.markdown("---")

    # --- 5. GRÁFICOS CON PLOTLY ---
    st.subheader("📊 Visualización Interactiva")
    
    ver_grafico = st.checkbox("¿Mostrar gráfico comparativo?")

    if ver_grafico:
        if df_final.empty:
            st.warning("No hay datos para graficar.")
        else:
            # Preparamos datos: Contamos cuántos perfumes hay por Género
            conteo = df_final['Genero'].value_counts().reset_index()
            conteo.columns = ['Genero', 'Cantidad'] # Renombramos para que Plotly entienda
            
            # CREAMOS EL GRÁFICO DE BARRAS INTERACTIVO
            fig = px.bar(
                conteo, 
                x='Genero', 
                y='Cantidad', 
                color='Genero',
                title="Cantidad de Publicaciones por Género",
                color_discrete_map={'Hombre': '#3366CC', 'Mujer': '#FF66B2'}, # Colores personalizados
                text='Cantidad' # Muestra el número encima de la barra
            )
            
            # Ajustes visuales (Centrar título)
            fig.update_layout(title_x=0.5)
            
            # Mostrar en Streamlit (Usa todo el ancho disponible)
            st.plotly_chart(fig, use_container_width=True)
    
    # SECCIÓN DE DATOS
    st.subheader("📋 Detalle de Publicaciones")
    st.dataframe(df_final[['Marca', 'Titulo', 'Precio', 'Vendidos', 'Ubicacion', 'Genero']])

else:
    st.error("Error: Verifica que los archivos CSV estén en la carpeta.")
