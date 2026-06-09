import streamlit as st
import os
import shutil
import zipfile
from io import BytesIO

# --- CONFIGURACIÓN Y CONSTANTES ---
CARPETA_BASE = "galeria_patinaje"
PASS_ADMIN = "AdminVillarrubia2026" 
if not os.path.exists(CARPETA_BASE): os.makedirs(CARPETA_BASE)

# Inicializar estados
if "nivel" not in st.session_state: st.session_state.nivel = None
if "passwords" not in st.session_state: st.session_state.passwords = {} # {nombre_carpeta: password}

def verificar_acceso():
    if st.session_state.nivel is None:
        st.title("🔐 Acceso al Club")
        pw = st.text_input("Introduce tu contraseña:", type="password")
        if st.button("Entrar"):
            if pw == PASS_ADMIN:
                st.session_state.nivel = 'admin'
                st.rerun()
            else:
                st.session_state.nivel = 'usuario'
                st.session_state.usuario_pw = pw
                st.rerun()
        st.stop()

verificar_acceso()

# --- INTERFAZ ---
st.title("🛼 Galería Club Patinaje Villarrubia")

tabs = ["🖼️ Ver Galería", "📤 Subir Contenido"]
if st.session_state.nivel == 'admin':
    tabs.append("⚙️ Admin")

selector = st.tabs(tabs)

# --- PESTAÑA: ADMINISTRACIÓN ---
if st.session_state.nivel == 'admin':
    with selector[2]:
        st.subheader("Crear nueva carpeta")
        nueva_cat = st.text_input("Nombre del evento:", key="new_cat_name")
        new_pw = st.text_input("Asignar contraseña a esta carpeta:", type="password", key="new_cat_pw")
        if st.button("Crear Carpeta"):
            if nueva_cat and new_pw:
                ruta = os.path.join(CARPETA_BASE, nueva_cat)
                os.makedirs(ruta, exist_ok=True)
                st.session_state.passwords[nueva_cat] = new_pw
                st.success(f"Carpeta '{nueva_cat}' creada.")
        
        st.divider()
        st.subheader("Borrar carpeta")
        carpeta_borrar = st.selectbox("Selecciona carpeta a borrar:", os.listdir(CARPETA_BASE))
        if st.button("BORRAR CARPETA"):
            shutil.rmtree(os.path.join(CARPETA_BASE, carpeta_borrar))
            st.warning(f"Carpeta {carpeta_borrar} eliminada.")
            st.rerun()

# --- LÓGICA DE VISUALIZACIÓN Y SUBIDA ---
def obtener_carpetas():
    return [d for d in os.listdir(CARPETA_BASE) if os.path.isdir(os.path.join(CARPETA_BASE, d))]

# Pestañas Ver y Subir
for tab_idx, tab_name in enumerate(["Ver", "Subir"]):
    with selector[tab_idx]:
        cats = obtener_carpetas()
        if not cats: st.info("No hay eventos activos.")
        else:
            sel_cat = st.selectbox(f"Selecciona el evento para {tab_name}:", cats, key=f"sel_{tab_name}")
            
            # Validación de contraseña por carpeta
            pw_input = st.text_input(f"Introduce la contraseña para {sel_cat}:", type="password", key=f"pw_{tab_name}")
            
            if pw_input == st.session_state.passwords.get(sel_cat, "9999"): # 9999 es un valor por defecto que no coincide
                ruta_cat = os.path.join(CARPETA_BASE, sel_cat)
                
                if tab_idx == 0: # VER
                    archivos = [f for f in os.listdir(ruta_cat) if not f.startswith('.')]
                    cols = st.columns(3)
                    for i, f in enumerate(archivos):
                        with cols[i % 3]:
                            st.image(os.path.join(ruta_cat, f), use_container_width=True)
                            with open(os.path.join(ruta_cat, f), "rb") as file:
                                st.download_button("⬇️", file, f)
                
                else: # SUBIR
                    creador = st.text_input("Tu nombre:", key="autor")
                    files = st.file_uploader("Sube tus fotos:", accept_multiple_files=True)
                    if st.button("Confirmar subida"):
                        for f in files:
                            with open(os.path.join(ruta_cat, f"{creador}_{f.name}"), "wb") as dest:
                                dest.write(f.getbuffer())
                        st.success("¡Fotos subidas!")
            else:
                st.error("Contraseña incorrecta para este evento.")
