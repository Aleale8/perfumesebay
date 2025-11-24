import streamlit as st
import pandas as pd
import re

# --- 1. CARGA DE DATOS Y TRADUCCIÓN ---
@st.cache_data
def cargar_datos():
    try:
        df_m = pd.read_csv('ebay_mens_perfume.csv')
        df_w = pd.read_csv('ebay_womens_perfume.csv')
        
        # Etiquetamos el género antes de unir
        df_m['Genero'] = 'Hombre'
        df_w['Genero'] = 'Mujer'
        
        # Unimos los dos archivos
        df_unido = pd.concat([df_m, df_w], ignore_index=True)
        
        # RENOMBRAMOS COLUMNAS AL ESPAÑOL
        # Esto facilita la lectura para tu equipo y la defensa
        df_unido = df_unido.rename(columns={
            'brand': 'Marca',
            'title': 'Titulo',
            'type': 'Tipo_Perfume',
            'price': 'Precio_Texto',      # Precio original sucio (ej: $45.00)
            'priceWithCurrency': 'Precio_Moneda',
            'available': 'Disponibles',
            'sold': 'Vendidos_Texto',     # Vendidos original sucio (ej: 1,200 sold)
            'lastUpdated': 'Ultima_Actualizacion',
            'itemLocation': 'Ubicacion'
        })
        
        return df_unido
    except FileNotFoundError:
        return None

df = cargar_datos()

# --- 2. LIMPIEZA DE DATOS (Usando nombres en español) ---

def limpiar_precio(texto):
    if pd.isna(texto):
        return 0.0
    texto_limpio = re.sub(r'[^\d.]', '', str(texto)) # Deja solo números y puntos
    try:
        return float(texto_limpio)
    except ValueError:
        return 0.0

def limpiar_vendidos(texto):
    if pd.isna(texto):
        return 0
    texto_limpio = re.sub(r'[^\d]', '', str(texto)) # Deja solo números (quita 'sold')
    try:
        return int(texto_limpio)
    except ValueError:
        return 0

if df is not None:
    # Creamos las columnas numéricas limpias para los cálculos
    df['Precio'] = df['Precio_Texto'].apply(limpiar_precio)
    df['Vendidos'] = df['Vendidos_Texto'].apply(limpiar_vendidos)
    
    # Rellenamos nulos en disponibilidad con 0
    df['Disponibles'] = df['Disponibles'].fillna(0).astype(int)

    # --- 3. FILTROS EN CASCADA (Sidebar) ---
    st.sidebar.header("🔍 Filtros de Búsqueda")
    
    # FILTRO 1: GÉNERO
    genero_selec = st.sidebar.radio("1. Selecciona Género", ["Ambos", "Hombre", "Mujer"])
    
    # Lógica de filtrado
    if genero_selec == "Hombre":
        df_f1 = df[df['Genero'] == 'Hombre']
    elif genero_selec == "Mujer":
        df_f1 = df[df['Genero'] == 'Mujer']
    else:
        df_f1 = df # Todos

    # FILTRO 2: MARCA
    # Ordenamos las marcas alfabéticamente
    lista_marcas = sorted(df_f1['Marca'].astype(str).unique())
    marca_selec = st.sidebar.selectbox("2. Selecciona Marca", ["Todas"] + lista_marcas)

    if marca_selec != "Todas":
        df_f2 = df_f1[df_f1['Marca'] == marca_selec]
    else:
        df_f2 = df_f1

    # FILTRO 3: RANGO DE PRECIO
    # Calculamos min y max dinámicamente según lo que quede filtrado
    if not df_f2.empty:
        min_p = int(df_f2['Precio'].min())
        max_p = int(df_f2['Precio'].max())
        
        # Evitamos error si min y max son iguales
        if min_p == max_p:
            rango_precio = (min_p, max_p)
            st.sidebar.info(f"Precio único disponible: ${min_p}")
            df_final = df_f2
        else:
            rango_precio = st.sidebar.slider(
                "3. Rango de Precio ($)",
                min_value=min_p,
                max_value=max_p,
                value=(min_p, max_p)
            )
            # Filtro final
            df_final = df_f2[
                (df_f2['Precio'] >= rango_precio[0]) & 
                (df_f2['Precio'] <= rango_precio[1])
            ]
    else:
        df_final = df_f2
        st.sidebar.warning("No hay datos para estos filtros.")

    # FILTRO 4: STOCK
    solo_stock = st.sidebar.checkbox("4. Solo con Stock Disponible")
    if solo_stock:
        df_final = df_final[df_final['Disponibles'] > 0]

    # --- 4. VISUALIZACIÓN DE RESULTADOS ---
    st.title(f"📊 Análisis de Perfumes: {genero_selec}")
    st.markdown("Resultados filtrados según tus preferencias.")
    
    # Métricas principales
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Perfumes Encontrados", df_final.shape[0])
    kpi2.metric("Precio Promedio", f"${df_final['Precio'].mean():.2f}")
    kpi3.metric("Total Unidades Vendidas", f"{df_final['Vendidos'].sum():,.0f}")

    # Tabla interactiva con columnas limpias en ESPAÑOL
    st.dataframe(df_final[['Marca', 'Titulo', 'Precio', 'Vendidos', 'Disponibles', 'Ubicacion', 'Genero']])

else:
    st.error("Error al cargar los archivos. Verifica que estén en la carpeta.")
