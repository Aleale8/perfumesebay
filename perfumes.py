import streamlit as st
import pandas as pd

# 1. Título de la App (Requisito de "Diseño estructurado" )
st.title("Proyecto de Análisis de Perfumes eBay")
st.write("Cargando datos...")

# 2. Carga de datos con caché (Buena práctica en Streamlit)
@st.cache_data
def cargar_datos():
    try:
        # Asegúrate de que los archivos .csv estén en la misma carpeta que este archivo .py
        df_m = pd.read_csv('ebay_mens_perfume.csv')
        df_w = pd.read_csv('ebay_womens_perfume.csv')
        
        # Etiquetas para diferenciar
        df_m['tipo'] = 'Hombre'
        df_w['tipo'] = 'Mujer'
        
        # Unir los dataframes
        df_unido = pd.concat([df_m, df_w], ignore_index=True)
        return df_unido
    except FileNotFoundError:
        return None

# Ejecutar la función
df_main = cargar_datos()

# 3. Verificación visual en la App
if df_main is not None:
    st.success("¡Base de datos cargada correctamente!")
    
    # Mostrar las primeras filas (Requisito: st.dataframe es un componente )
    st.subheader("Vista Previa de los Datos")
    st.dataframe(df_main.head())
    
    # Mostrar información técnica
    st.subheader("Información del Dataset")
    st.write(f"Cantidad de filas: {df_main.shape[0]}")
    st.write(f"Cantidad de columnas: {df_main.shape[1]}")
    
else:
    st.error("Error: No se encontraron los archivos .csv. Verifica que estén en la misma carpeta.")
