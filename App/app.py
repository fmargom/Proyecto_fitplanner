import streamlit as st

st.set_page_config(page_title="Tu Plan Personalizado",page_icon = 'image.jpg', layout="wide", initial_sidebar_state="collapsed")
logo = "image.jpg"
st.sidebar.image(logo, width=300  )

st.markdown("<h1 style='color: darkgreen;'>💪Bienvenido a tu App de Rutinas y Dietas Personalizadas 🥗</h1>", unsafe_allow_html=True)

st.subheader("Rellene el formulario para proceder con su plan personalizado:")
with st.form(key='user_form'):
    nombre = st.text_input("¿Cuál es tu nombre?", "Usuario") 

    objetivo = st.selectbox(
        "¿Cuál es tu objetivo?",
        ('Lose Fat', 'Build Muscle', 'General Fitness', 'Increase Strength', 'Sports Performance')
    )

    nivel = st.radio(
        "Selecciona tu nivel de experiencia:",
        ('Beginner', 'Advanced', 'Intermediate')
    )
    sexo = st.selectbox(
        "¿Cuál es tu género?",
        ("Hombre", "Mujer")
    )
    peso = st.number_input(
        "Introduce tu peso",  
        min_value=0.0,          
        max_value=150.0,        
        value = 0.0,
        step=0.1                
    )
    altura = st.number_input(
        '¿Cuál es tu altura (en cm)',
        min_value=0,          
        max_value=250,        
        step=1  
    )
    edad = st.number_input(
        '¿Cuál es tu edad',         
        min_value=0,          
        max_value=100,        
        step=1  
    )
    

    factor_actividad = st.selectbox(
        'Cuál es tu factor de actividad semanal:',
        ("Sedentario", "Poca Actividad (1-3 veces por semana)", "Actividad Moderada (3-5 veces por semana)", 'Intensa (6-7 veces por semana)')
    )

    submit_button = st.form_submit_button(label="Generar Plan")

    if submit_button:
        if not nombre:
            st.error("Por favor, ingresa tu nombre.")
        elif peso <= 0:
            st.error("Por favor, ingresa un peso válido.")
        elif altura <= 0:
            st.error("Por favor, ingresa una altura válida.")
        elif edad <= 0:
            st.error("Por favor, ingresa una edad válida.")
        else:
            st.success(f"¡Plan personalizado generado para {nombre} con el objetivo de {objetivo} en nivel {nivel}!")
            
            # Guardar valores solo si el botón fue presionado
            st.session_state["nombre"] = nombre
            st.session_state["objetivo"] = objetivo
            st.session_state["nivel"] = nivel
            st.session_state["sexo"] = sexo
            st.session_state["peso"] = peso
            st.session_state["altura"] = altura
            st.session_state["edad"] = edad
            st.session_state["factor_actividad"] = factor_actividad

        
        st.switch_page('pages/output.py')
