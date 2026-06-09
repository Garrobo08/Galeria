import streamlit as st
import os
import zipfile
from io import BytesIO

st.set_page_config(page_title="Galería Patinaje Villarrubia", page_icon="🛼", layout="wide")

# --- CSS MEJORADO PARA GRID RESPONSIVO ---
st.markdown("""
    <style>
    .miniatura-galeria { margin-bottom: 10px; }
    .miniatura-galeria img, .miniatura-galeria video { 
        width: 100%; aspect-ratio: 1/1; object-fit: cover; border-radius: 8px; 
    }
    </style>
""", unsafe_allow_html=True)

CARPETA_BASE = "galeria_patinaje"
if not os.path.exists(CARPETA_BASE): os.makedirs(CARPETA_BASE)

# --- ESTADOS ---
if "uploader_key" not in st.session_state: st.session_state.uploader_key = 0
if "foto_sel" not in st.session_state: st.session_state.foto_sel = None

def obtener_carpetas():
    return sorted([d for d in os.listdir(CARPETA_BASE) if os.path.isdir(os.path.join(CARPETA_BASE, d))])

tab_ver, tab_subir, tab_config = st.tabs(["🖼️ Galería", "📤 Subir", "➕ Crear Carpeta"])

# --- TAB: CREAR CARPETA (Limpia el input automáticamente) ---
with tab_config:
    # Usamos un key específico para resetearlo después
    nueva_cat = st.text_input("Nombre de la nueva carpeta:", key="input_nueva_carpeta")
    if st.button("Crear"):
        if nueva_cat:
            ruta = os.path.join(CARPETA_BASE, nueva_cat)
            if not os.path.exists(ruta):
                os.makedirs(ruta)
                st.success(f"Carpeta '{nueva_cat}' creada.")
                st.rerun() # Esto refresca y limpia el input gracias al key
            else:
                st.error("Ya existe.")

# --- TAB: VER GALERÍA ---
with tab_ver:
    carpetas = obtener_carpetas()
    if carpetas:
        cat_select = st.selectbox("Elige un evento:", carpetas)
        ruta_cat = os.path.join(CARPETA_BASE, cat_select)
        archivos = [f for f in os.listdir(ruta_cat) if not f.startswith('.')]
        
        # Botón descarga ZIP
        buf = BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            for f in archivos: z.write(os.path.join(ruta_cat, f), f)
        st.download_button("📥 Descargar todo el evento", buf.getvalue(), f"{cat_select}.zip", "application/zip")
        
        # GRID DE FOTOS
        cols = st.columns([1, 1, 1]) # Grid responsivo para móvil y PC
        for i, archivo in enumerate(archivos):
            with cols[i % 3]:
                ruta_img = os.path.join(ruta_cat, archivo)
                st.markdown('<div class="miniatura-galeria">', unsafe_allow_html=True)
                st.image(ruta_img, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                # Botón descarga individual
                with open(ruta_img, "rb") as f:
                    st.download_button("⬇️", f, archivo, key=f"dl_{i}")
    else:
        st.info("Crea tu primera carpeta en la pestaña 'Crear Carpeta'.")

# --- TAB: SUBIR ---
with tab_subir:
    cat_destino = st.selectbox("Destino:", obtener_carpetas())
    creador = st.text_input("Tu nombre:")
    files = st.file_uploader("Fotos", accept_multiple_files=True, key=f"up_{st.session_state.uploader_key}")
    
    if st.button("Subir archivos"):
        if creador and files:
            for f in files:
                with open(os.path.join(CARPETA_BASE, cat_destino, f"{creador}_{f.name}"), "wb") as destino:
                    destino.write(f.getbuffer())
            st.session_state.uploader_key += 1
            st.success("Subido.")
            st.rerun()
