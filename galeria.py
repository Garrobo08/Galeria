import streamlit as st
import os
import zipfile
from io import BytesIO

# Configuración de la página
st.set_page_config(
    page_title="Galería Patinaje Villarrubia", 
    page_icon="🛼", 
    layout="wide"
)

# --- CSS (Se mantiene igual que el tuyo) ---
st.markdown("""
    <style>
    [data-testid="stHorizontalBlock"] { display: flex !important; flex-wrap: wrap !important; gap: 8px !important; }
    .miniatura-galeria img, .miniatura-galeria video { height: 110px !important; width: 100% !important; object-fit: cover !important; border-radius: 6px !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🛼 Galería Club Patinaje Villarrubia")

CARPETA_BASE = "galeria_patinaje"

if not os.path.exists(CARPETA_BASE):
    os.makedirs(CARPETA_BASE)

# --- LÓGICA DE CARPETAS DINÁMICAS ---
def obtener_carpetas():
    return [d for d in os.listdir(CARPETA_BASE) if os.path.isdir(os.path.join(CARPETA_BASE, d))]

# Inicializar estados
if "uploader_key" not in st.session_state: st.session_state.uploader_key = 0
if "foto_seleccionada" not in st.session_state: st.session_state.foto_seleccionada = None

tab_ver, tab_subir, tab_config = st.tabs(["🖼️ Ver Galería", "📤 Subir Contenido", "➕ Nueva Carpeta"])

# --- PESTAÑA: NUEVA CARPETA ---
with tab_config:
    nueva_cat = st.text_input("Nombre de la nueva carpeta (ej: Festival Verano 2026):")
    if st.button("Crear Carpeta"):
        if nueva_cat:
            ruta_nueva = os.path.join(CARPETA_BASE, nueva_cat)
            if not os.path.exists(ruta_nueva):
                os.makedirs(ruta_nueva)
                st.success(f"Carpeta '{nueva_cat}' creada.")
                st.rerun()
            else:
                st.error("Esta carpeta ya existe.")

# --- PESTAÑA: VER ---
with tab_ver:
    carpetas_disponibles = obtener_carpetas()
    if not carpetas_disponibles:
        st.info("No hay carpetas creadas. ¡Crea una en la pestaña 'Nueva Carpeta'!")
    else:
        categoria_vista = st.selectbox("Selecciona una categoría:", carpetas_disponibles)
        carpeta_actual = os.path.join(CARPETA_BASE, categoria_vista)
        archivos = [f for f in os.listdir(carpeta_actual) if os.path.isfile(os.path.join(carpeta_actual, f))]
        
        # Lógica de visualización (igual a la tuya, solo adaptada)
        if st.session_state.foto_seleccionada:
            if st.button("⬅️ Volver"):
                st.session_state.foto_seleccionada = None
                st.rerun()
            st.image(os.path.join(carpeta_actual, st.session_state.foto_seleccionada))
        else:
            # Aquí iría tu lógica de grid y borrado (reutiliza tu bloque de "MODO 2")
            st.write(f"Archivos en {categoria_vista}: {len(archivos)}")

# --- PESTAÑA: SUBIR ---
with tab_subir:
    carpetas_disponibles = obtener_carpetas()
    if not carpetas_disponibles:
        st.warning("Crea una carpeta primero.")
    else:
        categoria_destino = st.selectbox("Elegir carpeta destino:", carpetas_disponibles)
        creador = st.text_input("Tu Nombre:")
        archivos_subidos = st.file_uploader("Sube fotos/vídeos", accept_multiple_files=True)
        
        if st.button("🚀 Guardar"):
            if creador and archivos_subidos:
                for archivo in archivos_subidos:
                    ruta = os.path.join(CARPETA_BASE, categoria_destino, f"{creador}_{archivo.name}")
                    with open(ruta, "wb") as f: f.write(archivo.getbuffer())
                st.success("Subido con éxito.")
                st.rerun()
