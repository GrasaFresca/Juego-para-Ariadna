import streamlit as st
import pandas as pd
from github import Github
import io

# 1. Configuración general
st.set_page_config(page_title="Akinator: Ley AntiLavado", layout="centered")

# Configura estos datos con los tuyos
REPO_NAME = "TU_USUARIO/akinator-ley-antilavado" # Ej: "ericmorett/akinator-ley-antilavado"
CSV_FILENAME = "arbol_decisiones_antilavado.csv"

# 2. Funciones de Carga y Guardado
@st.cache_data(ttl=0) # ttl=0 fuerza a recargar si el archivo cambió en github
def cargar_datos():
    df = pd.read_csv(CSV_FILENAME)
    return df.set_index('nodo_id').to_dict('index')

def guardar_en_github(nuevo_arbol_dict):
    # Convertimos el diccionario actualizado de vuelta a un DataFrame de Pandas
    df_actualizado = pd.DataFrame.from_dict(nuevo_arbol_dict, orient='index').reset_index()
    df_actualizado.rename(columns={'index': 'nodo_id'}, inplace=True)
    
    # Pasamos el DataFrame a formato texto CSV en memoria
    csv_buffer = io.StringIO()
    df_actualizado.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
    contenido_csv = csv_buffer.getvalue()
    
    # Nos conectamos a GitHub y hacemos el Commit
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
# INTERFAZ 2: PANTALLA DEL JUEGO (LAYOUT AKINATOR)
# ==========================================
elif st.session_state.pantalla == 'juego':
    if st.button("🔙 Volver al inicio"):
        st.session_state.pantalla = 'inicio'
        st.rerun()
        
    st.write("") # Espaciador
    
    # Extraemos los datos del nodo actual
    nodo = arbol[st.session_state.nodo_actual]
    
    # 1. Sistema de grilla: Partimos la pantalla en dos columnas
    # La proporción [1, 1.5] le da un poco más de espacio a los botones que a la imagen
    col_personaje, col_interfaz = st.columns([1, 1.5], gap="large")
    
    with col_personaje:
        # 2. Renderizamos tu imagen del genio en la izquierda
        # Asegúrate de subir el archivo 'image_397e12.jpg' a tu repositorio de GitHub
        st.image("image_397e12.jpg", use_container_width=True)
        
    with col_interfaz:
        # --- RENDERIZADO DE PREGUNTAS ---
        if nodo['tipo'] == 'pregunta':
            
            # 3. Inyección de CSS para simular el globo de texto del genio
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
            
            # Renderizamos los botones debajo del globo de texto
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
                # Globo de texto de éxito
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
                        st.balloons()
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
                        # (Aquí va la misma lógica de guardado matricial de GitHub que ya armamos)
                        # ...
                
    # --- RENDERIZADO DE RESULTADOS ---
    elif nodo['tipo'] == 'resultado':
        
        if not st.session_state.fallo_inferencia:
            st.success(f"Mi respuesta es: **{nodo['texto']}**")
            st.write("¿Adiviné correctamente?")
            
            col_acierto, col_error = st.columns(2)
            with col_acierto:
                if st.button("¡Sí, acertaste!", type="primary", use_container_width=True):
                    st.balloons()
                    st.session_state.nodo_actual = 'root'
                    st.rerun()
            with col_error:
                if st.button("No, te equivocaste", use_container_width=True):
                    st.session_state.fallo_inferencia = True
                    st.rerun()
                    
        # --- APRENDIZAJE: INTERFAZ DE ACTUALIZACIÓN ---
        else:
            st.warning("¡Vaya! Necesito actualizar mi base de datos.")
            
            # Formularios de captura
            nueva_actividad = st.text_input("1. ¿En qué estabas pensando?", placeholder="Ej: Venta de NFTs")
            nueva_pregunta = st.text_input("2. ¿Qué le falta o qué diferencia hay entre lo que pensaste y lo que dije?", placeholder=f"Ej: ¿Involucra arte digital? (Donde 'Sí' sea para tu actividad y 'No' para {nodo['texto']})")
            
            if st.button("Guardar y Aprender", type="primary"):
                if nueva_actividad and nueva_pregunta:
                    # Lógica matricial para inyectar los nuevos nodos
                    id_nueva_pregunta = f"nodo_dinamico_{len(arbol)+1}"
                    id_nuevo_resultado = f"resultado_dinamico_{len(arbol)+2}"
                    
                    # 1. El resultado que falló se mueve a la rama "No" de la nueva pregunta
                    # 2. La actividad del usuario se asigna a la rama "Sí"
                    arbol[id_nuevo_resultado] = {"tipo": "resultado", "texto": nueva_actividad, "rama_si": "", "rama_no": ""}
                    arbol[id_nueva_pregunta] = {"tipo": "pregunta", "texto": nueva_pregunta, "rama_si": id_nuevo_resultado, "rama_no": st.session_state.nodo_actual}
                    
                    # 3. Modificamos el nodo actual (que era un resultado) para que ahora sea la nueva pregunta
                    arbol[st.session_state.nodo_actual] = arbol[id_nueva_pregunta].copy()
                    
                    # 4. Limpiamos la referencia temporal de la pregunta para evitar duplicados lógicos en la matriz
                    del arbol[id_nueva_pregunta]
                    
                    with st.spinner("Compilando matriz y haciendo commit en GitHub..."):
                        guardar_en_github(arbol)
                        
                    st.success("¡Base de datos actualizada! El algoritmo es más inteligente ahora.")
                    st.session_state.fallo_inferencia = False
                    st.session_state.nodo_actual = 'root'
                    
                    # Forzamos la limpieza de la caché para que descargue el nuevo CSV
                    cargar_datos.clear() 
                    st.rerun()
                else:
                    st.error("Debes llenar ambos campos para que el sistema pueda aprender.")
