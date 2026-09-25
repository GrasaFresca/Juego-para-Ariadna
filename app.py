import streamlit as st
import pandas as pd
from github import Github
import io
import time
import base64 # Nueva librería para renderizar el video

# 1. Configuración general
st.set_page_config(page_title="Akinator: Ley AntiLavado", layout="centered")

# OJO AQUÍ: Pon tu usuario de GitHub. 
REPO_NAME = "TU_USUARIO/juego-para-ariadna" 
CSV_FILENAME = "arbol_decisiones_antilavado.csv"

# 2. Funciones de Carga y Guardado
@st.cache_data(ttl=0) 
def cargar_datos():
    df = pd.read_csv(CSV_FILENAME)
    return df.set_index('nodo_id').to_dict('index')

def guardar_en_github(nuevo_arbol_dict):
    df_actualizado = pd.DataFrame.from_dict(nuevo_arbol_dict, orient='index').reset_index()
    df_actualizado.rename(columns={'index': 'nodo_id'}, inplace=True)
    
    csv_buffer = io.StringIO()
    df_actualizado.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
    contenido_csv = csv_buffer.getvalue()
    
    g = Github(st.secrets["GITHUB_TOKEN"])
    repo = g.get_repo(REPO_NAME)
    contents = repo.get_contents(CSV_FILENAME)
    
    repo.update_file(
        contents.path, 
        "Actualización de conocimiento de Akinator", 
        contenido_csv, 
        contents.sha
    )

# Cargamos el árbol
arbol = cargar_datos()

# 3. Gestor de estados
if 'pantalla' not in st.session_state:
    st.session_state.pantalla = 'inicio'
if 'nodo_actual' not in st.session_state:
    st.session_state.nodo_actual = 'root'
if 'fallo_inferencia' not in st.session_state:
    st.session_state.fallo_inferencia = False

# ==========================================
# INTERFAZ 1: PANTALLA DE INICIO
# ==========================================
if st.session_state.pantalla == 'inicio':
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>Akinator: Ley AntiLavado</h1>", unsafe_allow_html=True)
        st.info("🖼️ [Espacio reservado para tu logo]")
        st.markdown("<h4 style='text-align: center;'>¿Podré adivinar en qué Actividad Vulnerable estás pensando?</h4>", unsafe_allow_html=True)
        
        if st.button("¡Comenzar a Jugar!", type="primary", use_container_width=True):
            st.session_state.pantalla = 'juego'
            st.session_state.nodo_actual = 'root'
            st.session_state.fallo_inferencia = False
            st.rerun()

# ==========================================
# INTERFAZ 2: PANTALLA DEL JUEGO
# ==========================================
elif st.session_state.pantalla == 'juego':
    if st.button("🔙 Volver al inicio"):
        st.session_state.pantalla = 'inicio'
        st.rerun()
        
    st.write("") 
    
    nodo = arbol[st.session_state.nodo_actual]
    
    col_personaje, col_interfaz = st.columns([1, 1.5], gap="large")
    
    with col_personaje:
        st.image("personaje juego.jpg", use_container_width=True)
        
    with col_interfaz:
        # --- RENDERIZADO DE PREGUNTAS ---
        if nodo['tipo'] == 'pregunta':
            
            globo_texto = f"""
            <div style='
                background-color: #ffffff; 
                padding: 25px; 
                border-radius: 15px; 
                text-align: center; 
                margin-bottom: 30px; 
                box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
                border-left: 5px solid #2e86c1;'>
                <h4 style='color: #1f2937; margin: 0;'>{nodo['texto']}</h4>
            </div>
            """
            st.markdown(globo_texto, unsafe_allow_html=True)
            
            col_si, col_no = st.columns(2)
            with col_si:
                if st.button("Sí", use_container_width=True, type="primary"):
                    st.session_state.nodo_actual = nodo['rama_si']
                    st.rerun()
            with col_no:
                if st.button("No", use_container_width=True):
                    st.session_state.nodo_actual = nodo['rama_no']
                    st.rerun()
                    
        # --- RENDERIZADO DE RESULTADOS ---
        elif nodo['tipo'] == 'resultado':
            
            if not st.session_state.fallo_inferencia:
                globo_exito = f"""
                <div style='background-color: #d4edda; padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 20px; border-left: 5px solid #28a745;'>
                    <h3 style='color: #155724; margin: 0;'>¡Lo tengo!</h3>
                    <p style='font-size: 18px; margin-top: 10px;'>Tu actividad es:<br><b>{nodo['texto']}</b></p>
                </div>
                """
                st.markdown(globo_exito, unsafe_allow_html=True)
                st.write("¿Adiviné correctamente?")
                
                col_acierto, col_error = st.columns(2)
                
                with col_acierto:
                    if st.button("¡Sí, acertaste!", type="primary", use_container_width=True):
                        
                        # --- ANIMACIÓN DE HUMO VECTEEZY ---
                        try:
                            # Lee el archivo físico y lo transforma a código
                            with open("humo.mp4", "rb") as f:
                                video_base64 = base64.b64encode(f.read()).decode()
                            
                            # Crea una capa HTML que cubre toda la pantalla (100vw/100vh)
                            humo_html = f"""
                            <div style='position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: 9999; pointer-events: none;'>
                                <video width="100%" height="100%" autoplay muted style="object-fit: cover; opacity: 0.85;">
                                    <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                                </video>
                            </div>
                            """
                            # Renderiza el video, espera 3 segundos y lo borra
                            pantalla_humo = st.empty()
                            pantalla_humo.markdown(humo_html, unsafe_allow_html=True)
                            time.sleep(3.5) 
                            pantalla_humo.empty()
                            
                        except FileNotFoundError:
                            # Si detecta que no has subido humo.mp4, solo hace pausa para no romper el juego
                            time.sleep(1)
                            
                        # Reinicio al menú principal
                        st.session_state.pantalla = 'inicio'
                        st.session_state.nodo_actual = 'root'
                        st.rerun()
                        
                with col_error:
                    if st.button("No, te equivocaste", use_container_width=True):
                        st.session_state.fallo_inferencia = True
                        st.rerun()
                        
            # --- APRENDIZAJE: INTERFAZ DE ACTUALIZACIÓN ---
            else:
                st.warning("¡Vaya! Necesito actualizar mi base de datos algorítmica.")
                
                nueva_actividad = st.text_input("1. ¿En qué estabas pensando?", placeholder="Ej: Venta de NFTs")
                nueva_pregunta = st.text_input("2. ¿Qué le falta o qué diferencia hay entre lo que pensaste y lo que dije?", placeholder=f"Ej: ¿Involucra arte digital? (Donde 'Sí' sea para tu actividad y 'No' para {nodo['texto']})")
                
                if st.button("Guardar y Aprender", type="primary"):
                    if nueva_actividad and nueva_pregunta:
                        id_nueva_pregunta = f"nodo_dinamico_{len(arbol)+1}"
                        id_nuevo_resultado = f"resultado_dinamico_{len(arbol)+2}"
                        
                        arbol[id_nuevo_resultado] = {"tipo": "resultado", "texto": nueva_actividad, "rama_si": "", "rama_no": ""}
                        arbol[id_nueva_pregunta] = {"tipo": "pregunta", "texto": nueva_pregunta, "rama_si": id_nuevo_resultado, "rama_no": st.session_state.nodo_actual}
                        
                        arbol[st.session_state.nodo_actual] = arbol[id_nueva_pregunta].copy()
                        del arbol[id_nueva_pregunta]
                        
                        with st.spinner("Compilando matriz y haciendo commit en GitHub..."):
                            guardar_en_github(arbol)
                            
                        st.success("¡Base de datos actualizada! El algoritmo es más inteligente ahora.")
                        st.session_state.fallo_inferencia = False
                        st.session_state.nodo_actual = 'root'
                        
                        cargar_datos.clear() 
                        st.rerun()
                    else:
                        st.error("Debes llenar ambos campos para que el sistema pueda aprender.")
