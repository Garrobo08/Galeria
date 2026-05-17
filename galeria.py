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
    </style>
""", unsafe_allow_html=True)

st.title("🇪🇬 Nuestro Viaje a Egipto")

CARPETA_EGIPTO = "fotos_egipto"
if not os.path.exists(CARPETA_EGIPTO):
    os.makedirs(CARPETA_EGIPTO)

tab_ver, tab_subir = st.tabs(["🖼️ Ver Galería", "📤 Subir Contenido"])

# --- PESTAÑA 1: VER Y BORRAR CON CONTROL ---
with tab_ver:
    archivos = [f for f in os.listdir(CARPETA_EGIPTO) if os.path.isfile(os.path.join(CARPETA_EGIPTO, f))]
    
    if not archivos:
        st.info("La galería está vacía. ¡Sube fotos en la pestaña de al lado!")
    else:
        # Descarga completa en ZIP
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

        # Input global para saber quién está navegando (y permitirle borrar lo suyo)
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
                
                # Detectar el autor leyendo el nombre del archivo
                # El formato es "autor_nombreoriginal.jpg"
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
                            st.error("⚠️ Escribe tu nombre arriba para borrar.")
                        elif usuario_actual == autor_foto or autor_foto == "desconocido":
                            os.remove(ruta_completa)
                            st.success("¡Borrada!")
                            st.rerun()
                        else:
                            st.error(f"❌ Esta foto es de {autor_foto.capitalize()}")

        st.markdown("---")
        st.subheader("🔍 Toca para ampliar una imagen")
        # Mostrar nombres limpios en el selector (quitando el "autor_")
        opciones_ver = ["---"] + archivos
        foto_ampliada = st.selectbox("Selecciona:", opciones_ver, format_func=lambda x: x.split("_")[-1] if "_" in x else x)
        
        if foto_ampliada != "---":
            ruta_ampliada = os.path.join(CARPETA_EGIPTO, foto_ampliada)
            if foto_ampliada.lower().endswith(ext_fotos):
                st.image(ruta_ampliada, use_container_width=True)
            else:
                st.video(ruta_ampliada)

# --- PESTAÑA 2: SUBIR CON NOMBRE ---
with tab_subir:
    st.subheader("Añade tus recuerdos")
    
    # Campo obligatorio para saber de quién es la foto antes de subir
    creador = st.text_input("✍️ Tu Nombre (Obligatorio para saber que es tuya):").strip().lower()
    
    archivos_subidos = st.file_uploader(
        "Selecciona fotos o vídeos:", 
        type=["png", "jpg", "jpeg", "webp", "mp4", "mov"], 
        accept_multiple_files=True
    )

    if st.button("🚀 Guardar en la Galería"):
        if not creador:
            st.error("⚠️ Por favor, pon tu nombre antes de subir los archivos para que el sistema sepa que son tuyos.")
        elif archivos_subidos:
            for archivo in archivos_subidos:
                # Guardamos el archivo renombrándolo a: "nombre_archivofoto.jpg"
                nombre_seguro = f"{creador}_{archivo.name}"
                ruta_archivo = os.path.join(CARPETA_EGIPTO, nombre_seguro)
                with open(ruta_archivo, "wb") as f:
                    f.write(archivo.getbuffer())
            st.success("¡Archivos guardados!")
            st.rerun()
        else:
            st.warning("Selecciona primero algún archivo.")
