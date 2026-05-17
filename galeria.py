import streamlit as st
import os
from PIL import Image
import zipfile
from io import BytesIO

# Configuración de la página
st.set_page_config(
    page_title="Fotos de Nuestro Viaje a Egipto",
    page_icon="🇪🇬",
    layout="wide",  # Usar todo el ancho para la cuadrícula
    initial_sidebar_state="collapsed" # Ocultar la barra lateral por defecto
)

# Estilos CSS personalizados para la cuadrícula y el visor
st.markdown("""
<style>
    .gallery-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); /* Cuadrícula adaptativa */
        gap: 10px;
        padding: 20px;
    }
    .gallery-item {
        width: 100%;
        padding-top: 100%; /* Mantener aspecto cuadrado */
        position: relative;
        cursor: pointer;
        border-radius: 8px;
        overflow: hidden;
    }
    .gallery-item img {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        object-fit: cover; /* Ajustar imagen al contenedor */
        transition: transform 0.3s ease;
    }
    .gallery-item:hover img {
        transform: scale(1.05); /* Efecto de zoom al pasar el ratón */
    }
    /* Estilos para el visor a tamaño completo */
    #image-viewer {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.9);
        z-index: 999;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    #viewer-image {
        max-width: 90%;
        max-height: 90%;
    }
    #viewer-controls {
        position: absolute;
        bottom: 20px;
        display: flex;
        gap: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Directorio donde se guardan las fotos
IMAGE_DIR = "fotos_viaje"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# Estado de la sesión para controlar el visor
if 'viewer_image_path' not in st.session_state:
    st.session_state['viewer_image_path'] = None

# Función para abrir el visor
def open_viewer(image_path):
    st.session_state['viewer_image_path'] = image_path

# Función para cerrar el visor
def close_viewer():
    st.session_state['viewer_image_path'] = None

# Título y descripción
st.title("🇪🇬 Nuestro Viaje a Egipto")
st.write("¡Sube tus fotos y vídeos del viaje para compartirlos con todos!")

# --- Sección de Visualización de la Galería (Cuadrícula Compacta) ---
st.header("📸 Galería de Fotos")

# Obtener lista de imágenes
image_files = [f for f in os.listdir(IMAGE_DIR) if os.path.isfile(os.path.join(IMAGE_DIR, f))]

if image_files:
    # Contenedor de la cuadrícula
    st.markdown('<div class="gallery-grid">', unsafe_allow_html=True)

    for image_name in image_files:
        image_path = os.path.join(IMAGE_DIR, image_name)
        
        # Generar miniatura en memoria
        image = Image.open(image_path)
        image.thumbnail((200, 200))  # Tamaño de la miniatura
        thumbnail_buffer = BytesIO()
        image.save(thumbnail_buffer, format=image.format)
        thumbnail_base64 = thumbnail_buffer.getvalue()

        # Item de la galería (miniatura clickable)
        st.markdown(f"""
            <div class="gallery-item" onclick="Streamlit.setComponentValue('viewer_image_path', '{image_path}')">
                <img src="data:image/{image.format.lower()};base64,{thumbnail_base64.decode()}" alt="{image_name}">
            </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True) # Cerrar contenedor de la cuadrícula

else:
    st.info("Aún no hay fotos en la galería. ¡Sube las tuyas!")

# --- Visor a Tamaño Completo (Lógica de Streamlit) ---
if st.session_state['viewer_image_path']:
    viewer_image_path = st.session_state['viewer_image_path']
    viewer_image_name = os.path.basename(viewer_image_path)

    # Mostrar imagen a tamaño completo
    image = Image.open(viewer_image_path)
    st.image(image, caption=viewer_image_name, use_column_width=True)

    # Controles del visor
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        # Botón para descargar la foto individualmente
        with open(viewer_image_path, "rb") as file:
            st.download_button(
                label="⬇️ Descargar Foto",
                data=file,
                file_name=viewer_image_name,
                mime=f"image/{image.format.lower()}"
            )
    
    with col2:
        # Botón para eliminar la foto
        if st.button("🗑️ Eliminar Foto"):
            os.remove(viewer_image_path)
            close_viewer()
            st.experimental_rerun()  # Recargar la página para actualizar la galería

    with col3:
        # Botón para cerrar el visor
        if st.button("❌ Cerrar"):
            close_viewer()

# --- Sección para Subir Fotos y Vídeos ---
st.header("📤 Subir Fotos y Vídeos")
uploaded_files = st.file_uploader("Elige tus archivos", accept_multiple_files=True, type=['png', 'jpg', 'jpeg', 'mp4', 'mov'])

if uploaded_files:
    for uploaded_file in uploaded_files:
        # Guardar el archivo en el directorio
        with open(os.path.join(IMAGE_DIR, uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
    st.success("¡Archivos subidos correctamente!")
    st.experimental_rerun()  # Recargar la página para mostrar las nuevas fotos

# --- Sección para Descargar Todo el Viaje ---
st.header("⬇️ Descargar Todo el Viaje")

# Función para crear el archivo ZIP
def create_zip():
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for image_name in image_files:
            image_path = os.path.join(IMAGE_DIR, image_name)
            zip_file.write(image_path, image_name)
    return zip_buffer.getvalue()

if image_files:
    st.download_button(
        label="🎁 Descargar Todo el Viaje (.ZIP)",
        data=create_zip(),
        file_name="viaje_egipto.zip",
        mime="application/zip"
    )
else:
    st.warning("No hay fotos para descargar.")

# Capturar el valor del componente personalizado para abrir el visor
viewer_image_path_value = st.experimental_get_query_params().get('viewer_image_path')
if viewer_image_path_value:
    open_viewer(viewer_image_path_value[0])
    st.experimental_set_query_params() # Limpiar parámetros de consulta
