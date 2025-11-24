import streamlit as st
import pandas as pd
import re
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
        <div style='background-color: #E6F3FF; padding: 20px; border-radius: 10px; border-
