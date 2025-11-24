import pandas as pd

# 1. Cargar las bases de datos (Asegúrate de tener los archivos en la misma carpeta)
# Se usa 'try-except' por si el nombre del archivo cambia, una buena práctica de código.
try:
    df_men = pd.read_csv('ebay_mens_perfume.csv')
    df_women = pd.read_csv('ebay_womens_perfume.csv')
    print("¡Archivos cargados exitosamente!")
except FileNotFoundError:
    print("Error: No se encuentran los archivos CSV. Verifica la ruta.")

# 2. Agregar una columna identificadora (Requisito implícito para poder comparar)
# Esto nos permitirá separar hombres de mujeres después de unirlos.
df_men['tipo'] = 'Hombre'
df_women['tipo'] = 'Mujer'

# 3. Crear el DataFrame Maestro (Concatenación)
# Unimos ambos archivos en una sola variable llamada 'df_main'
df_main = pd.concat([df_men, df_women], ignore_index=True)

# 4. Revisión rápida
# Mostramos las columnas y tipos de datos para confirmar qué hay que limpiar
print("\n--- Información del Dataset Completo ---")
df_main.info()

print("\n--- Ejemplo de las primeras filas ---")
print(df_main.head())
