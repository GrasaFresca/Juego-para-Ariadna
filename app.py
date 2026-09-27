# ==========================================
# INTERFAZ 1: PANTALLA DE INICIO
# ==========================================
if st.session_state.pantalla == 'inicio':
    
    # 1. Títulos abarcando el ancho completo de la pantalla
    st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>Akinator: Ley AntiLavado</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #555; margin-bottom: 2rem;'>¿Podré adivinar en qué Actividad Vulnerable estás pensando?</h4>", unsafe_allow_html=True)
    
    # 2. Dividimos la pantalla en dos mitades paralelas
    col_img, col_btn = st.columns([1, 1], gap="large")
    
    with col_img:
        st.image("personaje juego.svg", use_container_width=True)
        
    with col_btn:
        # 3. Espaciador dinámico para centrar el botón a la altura del personaje
        st.markdown("<div style='height: 20vh;'></div>", unsafe_allow_html=True)
        
        if st.button("¡Comenzar a Jugar!", type="primary", use_container_width=True):
            st.session_state.pantalla = 'juego'
            st.session_state.nodo_actual = 'root'
            st.session_state.fallo_inferencia = False
            st.rerun()
