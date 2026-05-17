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

# --- CSS DEFINITIVO (MANTENE LAS 3 COLUMNAS Y OCULTA EL BOTÓN RAROS DE AMPLIAR) ---
st.markdown("""
    <style>
    /* Ocultar el botón nativo de pantalla completa (flechitas) que mete el navegador */
    button[title="View fullscreen"], .stImage button, button[aria-label="View fullscreen"] {
        display: none !important;
    }
    
    /* Mantener las 3 columnas juntas en el móvil */
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

    /* Evitar que las alertas se aplasten hacia abajo */
    [data-testid="stNotification"], [data-testid="stAlert"], .stAlert {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
        display: block !important;
    }

    /* Cuadrados perfectos estilo Google Fotos */
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
    </style>
""", unsafe_allow_html=True)

st.title("🇪🇬 Nuestro Viaje a Egipto")

CARPETA_EGIPTO = "fotos_egipto"
if not os.path.exists(CARPETA_EGIPTO):
    os.makedirs(CARPETA_EGIPTO)

# Lógica inteligente para capturar la flecha de atrás del móvil usando parámetros de la URL
query_params = st.query_params
foto_url = query_params.get("ver", None)

# Si el usuario usa la flecha del móvil, la URL limpia el parámetro y cerramos la foto
if "foto_grande" not in st.session_state:
    st.session_state.foto_grande = None

if foto_url:
    st.session_state.foto_grande = foto_url
elif st.session_state.foto_grande and not foto_url:
    st.session_state.foto_grande = None

# Inicializar clave de reinicios para el subidor de archivos
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# --- CONTROL DEL VISOR EN PANTALLA COMPLETA ---
if st.session_state.foto_grande:
    ruta_grande = os.path.join(CARPETA_EGIPTO, st.session_state.foto_grande)
    ext_fotos = ('.png', '.jpg', '.jpeg', '.webp', '.gif')
    
    # Botón grande para volver atrás de forma manual
    if st.button("⬅️ Volver a la galería web"):
        st.query_params.clear()
        st.session_state.foto_grande = None
        st.rerun()
        
    st.write("")
    
    if os.path.exists(ruta_grande):
        if ruta_grande.lower().endswith(ext_fotos):
            st.image(ruta_grande, use_container_width=True)
        else:
            st.video(ruta_grande)
    else:
        st.error("El archivo ya no existe.")
        if st.button("Regresar"):
            st.query_params.clear()
            st.rerun()
    st.stop() # Detiene la carga del resto de la web mientras se ve la foto en grande

# --- SI NO HAY FOTO EN GRANDE, MOSTRAR LA WEB NORMAL ---
tab_ver, tab_subir = st.tabs(["🖼️ Ver Galería Web", "📤 Subir Contenido"])

# --- PESTAÑA 1: MOSTRAR GALERÍA ---
with tab_ver:
    archivos = [f for f in os.listdir(CARPETA_EGIPTO) if os.path.isfile(os.path.join(CARPETA_EGIPTO, f))]
    
    if not archivos:
        st.info("La galería está vacía. ¡Sube fotos en la pestaña de al lado!")
    else:
        buf = BytesIO()
        with zipfile.ZipFile(buf, "x", zipfile.ZIP_DEFLATED) as zip_file:
            for archivo in archivos:
                zip_file.write(os.path.join(CARPETA_EGIPTO, archivo), arcname=archivo)
        
        st.download_button(
            label="📥 Descargar Todo el Viaje (.ZIP)",
            data=buf.getvalue(),
            file_name="viaje_egipto.zip",
            mime="application/zip"
        )
        st.write("")

        usuario_actual = st.text_input("👤 Tu Nombre (Para poder borrar tus fotos):", key="user_global").strip().lower()

        columnas = st.columns(3)
        ext_fotos = ('.png', '.jpg', '.jpeg', '.webp', '.gif')

        for index, nombre_archivo in enumerate(archivos):
            col = columnas[index % 3]
            ruta_completa = os.path.join(CARPETA_EGIPTO, nombre_archivo)
            
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
                
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    with open(ruta_completa, "rb") as file:
                        st.download_button(label="⬇️", data=file, file_name=nombre_archivo, mime="application/octet-stream", key=f"dl_{index}")
                with btn_col2:
                    if st.button("🗑️", key=f"del_{index}"):
                        if not usuario_actual:
                            st.error("⚠️ Pon tu nombre arriba.")
                        elif usuario_actual == autor_foto or autor_foto == "desconocido":
                            os.remove(ruta_completa)
                            st.rerun()
                        else:
                            st.error(f"❌ Es de {autor_foto.capitalize()}")

        st.markdown("---")
        st.subheader("🔍 Toca para ampliar una imagen")
        opciones_ver = ["---"] + archivos
        foto_ampliada = st.selectbox("Selecciona:", opciones_ver, format_func=lambda x: x.split("_")[-1] if "_" in x else x)
        
        if foto_ampliada != "---":
            # Guardamos en la URL que estamos viendo esta foto
            st.query_params.ver = foto_ampliada
            st.rerun()

# --- PESTAÑA 2: SUBIR CONTENIDO ---
with tab_subir:
    st.subheader("Añade tus recuerdos")
    creador = st.text_input("✍️ Tu Nombre (Obligatorio para saber que es tuya):").strip().lower()
    
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
            for archivo in archivos_subidos:
                nombre_seguro = f"{creador}_{archivo.name}"
                ruta_archivo = os.path.join(CARPETA_EGIPTO, nombre_seguro)
                with open(ruta_archivo, "wb") as f:
                    f.write(archivo.getbuffer())
            st.session_state.uploader_key += 1
            st.success("¡Archivos guardados!")
            st.rerun()
        else:
            st.warning("Selecciona primero algún archivo.")
