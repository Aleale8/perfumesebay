import streamlit as st
import pandas as pd
import matplotlib as plt 
import re

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Perfumes eBay", layout="wide")

# --- 1. CARGA Y LIMPIEZA (Igual que antes) ---
@st.cache_data
def cargar_datos():
    try:
        df_m = pd.read_csv('ebay_mens_perfume.csv')
        df_w = pd.read_csv('ebay_womens_perfume.csv')
        df_m['Genero'] = 'Hombre'
        df_w['Genero'] = 'Mujer'
        df_unido = pd.concat([df_m, df_w], ignore_index=True)
        
        # Renombrar columnas
        df_unido = df_unido.rename(columns={
            'brand': 'Marca', 'title': 'Titulo', 'type': 'Tipo_Perfume',
            'price': 'Precio_Texto', 'available': 'Disponibles', 
            'sold': 'Vendidos_Texto', 'itemLocation': 'Ubicacion'
        })
        return df_unido
    except FileNotFoundError:
        return None

df = cargar_datos()

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

if df is not None:
    df['Precio'] = df['Precio_Texto'].apply(limpiar_precio)
    df['Vendidos'] = df['Vendidos_Texto'].apply(limpiar_vendidos)
    df['Disponibles'] = df['Disponibles'].fillna(0).astype(int)

    # --- 2. BARRA LATERAL (Filtros) ---
    st.sidebar.header("🔍 Filtros")
    
    # Filtro Género
    genero_selec = st.sidebar.radio("Género:", ["Ambos", "Hombre", "Mujer"])
    if genero_selec == "Hombre": df_final = df[df['Genero'] == 'Hombre']
    elif genero_selec == "Mujer": df_final = df[df['Genero'] == 'Mujer']
    else: df_final = df

    # --- 3. SECCIÓN DE BIENVENIDA (SHAPE) ---
    # Usamos st.container para agrupar visualmente la bienvenida
    with st.container():
        st.markdown("""
        <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; border: 1px solid #ddd;'>
            <h1 style='text-align: center; color: #333;'>✨ Análisis de Mercado de Perfumes eBay</h1>
            <p style='text-align: center; font-size: 16px;'>
                Bienvenido a la herramienta de visualización interactiva. 
                Utiliza los filtros de la izquierda para explorar datos de perfumes de hombre y mujer.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---") # Línea separadora

    # --- 4. GRÁFICO CONDICIONAL (Requisito: Gráfico de Barras) ---
    st.subheader("📊 Visualización General")
    
    # Checkbox: El usuario decide SI o NO ver el gráfico
    # Esto suma interactividad y un componente (checkbox)
    ver_grafico = st.checkbox("¿Deseas ver la comparación de cantidad por Género?")

    if ver_grafico:
        # Si dice que SÍ, generamos el gráfico
        st.write("Generando gráfico comparativo...")
        
        # Preparamos los datos para el gráfico
        # Contamos cuántos hay de cada género en la selección actual
        conteo_genero = df_final['Genero'].value_counts()
        
        # Código Matplotlib (Requisito de código)
        fig, ax = plt.subplots(figsize=(6, 4))
        
        # Colores personalizados: Azul para hombre, Rosa para mujer (si existen en los datos)
        colores = ['skyblue' if x == 'Hombre' else 'lightpink' for x in conteo_genero.index]
        
        # Crear gráfico de BARRAS
        ax.bar(conteo_genero.index, conteo_genero.values, color=colores)
        
        # Etiquetas y Títulos (Requisito: "Visualizaciones claras" [cite: 48])
        ax.set_title("Cantidad de Perfumes por Género (Filtrado)")
        ax.set_xlabel("Género")
        ax.set_ylabel("Cantidad de Publicaciones")
        
        # Mostrar en Streamlit
        st.pyplot(fig)
        
        st.info(f"Interpretación: En esta selección hay {df_final.shape[0]} perfumes mostrados.")
    else:
        # Si dice que NO
        st.caption("Selecciona la casilla de arriba para activar los gráficos.")

    # --- 5. DATOS ---
    st.subheader("📋 Detalle de Datos")
    st.dataframe(df_final[['Marca', 'Titulo', 'Precio', 'Vendidos', 'Genero']].head(10))

else:
    st.error("Error al cargar datos.")
