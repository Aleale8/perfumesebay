import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt  # <--- ESTA LÍNEA ES LA CLAVE
import matplotlib

# Configuración para evitar errores de hilos en Streamlit (Opcional pero recomendado)
matplotlib.use('Agg')

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
    texto_limpio = re.sub(r'[^\d.]', '', str(texto)) # Solo números y punto
    try: return float(texto_limpio)
    except: return 0.0

def limpiar_vendidos(texto):
    if pd.isna(texto): return 0
    texto_limpio = re.sub(r'[^\d]', '', str(texto)) # Solo números
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

    # --- 3. BARRA LATERAL (FILTROS EN CASCADA) ---
    st.sidebar.header("🔍 Filtros de Búsqueda")
    
    # A) Filtro Género
    genero_selec = st.sidebar.radio("1. Género:", ["Ambos", "Hombre", "Mujer"])
    
    if genero_selec == "Hombre":
        df_f1 = df[df['Genero'] == 'Hombre']
    elif genero_selec == "Mujer":
        df_f1 = df[df['Genero'] == 'Mujer']
    else:
        df_f1 = df

    # B) Filtro Marca (Depende del género)
    lista_marcas = sorted(df_f1['Marca'].astype(str).unique())
    marca_selec = st.sidebar.selectbox("2. Marca:", ["Todas"] + lista_marcas)
    
    if marca_selec != "Todas":
        df_final = df_f1[df_f1['Marca'] == marca_selec]
    else:
        df_final = df_f1

    # --- 4. ÁREA PRINCIPAL (Bienvenida y Gráficos) ---
    
    # SHAPE DE BIENVENIDA (HTML/CSS)
    with st.container():
        st.markdown("""
        <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 20px;'>
            <h1 style='text-align: center; color: #333;'>✨ Análisis de Mercado: Perfumes eBay</h1>
            <p style='text-align: center; font-size: 16px;'>
                Explora precios, marcas y tendencias de venta. Usa el menú izquierdo para filtrar.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # MÉTRICAS RÁPIDAS
    col1, col2, col3 = st.columns(3)
    col1.metric("Resultados", df_final.shape[0])
    col2.metric("Precio Promedio", f"${df_final['Precio'].mean():.2f}")
    col3.metric("Total Vendidos", f"{df_final['Vendidos'].sum():,.0f}")
    
    st.markdown("---")

    # SECCIÓN GRÁFICA CONDICIONAL
    st.subheader("📊 Visualización Comparativa")
    
    # Checkbox para mostrar/ocultar gráfico
    ver_grafico = st.checkbox("¿Mostrar gráfico de cantidad por Género?")

    if ver_grafico:
        if df_final.empty:
            st.warning("No hay datos para graficar con estos filtros.")
        else:
            st.write("Generando gráfico...")
            
            # Preparar datos
            conteo = df_final['Genero'].value_counts()
            
            # Crear figura con Matplotlib
            fig, ax = plt.subplots(figsize=(6, 4))
            
            # Definir colores
            colores = ['skyblue' if x == 'Hombre' else 'lightpink' for x in conteo.index]
            
            ax.bar(conteo.index, conteo.values, color=colores)
            ax.set_title("Cantidad de Perfumes Filtrados")
            ax.set_ylabel("Cantidad")
            
            # Renderizar en Streamlit
            st.pyplot(fig)
    
    # SECCIÓN DE DATOS
    st.subheader("📋 Detalle de Publicaciones")
    st.dataframe(df_final[['Marca', 'Titulo', 'Precio', 'Vendidos', 'Ubicacion', 'Genero']])

else:
    st.error("Error: No se encuentran los archivos CSV. Verifica que 'ebay_mens_perfume.csv' y 'ebay_womens_perfume.csv' estén en la carpeta.")
