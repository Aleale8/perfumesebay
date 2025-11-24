import streamlit as st
import pandas as pd
import re # Importamos expresiones regulares para limpiar texto

# --- 1. CARGA DE DATOS ---
@st.cache_data
def cargar_datos():
    try:
        df_m = pd.read_csv('ebay_mens_perfume.csv')
        df_w = pd.read_csv('ebay_womens_perfume.csv')
        df_m['tipo'] = 'Hombre'
        df_w['tipo'] = 'Mujer'
        df_unido = pd.concat([df_m, df_w], ignore_index=True)
        return df_unido
    except FileNotFoundError:
        return None

df = cargar_datos()

# --- 2. LIMPIEZA DE DATOS (Obligatorio para que funcionen los filtros) ---
# Función para limpiar el precio (quita símbolos '$', 'US', espacios)
def limpiar_precio(texto):
    if pd.isna(texto):
        return 0.0
    # Mantenemos solo números y el punto decimal
    texto_limpio = re.sub(r'[^\d.]', '', str(texto))
    try:
        return float(texto_limpio)
    except ValueError:
        return 0.0

# Función para limpiar 'sold' (quita 'sold' y comas)
def limpiar_vendidos(texto):
    if pd.isna(texto):
        return 0
    texto_limpio = re.sub(r'[^\d]', '', str(texto)) # Solo deja dígitos
    try:
        return int(texto_limpio)
    except ValueError:
        return 0

if df is not None:
    # Aplicamos la limpieza
    df['precio_num'] = df['price'].apply(limpiar_precio)
    df['vendidos_num'] = df['sold'].apply(limpiar_vendidos)
    
    # Rellenamos nulos en disponibilidad con 0
    df['available'] = df['available'].fillna(0).astype(int)

    # --- 3. BARRA LATERAL CON FILTROS EN CASCADA ---
    st.sidebar.header("🔍 Filtros Avanzados")
    
    # FILTRO 1: GÉNERO
    genero = st.sidebar.radio("1. Selecciona Género", ["Ambos", "Hombre", "Mujer"])
    
    # Filtrado inicial según género
    if genero == "Hombre":
        df_filtrado_1 = df[df['tipo'] == 'Hombre']
    elif genero == "Mujer":
        df_filtrado_1 = df[df['tipo'] == 'Mujer']
    else:
        df_filtrado_1 = df # Ambos

    # FILTRO 2: MARCA (Las opciones dependen del género seleccionado arriba)
    # Obtenemos la lista de marcas DISPONIBLES en el dataframe ya filtrado
    lista_marcas = sorted(df_filtrado_1['brand'].astype(str).unique())
    marca = st.sidebar.selectbox("2. Selecciona Marca", ["Todas"] + lista_marcas)

    # Filtrado secundario según marca
    if marca != "Todas":
        df_filtrado_2 = df_filtrado_1[df_filtrado_1['brand'] == marca]
    else:
        df_filtrado_2 = df_filtrado_1

    # FILTRO 3: COSTE (Rango dinámico basado en los datos filtrados)
    # Calculamos el precio min y max de los productos que quedan
    if not df_filtrado_2.empty:
        min_precio = int(df_filtrado_2['precio_num'].min())
        max_precio = int(df_filtrado_2['precio_num'].max())
        
        # Slider doble para rango de precio
        rango_precio = st.sidebar.slider(
            "3. Rango de Precio ($)",
            min_value=min_precio,
            max_value=max_precio,
            value=(min_precio, max_precio)
        )
        
        # Filtro final por precio
        df_final = df_filtrado_2[
            (df_filtrado_2['precio_num'] >= rango_precio[0]) & 
            (df_filtrado_2['precio_num'] <= rango_precio[1])
        ]
    else:
        df_final = df_filtrado_2
        st.sidebar.warning("No hay productos con estos filtros.")

    # FILTRO 4: DISPONIBILIDAD (Check para ver solo productos con stock)
    solo_con_stock = st.sidebar.checkbox("4. Solo productos disponibles (Stock > 0)")
    if solo_con_stock:
        df_final = df_final[df_final['available'] > 0]

    # --- 4. RESULTADOS EN PANTALLA ---
    st.title(f"Resultados: {genero} - {marca}")
    
    # Métricas (Suma componentes para la rúbrica)
    col1, col2, col3 = st.columns(3)
    col1.metric("Resultados Encontrados", df_final.shape[0])
    col2.metric("Precio Promedio", f"${df_final['precio_num'].mean():.2f}")
    col3.metric("Total Vendidos", f"{df_final['vendidos_num'].sum():,.0f}")

    # Mostrar tabla final
    st.dataframe(df_final[['brand', 'title', 'price', 'sold', 'available', 'tipo']])

else:
    st.error("No se pudo cargar la base de datos.")
