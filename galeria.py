import streamlit as st
import os
import zipfile
import json
from io import BytesIO
import secrets

# Configuración de la página (Layout wide para que en PC aproveche el espacio)
st.set_page_config(page_title="Galería Compartida", page_icon="📸", layout="wide")

# --- ESTILOS CSS PARA HACERLO MÁS MODERNO Y MÓVIL-FRIENDLY ---
st.markdown("""
    <style>
    /* Estilizar botones principales */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 45px;
    }
    /* Hacer las tarjetas multimedia más limpias */
    .stImage, .stVideo {
        border-radius: 12px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.05);
    }
    /* Ajustar espacios en móvil */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

BASE_DIR = "galeria_privada"
DATA_FILE = "albumes_links.json"

if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

# Inicializar JSON para guardar los tokens de los enlaces
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

def cargar_datos():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def guardar_datos(datos):
    with open(DATA_FILE, "w") as f:
        json.dump(datos, f, indent=4)

datos_albumes = cargar_datos()

# --- CAPTURAR EL ENLACE DE INVITACIÓN ---
# Si la URL tiene un parámetro (?token=xxxx), cargamos ese álbum directamente
query_params = st.query_params
token_actual = query_params.get("token", None)

album_por_enlace = None
if token_actual:
    for alb, info in datos_albumes.items():
        if info["token"] == token_actual:
            album_por_enlace = alb
            break

# --- INTERFAZ PRINCIPAL ---
st.title("📸 Galería Multimedia")

# CASO 1: El usuario ha entrado a través de un enlace compartido
if album_por_enlace:
    st.info(f"📍 Estás viendo el álbum compartido: **{album_por_enlace}**")
    ruta_album_actual = os.path.join(BASE_DIR, album_por_enlace)
    album_seleccionado = album_por_enlace
    es_creador = False

# CASO 2: El usuario ha entrado a la raíz de la web (Panel de Gestión)
else:
    st.subheader("📁 Tus Álbumes")
    
    # Usamos un menú desplegable colapsable para crear álbumes y no abrumar en el móvil
    with st.expander("➕ Crear una nueva colección / álbum"):
        nuevo_album = st.text_input("Nombre del álbum (ej: Viaje Egipto):").strip()
        if st.button("Crear Álbum y Generar Enlace"):
            if nuevo_album:
                ruta_nuevo_album = os.path.join(BASE_DIR, nuevo_album)
                if nuevo_album not in datos_albumes:
                    os.makedirs(ruta_nuevo_album, exist_ok=True)
                    
                    # Generar un token único y secreto para este álbum
                    token_unico = secrets.token_urlsafe(12)
                    datos_albumes[nuevo_album] = {
                        "token": token_unico
                    }
                    guardar_datos(datos_albumes)
                    st.success(f"¡Álbum '{nuevo_album}' creado!")
                    st.rerun()
                else:
                    st.warning("Ese álbum ya existe.")
            else:
                st.error("Introduce un nombre válido.")

    # Listar álbumes creados en este PC
    lista_albumes = list(datos_albumes.keys())
    if not lista_albumes:
        st.markdown("### 👋 ¡Bienvenido/a!")
        st.info("Aún no tienes álbumes creados. Abre la pestaña de arriba para crear el primero.")
        st.stop()
        
    album_seleccionado = st.selectbox("Selecciona un álbum para gestionar:", lista_albumes)
    ruta_album_actual = os.path.join(BASE_DIR, album_seleccionado)
    es_creador = True

    # Mostrar enlace para compartir
    token_alb = datos_albumes[album_seleccionado]["token"]
    
    # Intentar detectar la URL base automáticamente, si no usa localhost por defecto
    url_base = "http://localhost:8501"
    enlace_compartir = f"{url_base}/?token={token_alb}"
    
    st.markdown("### 🔗 Enlace para compartir")
    st.code(enlace_compartir, language="text")
    st.caption("Copia este enlace de arriba y envíaselo a tus amigos. Quien lo tenga podrá ver, subir y borrar archivos en este álbum sin necesidad de registrarse.")

st.markdown("---")

# --- PESTAÑAS (TABS): DISEÑO LIMPIO PARA MÓVIL ---
# En vez de tener todo vertical, usamos pestañas para separar la visualización de la subida.
tab_ver, tab_subir = st.tabs(["🖼️ Ver Colección", "📤 Subir Archivos"])

# --- PESTAÑA 1: VER, DESCARGAR Y BORRAR ---
with tab_ver:
    if os.path.exists(ruta_album_actual):
        archivos_existentes = [f for f in os.listdir(ruta_album_actual) if os.path.isfile(os.path.join(ruta_album_actual, f))]
    else:
        archivos_existentes = []

    if not archivos_existentes:
        st.info("Este álbum está vacío. Ve a la pestaña 'Subir Archivos' para añadir fotos o vídeos.")
    else:
        # Botón de descarga completa optimizado
        buf = BytesIO()
        with zipfile.ZipFile(buf, "x", zipfile.ZIP_DEFLATED) as zip_file:
            for archivo in archivos_existentes:
                zip_file.write(os.path.join(ruta_album_actual, archivo), arcname=archivo)
        
        st.download_button(
            label="📥 Descargar Todo el Álbum (.ZIP)",
            data=buf.getvalue(),
            file_name=f"{album_seleccionado}.zip",
            mime="application/zip"
        )
        st.write("")

        # Forzamos una cuadrícula de 3 columnas para que quepan varias en pantalla
        columnas = st.columns(3)
        ext_fotos = ('.png', '.jpg', '.jpeg', '.webp')
        ext_videos = ('.mp4', '.mov', '.avi', '.mkv')

        for index, nombre_archivo in enumerate(archivos_existentes):
            col = columnas[index % 3]
            ruta_completa = os.path.join(ruta_album_actual, nombre_archivo)
            
            with col:
                # Usamos HTML/CSS personalizado para limitar la altura máxima de las imágenes/vídeos
                # Esto evita que se vuelvan gigantes y permite ver el botón de descarga sin hacer scroll
                if nombre_archivo.lower().endswith(ext_fotos):
                    st.markdown(
                        f"""
                        <div style="display: flex; justify-content: center; align-items: center; background-color: #f0f2f6; border-radius: 12px; height: 200px; overflow: hidden; margin-bottom: 5px;">
                            <img src="data:image/png;base64," style="max-height: 200px; max-width: 100%; object-fit: cover;" />
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                    # Mantenemos el st.image nativo pero con el tamaño controlado por el contenedor superior
                    st.image(ruta_completa, use_container_width=True)
                    
                elif nombre_archivo.lower().endswith(ext_videos):
                    # Para los vídeos limitamos su contenedor vertical
                    st.video(ruta_completa)
                
                st.caption(f"📄 {nombre_archivo[:15]}...") # Cortamos nombres muy largos para no romper el diseño
                
                # Botones de acción compactos alineados en horizontal abajo del archivo
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
# --- PESTAÑA 2: SUBIR ARCHIVOS ---
with tab_subir:
    st.subheader("Añadir contenido")
    archivos_subidos = st.file_uploader(
        "Selecciona fotos o vídeos de tu carrete:", 
        type=["png", "jpg", "jpeg", "webp", "mp4", "mov", "avi", "mkv"], 
        accept_multiple_files=True
    )

    if st.button("🚀 Guardar Archivos en el Álbum"):
        if archivos_subidos:
            for archivo in archivos_subidos:
                ruta_archivo = os.path.join(ruta_album_actual, archivo.name)
                with open(ruta_archivo, "wb") as f:
                    f.write(archivo.getbuffer())
            st.success("¡Archivos subidos correctamente!")
            st.rerun()
        else:
            st.warning("No has seleccionado ningún archivo.")
