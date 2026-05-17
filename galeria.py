import streamlit as st
import os
import zipfile
from io import BytesIO

# Configuración de la página para ocultar menús innecesarios y optimizar espacio
st.set_page_config(
    page_title="Egipto 📸", 
    page_icon="🇪🇬", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- TRUCO CSS: CUADRÍCULA COMPACTA ESTILO GOOGLE FOTOS ---
st.markdown("""
    <style>
    /* Forzar a que todas las imágenes sean cuadraditos perfectos de 110px (capan 3 por fila en móvil) */
    [data-testid="stImage"] img {
        height: 110px !important;
        width: 110px !important;
        object-fit: cover !important;
        border-radius: 4px !important;
        margin: 0 auto !important;
    }
    /* Estilizar vídeos para que mantengan el mismo tamaño cuadrado compacto */
    [data-testid="stVideo"] video {
        height: 110px !important;
        width: 110px !important;
        object-fit: cover !important;
        border-radius: 4px !important;
    }
    /* Reducir márgenes y espacios para que todo quede pegadito y limpio */
    .block-container {
        padding: 1rem !important;
    }
    div[data-testid="stColumn"] {
        padding: 0px !important;
        margin: 0px !important;
        text-align: center;
    }
    /* Hacer el botón de borrar súper discreto debajo de la foto */
    .stButton>button {
        padding: 2px !important;
        height: 24px !important;
        font-size: 11px !important;
        margin-top: -5px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🇪🇬 Fotos Egipto")

CARPETA_EGIPTO = "fotos_egipto"
if not os.path.exists(CARPETA_EGIPTO):
    os.makedirs(CARPETA_EGIPTO)

# Pestañas para separar la vista de la subida de archivos
tab_ver, tab_subir = st.tabs(["🖼️ Galería", "📤 Subir"])

# --- PESTAÑA 1: LA REVOLUCIÓN DE LA GALERÍA COMPACTA ---
with tab_ver:
    archivos = [f for f in os.listdir(CARPETA_EGIPTO) if os.path.isfile(os.path.join(CARPETA_EGIPTO, f))]
    
    if not archivos:
        st.info("Aún no hay fotos.")
    else:
        # Botón para descargar todo el viaje en un ZIP
        buf = BytesIO()
        with zipfile.ZipFile(buf, "x", zipfile.ZIP_DEFLATED) as zip_file:
            for archivo in archivos:
                zip_file.write(os.path.join(CARPETA_EGIPTO, archivo), arcname=archivo)
        
        st.download_button(
            label="📥 Descargar todo el viaje (.ZIP)",
            data=buf.getvalue(),
            file_name="viaje_egipto.zip",
            mime="application/zip"
        )
        st.write("")

        # Creamos 3 columnas nativas. En móviles se mantendrán en filas de 3 gracias al CSS.
        columnas = st.columns(3)
        ext_fotos = ('.png', '.jpg', '.jpeg', '.webp', '.gif')

        for index, nombre_archivo in enumerate(archivos):
            col = columnas[index % 3]
            ruta_completa = os.path.join(CARPETA_EGIPTO, nombre_archivo)
            
            with col:
                # 1. Mostramos la miniatura (Foto o Vídeo)
                if nombre_archivo.lower().endswith(ext_fotos):
                    st.image(ruta_completa)
                else:
                    st.video(ruta_completa)
                
                # 2. Mini-botón para borrar la foto si se desea
                if st.button("🗑️", key=f"del_{index}"):
                    os.remove(ruta_completa)
                    st.rerun() # Arreglado el error aquí usando la función moderna .rerun()

# --- PESTAÑA 2: SECCIÓN DE SUBIDA ---
with tab_subir:
    st.subheader("📤 Sube tus fotos del carrete")
    archivos_subidos = st.file_uploader(
        "Puedes seleccionar varias a la vez:", 
        type=["png", "jpg", "jpeg", "webp", "mp4", "mov"], 
        accept_multiple_files=True
    )

    if st.button("🚀 Guardar fotos"):
        if archivos_subidos:
            for archivo in archivos_subidos:
                ruta_archivo = os.path.join(CARPETA_EGIPTO, archivo.name)
                with open(ruta_archivo, "wb") as f:
                    f.write(archivo.getbuffer())
            st.success("¡Subidas correctamente!")
            st.rerun() # Arreglado el error aquí también
        else:
            st.warning("Selecciona archivos primero.")
