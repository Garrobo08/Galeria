import streamlit as st
import os
import zipfile
import base64
from io import BytesIO

# Configuración de la página
st.set_page_config(page_title="Fotos Egipto 📸", page_icon="🇪🇬", layout="wide")

# --- DISEÑO RESPONSIVO CON CSS GRID (2 COLUMNAS EN MÓVIL, 4 EN PC) ---
st.markdown("""
    <style>
    /* Creamos una cuadrícula que se adapta sola al tamaño de la pantalla */
    .galeria-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr); /* Por defecto: 2 columnas (Móvil) */
        gap: 12px;
        padding: 10px 0;
    }
    
    /* Si la pantalla es grande (Ordenador), cambiamos automáticamente a 4 columnas */
    @media (min-width: 768px) {
        .galeria-grid {
            grid-template-columns: repeat(4, 1fr);
        }
    }
    
    /* Estilo para cada tarjeta de foto/vídeo */
    .tarjeta-media {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 8px;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.05);
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    
    /* Forzar tamaño fijo y recorte tipo Instagram en las imágenes del Grid HTML */
    .tarjeta-media img, .tarjeta-media video {
        height: 160px !important;
        width: 100% !important;
        object-fit: cover !important;
        border-radius: 8px !important;
    }
    
    /* Ajustar tamaño en PC para que luzcan un poco más grandes */
    @media (min-width: 768px) {
        .tarjeta-media img, .tarjeta-media video {
            height: 200px !important;
        }
    }
    
    /* Hacer los botones más compactos para que quepan en horizontal en el móvil */
    .botón-contenedor {
        display: flex;
        gap: 6px;
        width: 100%;
        margin-top: 8px;
    }
    
    .stButton>button {
        width: 100% !important;
        padding: 4px 8px !important;
        height: 35px !important;
        font-size: 13px !important;
        border-radius: 6px !important;
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
    if os.path.exists(CARPETA_EGIPTO):
        archivos = [f for f in os.listdir(CARPETA_EGIPTO) if os.path.isfile(os.path.join(CARPETA_EGIPTO, f))]
    else:
        archivos = []
    
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

        # --- AQUÍ EMPIEZA EL GRID RESPONSIVO ---
        # Abrimos el contenedor de la galería
        grid_html = '<div class="galeria-grid">'
        st.markdown(grid_html, unsafe_allow_html=True)
        
        ext_fotos = ('.png', '.jpg', '.jpeg', '.webp')
        ext_videos = ('.mp4', '.mov', '.avi', '.mkv')

        for index, nombre_archivo in enumerate(archivos):
            ruta_completa = os.path.join(CARPETA_EGIPTO, nombre_archivo)
            
            # Para renderizar las imágenes dentro de nuestro CSS Grid propio, 
            # necesitamos codificarlas en base64 para que el navegador las lea directamente.
            try:
                with open(ruta_completa, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode()
                
                # Crear la tarjeta para cada elemento
                st.markdown('<div class="tarjeta-media">', unsafe_allow_html=True)
                
                if nombre_archivo.lower().endswith(ext_fotos):
                    st.markdown(f'<img src="data:image/jpeg;base64,{encoded_string}">', unsafe_allow_html=True)
                elif nombre_archivo.lower().endswith(ext_videos):
                    st.markdown(f'<video controls><source src="data:video/mp4;base64,{encoded_string}" type="video/mp4"></video>', unsafe_allow_html=True)
                
                st.caption(f"📄 {nombre_archivo[:12]}...")
                
                # Renderizamos los botones nativos de Streamlit de forma compacta
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    with open(ruta_completa, "rb") as file:
                        st.download_button(label="⬇️ Bajar", data=file, file_name=nombre_archivo, mime="application/octet-stream", key=f"dl_{index}")
                with col_btn2:
                    if st.button("🗑️ Borrar", key=f"del_{index}"):
                        os.remove(ruta_completa)
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True) # Cierra tarjeta-media
            except Exception as e:
                pass
                
        st.markdown('</div>', unsafe_allow_html=True) # Cierra galeria-grid

# --- PESTAÑA 2: SUBIR CONTENIDO ---
with tab_subir:
    st.subheader("Añade tus recuerdos")
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
