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

# --- CSS DEFINITIVO PARA MÓVIL Y ORDENADOR ---
st.markdown("""
    <style>
    /* TRUCO MAESTRO: Obliga a Streamlit a mantener las 3 columnas juntas en el móvil y no saltar de línea */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        justify-content: flex-start !important;
        gap: 8px !important;
    }
    
    /* Cada columna ocupará un tercio del espacio restando el hueco */
    [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
        width: calc(33.33% - 6px) !important;
        flex: 1 1 calc(33.33% - 6px) !important;
        min-width: calc(33.33% - 6px) !important;
        padding: 0px !important;
        margin: 0px !important;
    }

    /* Las miniaturas de la galería serán cuadrados perfectos estilo Google Fotos */
    .miniatura-galeria img, .miniatura-galeria video {
        height: 110px !important;
        width: 100% !important;
        object-fit: cover !important;
        border-radius: 6px !important;
    }

    /* Reducir los espacios globales para que todo se vea más recogido */
    .block-container {
        padding: 1rem !important;
    }
    
    /* Estilo para los botones pequeños debajo de las fotos */
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

# Pestañas limpias para móvil
tab_ver, tab_subir = st.tabs(["🖼️ Ver Galería", "📤 Subir Contenido"])

# --- PESTAÑA 1: REPOSITORIO DE FOTOS ---
with tab_ver:
    archivos = [f for f in os.listdir(CARPETA_EGIPTO) if os.path.isfile(os.path.join(CARPETA_EGIPTO, f))]
    
    if not archivos:
        st.info("La galería está vacía. ¡Sube fotos en la pestaña de al lado!")
    else:
        # Botón para descargar todo el paquete ZIP
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

        # Creamos una fila de 3 columnas fijas
        columnas = st.columns(3)
        ext_fotos = ('.png', '.jpg', '.jpeg', '.webp', '.gif')

        for index, nombre_archivo in enumerate(archivos):
            col = columnas[index % 3]
            ruta_completa = os.path.join(CARPETA_EGIPTO, nombre_archivo)
            
            with col:
                # Envolvemos en un contenedor personalizado para aplicar el tamaño de miniatura cuadrado
                st.markdown('<div class="miniatura-galeria">', unsafe_allow_html=True)
                if nombre_archivo.lower().endswith(ext_fotos):
                    st.image(ruta_completa)
                else:
                    st.video(ruta_completa)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Botones de acción compactos
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    with open(ruta_completa, "rb") as file:
                        st.download_button(
                            label="⬇️", 
                            data=file, 
                            file_name=nombre_archivo, 
                            mime="application/octet-stream", 
                            key=f"dl_{index}"
                        )
                with btn_col2:
                    if st.button("🗑️", key=f"del_{index}"):
                        os.remove(ruta_completa)
                        st.rerun()

        st.markdown("---")
        # --- SECCIÓN EXTRA: VER EN GRANDE ---
        st.subheader("🔍 Toca para ampliar una imagen")
        foto_ampliada = st.selectbox("Selecciona qué foto quieres ver a tamaño completo:", ["---"] + archivos)
        if foto_ampliada != "---":
            ruta_ampliada = os.path.join(CARPETA_EGIPTO, foto_ampliada)
            # Aquí la mostramos con el componente normal sin aplicar las restricciones de miniatura
            if foto_ampliada.lower().endswith(ext_fotos):
                st.image(ruta_ampliada, use_container_width=True)
            else:
                st.video(ruta_ampliada)

# --- PESTAÑA 2: SUBIR CONTENIDO ---
with tab_subir:
    st.subheader("Añade tus recuerdos")
    archivos_subidos = st.file_uploader(
        "Selecciona fotos o vídeos desde tu móvil:", 
        type=["png", "jpg", "jpeg", "webp", "mp4", "mov"], 
        accept_multiple_files=True
    )

    if st.button("🚀 Guardar en la Galería"):
        if archivos_subidos:
            for archivo in archivos_subidos:
                ruta_archivo = os.path.join(CARPETA_EGIPTO, archivo.name)
                with open(ruta_archivo, "wb") as f:
                    f.write(archivo.getbuffer())
            st.success("¡Archivos guardados!")
            st.rerun()
        else:
            st.warning("Selecciona primero algún archivo.")
