import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz
from typing import Tuple
from Recetas.mealplanner import MealPlanner

def calcular_calorias(objetivo, peso, altura, edad, genero, factor_actividad):
    """
    Calcula las calorías diarias necesarias según el género, peso, altura, edad y nivel de actividad.
    
    Args:
    peso (float): Peso en kilogramos.
    altura (float): Altura en centímetros.
    edad (int): Edad en años.
    genero (str): "Hombre" o "Mujer".
    factor_actividad (float): Factor de actividad (ejemplo: 1.2 para sedentario, 1.55 para moderado).
    
    Returns:
    float: Calorías estimadas.
    """
    factor_actividad_num = {
        'Sedentario': 1.2, 
        'Poca Actividad (1-3 veces por semana)': 1.375,
        'Actividad Moderada (3-5 veces por semana)': 1.55, 
        'Intensa (6-7 veces por semana)': 1.725
    }
    if genero.lower() == "mujer":
        calorias = (65 + (9.6 * peso) + (1.8 * altura) - (4.7 * edad)) * factor_actividad_num[factor_actividad]
    elif genero.lower() == "hombre":
        calorias = (66 + (13.7 * peso) + (5 * altura) - (6.8 * edad)) * factor_actividad_num[factor_actividad]

    if objetivo == 'Build Muscle':
        calorias += 300
    elif objetivo == 'Lose Fat':
        calorias -= 300
    
    return int(calorias)

def busqueda_ofertas(sumplementos, df_productos, umbral = 60):
    """
    Busca ofertas de productos de suplementación en el dataframe de articulos del Decathlon. 
    
    Args:
    sumplementos (list): Lista de suplementos separados por comas.
    df_productos (pd.DataFrame): DataFrame con los productos.
    umbral (int): Umbral de similitud para considerar un producto como recomendado.
    
    Returns:
    df_ofertas (pd.DataFrame): DataFrame con las ofertas de productos recomendados.
    """
    ofertas = []
    for suplemento in sumplementos:
        for index, row in df_productos.iterrows():
            if fuzz.partial_ratio(suplemento, row['Tipo Producto']) > umbral:
                ofertas.append(row)
    df_ofertas = pd.DataFrame(ofertas)
    return df_ofertas

def mostrar_productos(df_productos):
    """
    Muestra productos en formato de tienda (3 arriba, 3 abajo).
    Args:
    df_productos (pd.DataFrame): DataFrame con los productos.
    """
    productos_aleatorios = df_productos.sample(frac=1).drop_duplicates(subset=['Tipo Producto']).head(6)

    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)
    columnas = [col1, col2, col3, col4, col5, col6]

    for i, (_, oferta) in enumerate(productos_aleatorios.iterrows()):
        with columnas[i]:
            st.markdown(f"### 🔥 {oferta['Tipo Producto']}")
            st.markdown(f"<div style='text-align: center;'><img src='{oferta['Image URL']}' width='150'></div>", unsafe_allow_html=True)
            st.markdown(f"### 🤑 ~~{oferta['Precio Previo']}€~~ ➡️ **{oferta['Precio']}€**")
            st.caption(f" {oferta['Etiqueta Web']} de la marca {oferta['Marca']} con un descuento del {oferta['Descuento Aplicado (en %)']}%")


def rutina_personalizada(workouts : pd.DataFrame, nivel : str, sexo : str, objetivo : str) -> Tuple[str, pd.DataFrame]:
    # Filtramos la rutina en base a los datos proporcionados
    if sexo == 'Hombre':
        sexo_ingles = 'Male'
    elif sexo == 'Mujer':
        sexo_ingles = 'Female'
    
    filtered_rows = workouts[
        (workouts['Main Goal'] == objetivo) &
        (workouts['Workout Title'] == nivel) &
        ((workouts['Target Gender'] == sexo_ingles) | (workouts['Target Gender'] == 'Male & Female'))
    ]

    # Seleccionamos una rutina aleatoria de las filtradas para el usuario
    rutina_aleatoria = workouts['Workout Title'].sample(1).values[0]  
    filtered_rows = workouts[workouts['Workout Title'] == rutina_aleatoria]

    return rutina_aleatoria, filtered_rows


# ------------------------------
# App principal
# ------------------------------           

if __name__ == '__main__':
    st.set_page_config(page_title="Tu Plan Personalizado",page_icon = 'image.jpg', layout="wide", initial_sidebar_state="collapsed")
    st.markdown("<h1 style='color: green;'>🏋️‍♂️Descubre Tu Rutina Personalizada, Dieta basada en Calorías Diarias y Ofertas Exclusivas en Musculación 🥑</h1>", unsafe_allow_html=True)
    logo = "image.jpg"
    st.sidebar.image(logo, width=300  )

    try:
        nivel = st.session_state['nivel']
        objetivo = st.session_state['objetivo']
        peso = st.session_state["peso"]
        altura = st.session_state["altura"]
        edad = st.session_state["edad"]
        sexo = st.session_state["sexo"]
        factor_actividad = st.session_state["factor_actividad"]
    except KeyError as e:
        st.error(f"Falta la clave en session_state: {e}")
        st.stop()
    
    #Cargar df dieta
    calorias = calcular_calorias(objetivo, peso, altura, edad, sexo, factor_actividad)
    m = MealPlanner()
    df_dieta = m.get_weekly_menu(calorias)

    # Workouts
    st.write(f'# Rutinas Adecuadas para {nivel}')

    df_rutinas = pd.read_csv('rutinas.csv')

    nombre_rutina, rutina = rutina_personalizada(df_rutinas, nivel, sexo, objetivo)
    

    st.write(f"<h2 style='color: #a6ffcc;'>Tu rutina ideal es del tipo {rutina['Workout Type'].iloc[0]}: {nombre_rutina}</h2>", unsafe_allow_html=True)
    st.write("### Detalles de la rutina:")
    for index, row in rutina.iterrows():
        st.write(f"📌 - **{row['title']}**: {row['content']}")
    st.write(f"## Duración: {rutina['Program Duration'].iloc[0]}, y la debes realizar {rutina['Days Per Week'].iloc[0]} días/semana 📅")


    #Productos recomendades Decathlon

    recommended_supps = rutina['Recommended Supps'].iloc[0]
    if isinstance(recommended_supps, str) and recommended_supps:
        st.write("<h2 style='color: #a6ffcc;'> ⭐  Le recomendamos los siguientes productos:</h2>", unsafe_allow_html=True)
        supps_list = [supp.strip() for supp in recommended_supps.split(",")]
        for supp in supps_list:
            st.markdown(f"- ✅ **{supp}**")
    
    df_productos = pd.read_csv('productos_paginas.csv')
    if isinstance(recommended_supps, str) and recommended_supps:
        st.write(f"<h2 style='color: #a6ffcc;'> Suplementos recomendados con descuentos en Decathlon</h2>", unsafe_allow_html=True)
        df_filtrado = busqueda_ofertas(supps_list, df_productos)
        mostrar_productos(df_filtrado)
        st.write(f"<h2 style='color: #a6ffcc;'>Otros productos recomendados con descuentos</h2>", unsafe_allow_html=True)
        mostrar_productos(df_productos)
    else: 
        st.write(f"<h2 style='color: #a6ffcc;'>Productos recomendados con descuentos en Decathlon</h2>", unsafe_allow_html=True)
        df_filtrado = df_productos
        mostrar_productos(df_filtrado)
    


    # Mealplanner
    
    
    st.write(f"<h2 style='color: #a6ffcc;'>Meal Planner para unas {calorias} calorías diarias aprox</h2>", unsafe_allow_html=True)

    
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    dias_ingles = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday','sunday'] 
    comidas = ['Desayuno', 'Comida', 'Cena']
    comidas_ingles = ['breakfast', 'lunch', 'dinner']

    for dia, dia_ingles in zip(dias_semana, dias_ingles):
        st.markdown(f'<h2 style="color: #a6fff2;"> {dia}</h2>', unsafe_allow_html=True)

        for comida, comida_ingles in zip(comidas, comidas_ingles):
            # Selección de emoji para cada comida
            if comida == 'Desayuno':
                emoji = '☀'
            elif comida == 'Comida':
                emoji = '🍽'
            elif comida == 'Cena':
                emoji = '🌇'
            
            # Filtrado del DataFrame según la comida correspondiente
            df_comida = df_dieta[df_dieta['Meal'] == f'{dia_ingles.lower()} {comida_ingles}']

            # Verifica si el DataFrame contiene datos antes de intentar acceder a ellos
            if not df_comida.empty:
                nombre_plato = df_comida['Name'].values[0] 
                ingredientes = df_comida['Ingredients'].values[0] 
                instrucciones = df_comida['Instructions'].values[0] 

                st.write(f'### {emoji} {comida} : {nombre_plato}')
                st.write(f'#### 🥕 Ingredientes:\n{ingredientes}')
                st.write(f'#### 🍳 Preparación:\n{instrucciones}')
                st.write(f'#### 🥗 Información nutricional:\n')
                
                # Mostrar información nutricional si las columnas existen
                columnas_nutricionales = ['Calories', 'Carbs', 'Fat', 'Protein']
                columnas_presentes = [col for col in columnas_nutricionales if col in df_comida]
                if columnas_presentes:
                    for _, row in df_comida[columnas_presentes].iterrows():
                        calorias = row.get('Calories', 'N/A')
                        carbs = row.get('Carbs', 'N/A')
                        grasas = row.get('Fat', 'N/A')
                        proteina = row.get('Protein', 'N/A')
                        st.write(f'🔥 Calorías: {calorias} | 🥖 Carbs: {carbs} | 🧈 Grasas: {grasas} | 💪 Proteína: {proteina}')
                else:
                    st.write('Información nutricional no disponible.')

            else:
                st.write(f'### {emoji} {comida} : No hay datos disponibles para esta comida.')