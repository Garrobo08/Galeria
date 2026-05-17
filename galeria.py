import streamlit as st
import os
import zipfile
from io import BytesIO

# Configuración de la página
st.set_page_config(
    page_title="Egipto 📸", 
    page_icon="🇪🇬", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- CSS PARA MANTENER LAS 3 COLUMNAS EN MÓVIL ---
st.markdown("""
    <style>
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        justify-content: flex-start !important;
        gap: 8px !important;
    }
    [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
        width: calc(33.33% - 6px) !important;
        flex: 1 1 calc(33.33% - 6px) !important;
        min-width: calc(33.33% - 6px) !important;
        padding: 0px !important;
        margin: 0px !important;
    }
    .miniatura-galeria img, .miniatura-galeria video {
        height: 110px !important;
        width: 100% !important;
        object-fit: cover !important;
        border-radius: 6px !important;
    }
    .block-container {
        padding: 1rem !important;
    }
    .stButton>button {
        padding: 2px !important;
        height: 28px !important;
        font-size: 12px !important;
        width: 100% !important;
    }
    /* Estilo especial para el botón de volver atrás para que destaque en el móvil */
    .boton-volver>button {
        height: 40px !important;
        font-size: 16px !important;
        background-color: #f0f2f6 !important;
        font-weight: bold !important;
        margin-bottom: 15px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🇪🇬 Nuestro Viaje a Egipto")

# Base de la galería
CARPETA_BASE = "fotos_egipto"

# Diccionario de categorías con sus nombres de carpeta correspondientes
CATEGORIAS = {
    "Raquel": "fotos_raquel",
    "Paco": "fotos_paco",
    "Roberto": "fotos_roberto",
    "Lourdes": "fotos_lourdes",
    "Isabel": "fotos_isabel",
    "Arturo": "fotos_arturo",
    "Begoña": "fotos_begona",
    "Javala": "fotos_javala",
    "Rubén": "fotos_ruben",
    "Caste": "fotos_caste",
    "Monumentos": "fotos_monumentos",
    "Grupos": "fotos_grupos"
}

# Inicializar carpetas físicas en el servidor
if not os.path.exists(CARPETA_BASE):
    os.makedirs(CARPETA_BASE)

for carpeta in CATEGORIAS.values():
    ruta_subcarpeta = os.path.join(CARPETA_BASE, carpeta)
    if not os.path.exists(ruta_subcarpeta):
        os.makedirs(ruta_subcarpeta)

# Inicializar estados de la sesión
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0
if "foto_seleccionada" not in st.session_state:
    st.session_state.foto_seleccionada = None

tab_ver, tab_subir = st.tabs(["🖼️ Ver Galería Web", "📤 Subir Contenido"])

# --- PESTAÑA 1: VER Y BORRAR ---
with tab_ver:
    # Selector de categoría para filtrar la vista de la galería
    categoria_vista = st.selectbox(
        "📁 Selecciona la carpeta que quieres ver:", 
        list(CATEGORIAS.keys()),
        key="selector_categoria_vista"
    )
    
    # Definir la ruta física de la subcarpeta seleccionada
    carpeta_actual = os.path.join(CARPETA_BASE, CATEGORIAS[categoria_vista])
    archivos = [f for f in os.listdir(carpeta_actual) if os.path.isfile(os.path.join(carpeta_actual, f))]
    
    if not archivos:
        st.info(f"La carpeta '{categoria_vista}' está vacía actualmente.")
    
    # MODO 1: VISTA PANTALLA COMPLETA
    elif st.session_state.foto_seleccionada is not None:
        foto_grande = st.session_state.foto_seleccionada
        ruta_ampliada = os.path.join(carpeta_actual, foto_grande)
        ext_fotos = ('.png', '.jpg', '.jpeg', '.webp', '.gif')
        
        st.markdown('<div class="boton-volver">', unsafe_allow_html=True)
        if st.button("⬅️ Volver a la galería"):
            st.session_state.foto_seleccionada = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        if foto_grande.lower().endswith(ext_fotos):
            st.image(ruta_ampliada, use_container_width=True)
        else:
            st.video(ruta_ampliada)
            
    # MODO 2: VISTA NORMAL DE LA CUADRÍCULA DE 3 COLUMNAS
    else:
        # Descarga en ZIP de la carpeta específica que se está viendo
        buf = BytesIO()
        with zipfile.ZipFile(buf, "x", zipfile.ZIP_DEFLATED) as zip_file:
            for archivo in archivos:
                zip_file.write(os.path.join(carpeta_actual, archivo), arcname=archivo)
        
        st.download_button(
            label=f"📥 Descargar Carpeta {categoria_vista} (.ZIP)",
            data=buf.getvalue(),
            file_name=f"egipto_{CATEGORIAS[categoria_vista]}.zip",
            mime="application/zip"
        )
        st.write("")

        usuario_actual = st.text_input("👤 Tu Nombre (Para poder borrar tus fotos):", key="user_global").strip().lower()

        columnas = st.columns(3)
        ext_fotos = ('.png', '.jpg', '.jpeg', '.webp', '.gif')

        for index, nombre_archivo in enumerate(archivos):
            col = columnas[index % 3]
            ruta_completa = os.path.join(carpeta_actual, nombre_archivo)
            
            with col:
                st.markdown('<div class="miniatura-galeria">', unsafe_allow_html=True)
                if nombre_archivo.lower().endswith(ext_fotos):
                    st.image(ruta_completa)
                else:
                    st.video(ruta_completa)
                st.markdown('</div>', unsafe_allow_html=True)
                
                if "_" in nombre_archivo:
                    autor_foto = nombre_archivo.split("_")[0].lower()
                else:
                    autor_foto = "desconocido"
                
                btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
                with btn_col1:
                    with open(ruta_completa, "rb") as file:
                        st.download_button(label="⬇️", data=file, file_name=nombre_archivo, mime="application/octet-stream", key=f"dl_{index}")
                with btn_col2:
                    if st.button("🔍", key=f"zoom_{index}"):
                        st.session_state.foto_seleccionada = nombre_archivo
                        st.rerun()
                with btn_col3:
                    if st.button("🗑️", key=f"del_{index}"):
                        if not usuario_actual:
                            st.toast("⚠️ Escribe tu nombre arriba para borrar.", icon="⚠️")
                        elif usuario_actual == autor_foto or autor_foto == "desconocido":
                            os.remove(ruta_completa)
                            st.toast("✅ ¡Foto borrada correctamente!", icon="🗑️")
                            st.rerun()
                        else:
                            st.toast(f"❌ Esta foto es de {autor_foto.capitalize()}", icon="❌")

# --- PESTAÑA 2: SUBIR CONTENIDO A CARPETA ESPECÍFICA ---
with tab_subir:
    st.subheader("Añade tus recuerdos")
    
    creador = st.text_input("✍️ Tu Nombre (Obligatorio para saber que es tuya):").strip().lower()
    
    # Desplegable para que el usuario elija el destino de los archivos cargados
    categoria_destino = st.selectbox(
        "📂 ¿A qué carpeta quieres subir estas fotos/vídeos?", 
        list(CATEGORIAS.keys()),
        key="selector_categoria_subir"
    )
    
    archivos_subidos = st.file_uploader(
        "Selecciona fotos o vídeos:", 
        type=["png", "jpg", "jpeg", "webp", "mp4", "mov"], 
        accept_multiple_files=True,
        key=f"uploader_{st.session_state.uploader_key}"
    )

    if st.button("🚀 Guardar en la Galería Web"):
        if not creador:
            st.error("⚠️ Por favor, pon tu nombre antes de subir.")
        elif archivos_subidos:
            # Ruta de destino según la categoría seleccionada al subir
            carpeta_destino_final = os.path.join(CARPETA_BASE, CATEGORIAS[categoria_destino])
            
            for archivo in archivos_subidos:
                nombre_seguro = f"{creador}_{archivo.name}"
                ruta_archivo = os.path.join(carpeta_destino_final, nombre_seguro)
                with open(ruta_archivo, "wb") as f:
                    f.write(archivo.getbuffer())
            
            st.session_state.uploader_key += 1
            st.success(f"¡Archivos guardados en la carpeta de {categoria_destino}!")
            st.rerun()
        else:
            st.warning("Selecciona primero algún archivo.")
