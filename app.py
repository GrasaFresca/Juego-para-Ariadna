import streamlit as st
import pandas as pd

# 1. Configuración de la página
st.set_page_config(page_title="Akinator: Actividades Vulnerables", layout="centered")

# 2. Carga de la matriz de características en memoria caché (O(1))
@st.cache_data
def cargar_datos():
    df = pd.read_csv("arbol_decisiones_antilavado.csv")
    return df.set_index('nodo_id').to_dict('index')

arbol = cargar_datos()

# 3. Inicialización del puntero de estado
if 'nodo_actual' not in st.session_state:
    st.session_state.nodo_actual = "root"

# 4. Extracción de los datos del nodo actual
nodo = arbol[st.session_state.nodo_actual]

st.title("Akinator de la Ley AntiLavado")
st.write("Piensa en una de las Actividades Vulnerables del Artículo 17 e intentaré adivinarla.")
st.divider()

# 5. Lógica de renderizado y bifurcación
if nodo['tipo'] == 'pregunta':
    st.subheader(nodo['texto'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Sí", use_container_width=True):
            st.session_state.nodo_actual = nodo['rama_si']
            st.rerun()
            
    with col2:
        if st.button("No", use_container_width=True):
            st.session_state.nodo_actual = nodo['rama_no']
            st.rerun()

elif nodo['tipo'] == 'resultado':
    st.success(f"¡Lo tengo! El resultado es: **{nodo['texto']}**")
    
    if st.button("Volver a jugar", type="primary"):
        st.session_state.nodo_actual = "root"
        st.rerun()
