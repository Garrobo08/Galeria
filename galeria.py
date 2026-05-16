import streamlit as st
import os
import zipfile
import json
from io import BytesIO

# Configuración de la página
st.set_page_config(page_title="Galería Privada", page_icon="🔐", layout="wide")
st.title("📸 Galería Multimedia Privada y Compartida")

# --- CONFIGURACIÓN DE ARCHIVOS Y CARPETAS ---
BASE_DIR = "galeria_privada"
DATA_FILE = "usuarios_y_permisos.json"

if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

# Inicializar base de datos simulada en JSON (Usuarios y Permisos)
if not os.path.exists(DATA_FILE):
    datos_iniciales = {
        "usuarios": {},  # "usuario": "contraseña"
        "albumes_permisos": {}  # "nombre_album": {"creador": "user", "invitados": ["user2"]}
    }
    with open(DATA_FILE, "w") as f:
        json.dump(datos_iniciales, f)

def cargar_datos():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def guardar_datos(datos):
    with open(DATA_FILE, "w") as f:
        json.dump(datos, f, indent=4)

datos_app = cargar_datos()

# --- SISTEMA DE LOGIN / REGISTRO ---
if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = None

if st.session_state.usuario_actual is None:
    st.subheader("🔑 Inicia sesión o Regístrate para acceder")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Iniciar Sesión")
        login_user = st.text_input("Usuario", key="login_u").strip().lower()
        login_pass = st.text_input("Contraseña", type="password", key="login_p")
        if st.button("Entrar"):
            if login_user in datos_app["usuarios"] and datos_app["usuarios"][login_user] == login_pass:
                st.session_state.usuario_actual = login_user
                st.success(f"¡Bienvenido/a {login_user}!")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")
                
    with col2:
        st.markdown("### Crear Cuenta Nueva")
        reg_user = st.text_input("Elige Usuario", key="reg_u").strip().lower()
        reg_pass = st.text_input("Elige Contraseña", type="password", key="reg_p")
        if st.button("Registrarse"):
            if not reg_user or not reg_pass:
                st.error("Por favor, rellena ambos campos.")
            elif reg_user in datos_app["usuarios"]:
                st.error("Este usuario ya existe.")
            else:
                datos_app["usuarios"][reg_user] = reg_pass
                guardar_datos(datos_app)
                st.success("¡Cuenta creada con éxito! Ya puedes iniciar sesión a la izquierda.")
    st.stop()

# Si ya está logueado, mostramos la App
usuario = st.session_state.usuario_actual
st.sidebar.write(f"👤 Conectado como: **{usuario}**")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.usuario_actual = None
    st.rerun()

st.sidebar.markdown("---")

# --- FILTRAR ÁLBUMES PRIVADOS ---
def obtener_albumes_visibles(user):
    albumes = []
    for alb, info in datos_app["albumes_permisos"].items():
        if info["creador"] == user or user in info["invitados"]:
            # Verificar que la carpeta físicamente exista
            if os.path.exists(os.path.join(BASE_DIR, alb)):
                albumes.append(alb)
    return albumes

# --- BARRA LATERAL: GESTIÓN DE ÁLBUMES ---
st.sidebar.header("📁 Mis Álbumes")

nuevo_album = st.sidebar.text_input("Crear nuevo álbum privado (ej: Egipto):").strip()
if st.sidebar.button("Crear Álbum"):
    if nuevo_album:
        ruta_nuevo_album = os.path.join(BASE_DIR, nuevo_album)
        if nuevo_album not in datos_app["albumes_permisos"]:
            os.makedirs(ruta_nuevo_album, exist_ok=True)
            # Registrar al creador del álbum
            datos_app["albumes_permisos"][nuevo_album] = {
                "creador": usuario,
                "invitados": []
            }
            guardar_datos(datos_app)
            st.sidebar.success(f"Álbum '{nuevo_album}' creado.")
            st.rerun()
        else:
            st.sidebar.warning("Ese álbum ya existe en el sistema.")
    else:
        st.sidebar.error("Introduce un nombre válido.")

albumes_disponibles = obtener_albumes_visibles(usuario)

if not albumes_disponibles:
    st.info("No tienes álbumes disponibles. Crea uno en la barra lateral para empezar.")
    st.stop()

album_seleccionado = st.sidebar.selectbox("Selecciona un álbum:", albumes_disponibles)

# --- PANEL DE INVITACIONES (Solo para el Creador) ---
info_album = datos_app["albumes_permisos"][album_seleccionado]
ruta_album_actual = os.path.join(BASE_DIR, album_seleccionado)

st.header(f"📂 Álbum: {album_seleccionado}")

if info_album["creador"] == usuario:
    st.subheader("👥 Invitar amigos a este álbum")
    col_inv1, col_inv2 = st.columns([3, 1])
    with col_inv1:
        usuario_a_invitar = st.text_input("Introduce el nombre de usuario de tu amigo:", key="inv").strip().lower()
    with col_inv2:
        st.write("") # Espacio para alinear el botón
        st.write("")
        if st.button("Dar Acceso"):
            if usuario_a_invitar == usuario:
                st.error("Tú ya eres el dueño de este álbum.")
            elif usuario_a_invitar in datos_app["usuarios"]:
                if usuario_a_invitar not in info_album["invitados"]:
                    info_album["invitados"].append(usuario_a_invitar)
                    guardar_datos(datos_app)
                    st.success(f"¡{usuario_a_invitar} ahora puede ver este álbum!")
                else:
                    st.warning("Este usuario ya estaba invitado.")
            else:
                st.error("El usuario no existe. Dile que se registre primero en la web.")
    
    if info_album["invitados"]:
        st.caption(f"Personas con acceso: {', '.join(info_album['invitados'])}")
else:
    st.caption(f"🌟 Álbum compartido contigo por: **{info_album['creador']}**")

st.markdown("---")

# --- SUBIR FOTOS Y VÍDEOS ---
st.subheader("📤 Subir Fotos o Vídeos")
archivos_subidos = st.file_uploader(
    "Arrastra tus archivos multimedia", 
    type=["png", "jpg", "jpeg", "webp", "mp4", "mov", "avi", "mkv"], 
    accept_multiple_files=True
)

if st.button("Guardar Archivos"):
    if archivos_subidos:
        for archivo in archivos_subidos:
            ruta_archivo = os.path.join(ruta_album_actual, archivo.name)
            with open(ruta_archivo, "wb") as f:
                f.write(archivo.getbuffer())
        st.success(f"¡Archivos guardados en {album_seleccionado}!")
        st.rerun()

st.markdown("---")

# --- VISUALIZACIÓN, DESCARGA Y ELIMINACIÓN ---
st.subheader("🖼️ Contenido del álbum")
archivos_existentes = [f for f in os.listdir(ruta_album_actual) if os.path.isfile(os.path.join(ruta_album_actual, f))]

if not archivos_existentes:
    st.info("Este álbum está vacío.")
else:
    # ZIP de descarga completa
    buf = BytesIO()
    with zipfile.ZipFile(buf, "x", zipfile.ZIP_DEFLATED) as zip_file:
        for archivo in archivos_existentes:
            zip_file.write(os.path.join(ruta_album_actual, archivo), arcname=archivo)
    
    st.download_button(
        label="📥 Descargar Álbum Completo (.ZIP)",
        data=buf.getvalue(),
        file_name=f"{album_seleccionado}.zip",
        mime="application/zip"
    )
    
    # Cuadrícula multimedia
    columnas = st.columns(3) # 3 columnas para que los vídeos quepan mejor
    ext_fotos = ('.png', '.jpg', '.jpeg', '.webp')
    ext_videos = ('.mp4', '.mov', '.avi', '.mkv')

    for index, nombre_archivo in enumerate(archivos_existentes):
        col = columnas[index % 3]
        ruta_completa = os.path.join(ruta_album_actual, nombre_archivo)
        
        with col:
            # Renderizar según sea foto o vídeo
            if nombre_archivo.lower().endswith(ext_fotos):
                st.image(ruta_completa, use_container_width=True)
            elif nombre_archivo.lower().endswith(ext_videos):
                st.video(ruta_completa)
            
            st.caption(nombre_archivo)
            
            # Botones debajo de cada archivo: Descargar y Eliminar
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
                # Cualquiera con acceso puede descargar, pero decidimos si todos pueden borrar 
                # (en este caso, permitimos que cualquiera que tenga acceso al álbum pueda limpiarlo)
                if st.button("🗑️ Borrar", key=f"del_{index}"):
                    os.remove(ruta_completa)
                    st.success(f"Eliminado: {nombre_archivo}")
                    st.rerun()