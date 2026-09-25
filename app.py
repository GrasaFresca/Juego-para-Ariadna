import streamlit as st
import pandas as pd

# 1. Configuración general de la página
st.set_page_config(page_title="Akinator: Ley AntiLavado", layout="centered")

# 2. Carga de la matriz de características en memoria
@st.cache_data
def cargar_datos():
    df = pd.read_csv("arbol_decisiones_antilavado.csv")
    return df.set_index('nodo_id').to_dict('index')

arbol = cargar_datos()

# 3. Inicialización de variables de estado (Gestor de pantallas y nodos)
if 'pantalla' not in st.session_state:
    st.session_state.pantalla = 'inicio' # Iniciamos siempre en la pantalla de inicio

if 'nodo_actual' not in st.session_state:
    st.session_state.nodo_actual = 'root'


# ==========================================
# INTERFAZ 1: PANTALLA DE INICIO
# ==========================================
if st.session_state.pantalla == 'inicio':
    # Usamos columnas para centrar el contenido
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center;'>Akinator: Ley AntiLavado</h1>", unsafe_allow_html=True)
        
        # --- AQUÍ VA EL LOGO ---
        # Cuando subas tu imagen a GitHub, quítale el '#' a la línea de abajo y pon el nombre de tu archivo
        # st.image("mi_logo.png", use_container_width=True)
        
        # Este es un recuadro temporal para que veas dónde irá el logo
        st.info("🖼️ [Espacio reservado para tu logo]")
        
        st.markdown("<h4 style='text-align: center;'>¿Podré adivinar en qué Actividad Vulnerable estás pensando?</h4>", unsafe_allow_html=True)
        st.write("") # Espacio en blanco
        
        # Botón para cambiar de pantalla
        if st.button("¡Comenzar a Jugar!", type="primary", use_container_width=True):
            st.session_state.pantalla = 'juego'
            st.session_state.nodo_actual = 'root' # Aseguramos que empiece desde la pregunta 1
            st.rerun()


# ==========================================
# INTERFAZ 2: PANTALLA DEL JUEGO
# ==========================================
elif st.session_state.pantalla == 'juego':
    
    # Botón sutil para regresar al menú principal
    if st.button("🔙 Volver al inicio"):
        st.session_state.pantalla = 'inicio'
        st.rerun()
        
    st.divider() # Línea separadora
    
    # Extracción de los datos del nodo actual
    nodo = arbol[st.session_state.nodo_actual]
    
    # Lógica de renderizado
    if nodo['tipo'] == 'pregunta':
        st.subheader(nodo['texto'])
        
        col_si, col_no = st.columns(2)
        
        with col_si:
            if st.button("Sí", use_container_width=True):
                st.session_state.nodo_actual = nodo['rama_si']
                st.rerun()
                
        with col_no:
            if st.button("No", use_container_width=True):
                st.session_state.nodo_actual = nodo['rama_no']
                st.rerun()
                
    elif nodo['tipo'] == 'resultado':
        st.success(f"¡Lo tengo! El resultado es: **{nodo['texto']}**")
        
        if st.button("Jugar otra vez", type="primary"):
            st.session_state.nodo_actual = "root"
            st.rerun()
