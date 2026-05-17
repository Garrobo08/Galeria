import streamlit as st
import os
import zipfile
from io import BytesIO

# Configuración de la página optimizada para móvil y PC
st.set_page_config(page_title="Fotos Egipto 📸", page_icon="🇪🇬", layout="wide")

# --- ESTILOS CSS PARA CONTROLAR EL TAMÁÑO DE LAS FOTOS (TIPO INSTAGRAM) ---
st.markdown("""
    <style>
    /* Forzar a que todas las imágenes de la cuadrícula tengan un tamaño fijo y no sean gigantes */
    [data-testid="stImage"] img {
        height: 220px !important;
        object-fit: cover !important;
        border-radius: 12px !important;
        width: 100% !important;
    }
    /* Estilizar los vídeos para que no ocupen toda la pantalla */
    [data-testid="stVideo"] {
        height: 220px !important;
        border-radius: 12px !important;
        overflow: hidden;
    }
    /* Estilizar botones para que sean cómodos en el móvil */
    .stButton>button {
        border-radius: 8px;
        margin-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🇪🇬 Nuestro Viaje a Egipto")
st.write("¡Sube tus fotos/vídeos del viaje y descárgate los que te falten!")

# Carpeta única para las fotos de Egipto
CARPETA_EGIPTO = "fotos_egipto"
if not os.path.exists(CARPETA_EGIPTO):
    os.makedirs(CARPETA_EGIPTO)

# --- PESTAÑAS: VER MULTIMEDIA / SUBIR ARCHIVOS ---
tab_ver, tab_subir = st.tabs(["🖼️ Ver Galería", "📤 Subir Fotos y Vídeos"])

# --- PESTAÑA 1: VISUALIZACIÓN Y DESCARGAS ---
with tab_ver:
    archivos = [f for f in os.listdir(CARPETA_EGIPTO) if os.path.isfile(os.path.join(CARPETA_EGIPTO, f))]
    
    if not archivos:
        st.info("La galería aún está vacía. ¡Sé el primero en subir un recuerdo en la otra pestaña!")
    else:
        # Botón para descargar todo en un ZIP
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

        # Cuadrícula dinámica: 3 columnas que se adaptan solas
        columnas = st.columns(3)
        ext_fotos = ('.png', '.jpg', '.jpeg', '.webp')
        ext_videos = ('.mp4', '.mov', '.avi', '.mkv')

        for index, nombre_archivo in enumerate(archivos):
            col = columnas[index % 3]
            ruta_completa = os.path.join(CARPETA_EGIPTO, nombre_archivo)
            
            with col:
                # Mostrar archivo (el CSS de arriba controla que midan 220px de alto)
                if nombre_archivo.lower().endswith(ext_fotos):
                    st.image(ruta_completa, use_container_width=True)
                elif nombre_archivo.lower().endswith(ext_videos):
                    st.video(ruta_completa)
                
                # Nombre del archivo cortito
                st.caption(f"📄 {nombre_archivo[:18]}...")
                
                # Botones de acción debajo de cada foto
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    with open(ruta_completa, "rb") as file:
                        st.download_button(
                            label="⬇️ Bajar",
                            data=file,
                            file_name=nombre_archivo,
                            mime="application/octet-stream",
                            key=f"dl_{index}"
                        )
                with btn_col2:
                    if st.button("🗑️ Borrar", key=f"del_{index}"):
                        os.remove(ruta_completa)
                        st.rerun()

# --- PESTAÑA 2: SUBIR CONTENIDO ---
with tab_subir:
    st.subheader("📤 Añade tus recuerdos")
    archivos_subidos = st.file_uploader(
        "Selecciona fotos o vídeos desde tu móvil u ordenador:", 
        type=["png", "jpg", "jpeg", "webp", "mp4", "mov", "avi", "mkv"], 
        accept_multiple_files=True
    )

    if st.button("🚀 Guardar en la Galería"):
        if archivos_subidos:
            for archivo in archivos_subidos:
                ruta_archivo = os.path.join(CARPETA_EGIPTO, archivo.name)
                with open(ruta_archivo, "wb") as f:
                    f.write(archivo.getbuffer())
            st.success("¡Archivos añadidos a la colección de Egipto!")
            st.rerun()
        else:
            st.warning("Selecciona primero algún archivo.")
