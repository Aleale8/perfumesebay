import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- 1. CONFIGURACIÓN Y CARGA DE DATOS ---
st.set_page_config(page_title="Perfumes eBay", layout="wide")

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
        
        # Renombrar columnas al Español (para facilidad de lectura)
        df_unido = df_unido.rename(columns={
            'brand': 'Marca', 
            'title': 'Titulo', 
            'price': 'Precio_Texto', 
            'available': 'Disponibles', 
            'sold': 'Vendidos_Texto'
        })
        return df_unido
    except FileNotFoundError:
        return None

# Función básica de limpieza (necesaria para graficar)
def limpiar_texto_a_numero(texto):
    if pd.isna(texto): return 0
    # Eliminamos todo lo que NO sea número (como '$', 'sold', letras)
    texto_limpio = ''.join(filter(str.isdigit, str(texto)))
    return int(texto_limpio) if texto_limpio else 0

# Ejecutamos carga y limpieza
df = cargar_datos()

if df is not None:
    # Limpiamos columna de ventas para poder graficar
    df['Vendidos'] = df['Vendidos_Texto'].apply(limpiar_texto_a_numero)
else:
    st.error("Error: No se encontraron los archivos CSV.")
    st.stop()


# --- 2. BIENVENIDA (Shape Visual) ---
with st.container():
    st.title("✨ Explorador de Perfumes eBay")
    st.markdown("""
    Bienvenido a la herramienta de análisis. 
    Aquí podrás filtrar la base de datos de perfumes y visualizar las tendencias 
    de venta según el género seleccionado.
    """)
    st.markdown("---") # Línea separadora


# --- 3. FILTRADO DE DATOS (Sidebar) ---
st.sidebar.header("Configuración")

# Selector de Género
opcion_genero = st.sidebar.selectbox(
    "Selecciona el Género a analizar:",
    ["Comparativa General (Todos)", "Solo Hombres", "Solo Mujeres"]
)

# Lógica de Filtrado
if opcion_genero == "Solo Hombres":
    df_filtrado = df[df['Genero'] == 'Hombre']
    color_grafico = 'skyblue'
    titulo_grafico = "Top 5 Marcas más Vendidas (Hombres)"
elif opcion_genero == "Solo Mujeres":
    df_filtrado = df[df['Genero'] == 'Mujer']
    color_grafico = 'lightpink'
    titulo_grafico = "Top 5 Marcas más Vendidas (Mujeres)"
else:
    df_filtrado = df
    color_grafico = 'gray' # Color neutro para general
    titulo_grafico = "Cantidad de Productos por Género"


# --- 4. GRAFICAR A BASE DE SELECCIÓN ---
st.subheader(f"📊 Visualización: {opcion_genero}")

# Creamos el espacio para el gráfico
fig, ax = plt.subplots(figsize=(8, 4))

if opcion_genero == "Comparativa General (Todos)":
    # GRÁFICO 1: Comparación simple (Barras de cantidad)
    conteo = df_filtrado['Genero'].value_counts()
    ax.bar(conteo.index, conteo.values, color=['skyblue', 'lightpink'])
    ax.set_ylabel("Cantidad de Publicaciones")
    
else:
    # GRÁFICO 2: Top Marcas (Si seleccionó un género específico)
    # Agrupamos por marca y sumamos ventas
    top_marcas = df_filtrado.groupby('Marca')['Vendidos'].sum().sort_values(ascending=False).head(5)
    
    ax.bar(top_marcas.index, top_marcas.values, color=color_grafico)
    ax.set_ylabel("Unidades Vendidas")
    ax.set_xlabel("Marca")

# Ajustes finales del gráfico
ax.set_title(titulo_grafico)
plt.xticks(rotation=45) # Rotar nombres para que se lean bien

# Mostrar gráfico en Streamlit
st.pyplot(fig)

# Mostrar datos crudos abajo
with st.expander("Ver tabla de datos detallada"):
    st.dataframe(df_filtrado.head(50))
