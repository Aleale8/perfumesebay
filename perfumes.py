import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- 1. CONFIGURACIÓN Y CARGA ---
st.set_page_config(page_title="Perfumes eBay - Cascada", layout="wide")

@st.cache_data
def cargar_datos():
    try:
        # Cargamos ambos archivos
        df_m = pd.read_csv('ebay_mens_perfume.csv')
        df_w = pd.read_csv('ebay_womens_perfume.csv')
        
        # Etiquetamos
        df_m['Genero'] = 'Hombre'
        df_w['Genero'] = 'Mujer'
        
        # Unimos
        df_unido = pd.concat([df_m, df_w], ignore_index=True)
        
        # Renombramos al Español
        df_unido = df_unido.rename(columns={
            'brand': 'Marca', 
            'title': 'Titulo', 
            'price': 'Precio_Texto', 
            'available': 'Disponibles', 
            'sold': 'Vendidos_Texto',
            'itemLocation': 'Ubicacion'
        })
        return df_unido
    except FileNotFoundError:
        return None

# Funciones de limpieza (Esenciales para los filtros numéricos)
def limpiar_precio(texto):
    if pd.isna(texto): return 0.0
    # Dejar solo dígitos y punto decimal
    texto_limpio = ''.join(filter(lambda x: x.isdigit() or x == '.', str(texto)))
    try: return float(texto_limpio)
    except: return 0.0

def limpiar_vendidos(texto):
    if pd.isna(texto): return 0
    # Dejar solo dígitos
    texto_limpio = ''.join(filter(str.isdigit, str(texto)))
    return int(texto_limpio) if texto_limpio else 0

# Carga inicial
df = cargar_datos()

if df is not None:
    # Aplicamos limpieza
    df['Precio'] = df['Precio_Texto'].apply(limpiar_precio)
    df['Vendidos'] = df['Vendidos_Texto'].apply(limpiar_vendidos)
else:
    st.error("Error crítico: No se encontraron los archivos CSV.")
    st.stop()


# --- 2. BIENVENIDA ---
with st.container():
    st.title("✨ Buscador Inteligente de Perfumes")
    st.markdown("Utiliza los filtros del panel izquierdo para refinar tu búsqueda en cascada.")
    st.markdown("---")


# --- 3. FILTROS EN CASCADA (SIDEBAR) ---
st.sidebar.header("🔍 Filtros en Cascada")

# NIVEL 1: GÉNERO
genero_selec = st.sidebar.radio("1. Primero, elige el Género:", ["Ambos", "Hombre", "Mujer"])

# Aplicamos Filtro 1
if genero_selec == "Hombre":
    df_paso_1 = df[df['Genero'] == 'Hombre']
elif genero_selec == "Mujer":
    df_paso_1 = df[df['Genero'] == 'Mujer']
else:
    df_paso_1 = df

# NIVEL 2: MARCA (Depende del Nivel 1)
# Obtenemos solo las marcas que existen en el df_paso_1
lista_marcas = sorted(df_paso_1['Marca'].astype(str).unique())
marca_selec = st.sidebar.selectbox("2. Ahora, selecciona la Marca:", ["Todas"] + lista_marcas)

# Aplicamos Filtro 2
if marca_selec != "Todas":
    df_paso_2 = df_paso_1[df_paso_1['Marca'] == marca_selec]
else:
    df_paso_2 = df_paso_1

# NIVEL 3: PRECIO (Depende del Nivel 2)
# El slider se ajusta al precio mínimo y máximo de los productos que quedan
if not df_paso_2.empty:
    min_p = int(df_paso_2['Precio'].min())
    max_p = int(df_paso_2['Precio'].max())
    
    if min_p == max_p:
        st.sidebar.info(f"Precio único: ${min_p}")
        df_final = df_paso_2
    else:
        rango_precio = st.sidebar.slider(
            "3. Finalmente, ajusta tu presupuesto ($):", 
            min_p, max_p, (min_p, max_p)
        )
        # Aplicamos Filtro 3
        df_final = df_paso_2[
            (df_paso_2['Precio'] >= rango_precio[0]) & 
            (df_paso_2['Precio'] <= rango_precio[1])
        ]
else:
    df_final = df_paso_2
    st.sidebar.warning("No hay productos con estos criterios.")


# --- 4. VISUALIZACIÓN DINÁMICA ---
st.subheader(f"📊 Resultados: {genero_selec} > {marca_selec}")

# Métricas Clave
col1, col2, col3 = st.columns(3)
col1.metric("Perfumes Encontrados", df_final.shape[0])
col2.metric("Precio Promedio", f"${df_final['Precio'].mean():.2f}")
col3.metric("Total Unidades Vendidas", f"{df_final['Vendidos'].sum():,.0f}")

st.write("") # Espacio

# Lógica del Gráfico: Cambia según si eligió una marca o todas
fig, ax = plt.subplots(figsize=(10, 5))

if df_final.empty:
    st.info("No hay datos suficientes para graficar.")
else:
    if marca_selec == "Todas":
        # CASO A: Vemos TODAS las marcas -> Graficamos Top 10 Marcas más vendidas
        top_data = df_final.groupby('Marca')['Vendidos'].sum().sort_values(ascending=False).head(10)
        ax.bar(top_data.index, top_data.values, color='#4CAF50') # Verde
        ax.set_title(f"Top 10 Marcas Más Vendidas ({genero_selec})")
        ax.set_xlabel("Marca")
        ax.set_ylabel("Total Vendidos")
        plt.xticks(rotation=45)
    else:
        # CASO B: Vemos UNA sola marca -> Graficamos Top 10 Perfumes (Títulos) de esa marca
        top_data = df_final.groupby('Titulo')['Vendidos'].sum().sort_values(ascending=False).head(10)
        ax.barh(top_data.index, top_data.values, color='#2196F3') # Azul
        ax.set_title(f"Top Productos Más Vendidos de {marca_selec}")
        ax.set_xlabel("Total Vendidos")
        # barh es gráfico horizontal, ideal para nombres largos de perfumes

    # Mostrar gráfico
    st.pyplot(fig)

# Tabla final
with st.expander("Ver Detalles de la Lista"):
    st.dataframe(df_final[['Marca', 'Titulo', 'Precio', 'Vendidos', 'Ubicacion', 'Genero']])
