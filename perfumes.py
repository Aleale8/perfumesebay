import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt # <--- IMPORTANTE: Esta línea es obligatoria

# Configuración del backend para evitar errores de hilos en servidores web
import matplotlib
matplotlib.use('Agg')

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Perfumes eBay", layout="wide")

# --- 1. CARGA Y LIMPIEZA DE DATOS ---
@st.cache_data
def cargar_datos():
    try:
        df_m = pd.read_csv('ebay_mens_perfume.csv')
        df_w = pd.read_csv('ebay_womens_perfume.csv')
        
        # Etiquetas para diferenciar
        df_m['Genero'] = 'Hombre'
        df_w['Genero'] = 'Mujer'
        
        # Unir dataframes
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

# Funciones de limpieza
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

df = cargar_datos()

# --- 2. LÓGICA PRINCIPAL ---
if df is not None:
    # Aplicar limpieza
    df['Precio'] = df['Precio_Texto'].apply(limpiar_precio)
    df['Vendidos'] = df['Vendidos_Texto'].apply(limpiar_vendidos)
    df['Disponibles'] = df['Disponibles'].fillna(0).astype(int)

    # --- BARRA LATERAL (FILTROS) ---
    st.sidebar.header("🔍 Filtros de Búsqueda")
    
    # 1. Filtro Género
    genero_selec = st.sidebar.radio("1. Género:", ["Ambos", "Hombre", "Mujer"])
    
    if genero_selec == "Hombre":
        df_f1 = df[df['Genero'] == 'Hombre']
    elif genero_selec == "Mujer":
        df_f1 = df[df['Genero'] == 'Mujer']
    else:
        df_f1 = df

    # 2. Filtro Marca (Dinámico)
    lista_marcas = sorted(df_f1['Marca'].astype(str).unique())
    marca_selec = st.sidebar.selectbox("2. Marca:", ["Todas"] + lista_marcas)
    
    if marca_selec != "Todas":
        df_f2 = df_f1[df_f1['Marca'] == marca_selec]
    else:
        df_f2 = df_f1
        
    # 3. Filtro Rango de Precio (Dinámico)
    if not df_f2.empty:
        min_p = int(df_f2['Precio'].min())
        max_p = int(df_f2['Precio'].max())
        
        if min_p < max_p:
            rango_precio = st.sidebar.slider("3. Rango de Precio ($)", min_p, max_p, (min_p, max_p))
            df_final = df_f2[(df_f2['Precio'] >= rango_precio[0]) & (df_f2['Precio'] <= rango_precio[1])]
        else:
            df_final = df_f2
    else:
        df_final = df_f2

    # --- ÁREA PRINCIPAL ---
    
    # Bienvenida (Shape)
    with st.container():
        st.markdown("""
        <div style='background-color: #E6F3FF; padding: 20px; border-radius: 10px; border-left: 5px solid #3366CC;'>
            <h2 style='color: #000; margin:0;'>📊 Dashboard de Perfumes eBay</h2>
            <p style='margin:0;'>Análisis de precios, marcas y tendencias de mercado.</p>
        </div>
        <br>
        """, unsafe_allow_html=True)

    # Métricas
    col1, col2, col3 = st.columns(3)
    col1.metric("Resultados", df_final.shape[0])
    col2.metric("Precio Promedio", f"${df_final['Precio'].mean():.2f}")
    col3.metric("Total Vendidos", f"{df_final['Vendidos'].sum():,.0f}")
    
    st.divider()

    # --- GRÁFICOS (MATPLOTLIB) ---
    st.subheader("📈 Visualizaciones")
    
    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        # GRÁFICO 1: BARRAS (Cantidad por Género)
        mostrar_barras = st.checkbox("Ver Cantidad por Género", value=True)
        if mostrar_barras:
            conteo = df_final['Genero'].value_counts()
            if not conteo.empty:
                fig1, ax1 = plt.subplots(figsize=(5, 4))
                colores = ['#1f77b4' if x == 'Hombre' else '#e377c2' for x in conteo.index]
                ax1.bar(conteo.index, conteo.values, color=colores)
                ax1.set_title("Cantidad de Publicaciones")
                ax1.set_ylabel("Cantidad")
                st.pyplot(fig1) # <--- Aquí usamos Matplotlib
            else:
                st.info("Sin datos para graficar.")

    with col_graf2:
        # GRÁFICO 2: HISTOGRAMA (Distribución de Precios)
        mostrar_hist = st.checkbox("Ver Distribución de Precios")
        if mostrar_hist:
            if not df_final.empty:
                fig2, ax2 = plt.subplots(figsize=(5, 4))
                ax2.hist(df_final['Precio'], bins=15, color='teal', edgecolor='white', alpha=0.7)
                ax2.set_title("Distribución de Precios ($)")
                ax2.set_xlabel("Precio")
                ax2.set_ylabel("Frecuencia")
                st.pyplot(fig2) # <--- Aquí usamos Matplotlib
            else:
                st.info("Sin datos para graficar.")

    # --- TABLA DE DATOS ---
    st.subheader("📋 Detalle de Datos")
    st.dataframe(df_final[['Marca', 'Titulo', 'Precio', 'Vendidos', 'Ubicacion', 'Genero']], use_container_width=True)

else:
    st.error("Error: No se encuentran los archivos CSV. Verifica tu carpeta.")
