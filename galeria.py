import streamlit as st
import os
import shutil

# --- CONFIGURACIÓN ---
CARPETA_BASE = "galeria_patinaje"
ARCHIVO_PW = "passwords.txt"
PASS_ADMIN = "AdminVillarrubia2026" 

if not os.path.exists(CARPETA_BASE): os.makedirs(CARPETA_BASE)

def cargar_passwords():
    if not os.path.exists(ARCHIVO_PW): return {}
    with open(ARCHIVO_PW, "r") as f:
        return dict(line.strip().split(":") for line in f if ":" in line)

def guardar_password(carpeta, password):
    pws = cargar_passwords()
    pws[carpeta] = password
    with open(ARCHIVO_PW, "w") as f:
        for c, p in pws.items(): f.write(f"{c}:{p}\n")

# --- ESTADOS ---
if "nivel" not in st.session_state: st.session_state.nivel = None
if "acceso_carpeta" not in st.session_state: st.session_state.acceso_carpeta = None
if "uploader_key" not in st.session_state: st.session_state.uploader_key = 0

def verificar_acceso():
    if st.session_state.nivel is None:
        st.title("🔐 Acceso al Club")
        pw = st.text_input("Introduce tu contraseña:", type="password")
        if st.button("Entrar"):
            if pw == PASS_ADMIN: st.session_state.nivel = 'admin'
            else: st.session_state.nivel = 'usuario'
            st.rerun()
        st.stop()

verificar_acceso()

st.title("🛼 Galería Club Patinaje Villarrubia")

tabs = ["🖼️ Ver Galería", "📤 Subir Contenido"]
if st.session_state.nivel == 'admin': tabs.append("⚙️ Admin")
selector = st.tabs(tabs)

# --- PESTAÑA ADMIN ---
if st.session_state.nivel == 'admin':
    with selector[2]:
        st.subheader("Gestión de Carpetas")
        nueva_cat = st.text_input("Nombre del evento:", key="new_cat_name")
        new_pw = st.text_input("Contraseña para el evento:", type="password", key="new_cat_pw")
        if st.button("Crear Carpeta"):
            if nueva_cat and new_pw:
                os.makedirs(os.path.join(CARPETA_BASE, nueva_cat), exist_ok=True)
                guardar_password(nueva_cat, new_pw)
                st.success(f"Carpeta '{nueva_cat}' creada.")
                st.rerun()

        carpeta_borrar = st.selectbox("Borrar carpeta:", ["Selecciona una carpeta..."] + os.listdir(CARPETA_BASE))
        if carpeta_borrar != "Selecciona una carpeta..." and st.button("BORRAR"):
            shutil.rmtree(os.path.join(CARPETA_BASE, carpeta_borrar))
            st.rerun()

# --- LÓGICA VER Y SUBIR ---
for i, tab_name in enumerate(["Ver", "Subir"]):
    with selector[i]:
        cats = ["Selecciona una carpeta..."] + [d for d in os.listdir(CARPETA_BASE) if os.path.isdir(os.path.join(CARPETA_BASE, d))]
        sel_cat = st.selectbox(f"Elige evento:", cats, key=f"sel_{tab_name}")
        
        if sel_cat != "Selecciona una carpeta...":
            pw_input = st.text_input(f"Contraseña para {sel_cat}:", type="password", key=f"pw_{tab_name}")
            
            if st.button(f"Acceder a {sel_cat}", key=f"btn_acc_{tab_name}"):
                passwords = cargar_passwords()
                if pw_input == passwords.get(sel_cat):
                    st.session_state.acceso_carpeta = sel_cat
                else:
                    st.error("Contraseña incorrecta.")
                    st.session_state.acceso_carpeta = None
            
            if st.session_state.acceso_carpeta == sel_cat:
                ruta_cat = os.path.join(CARPETA_BASE, sel_cat)
                if i == 0: # VER
                    archivos = [f for f in os.listdir(ruta_cat) if not f.startswith('.')]
                    cols = st.columns(3)
                    for idx, f in enumerate(archivos):
                        with cols[idx % 3]:
                            st.image(os.path.join(ruta_cat, f), use_container_width=True)
                            with open(os.path.join(ruta_cat, f), "rb") as file:
                                st.download_button("⬇️", file, f, key=f"dl_{tab_name}_{idx}")
                else: # SUBIR
                    creador = st.text_input("Tu nombre:", key="autor_input")
                    files = st.file_uploader("Fotos:", accept_multiple_files=True, key=f"up_{st.session_state.uploader_key}")
                    
                    if st.button("Confirmar subida"):
                        if creador and files:
                            for f in files:
                                with open(os.path.join(ruta_cat, f"{creador}_{f.name}"), "wb") as dest:
                                    dest.write(f.getbuffer())
                            st.success("Subido con éxito.")
                            # Incrementar la key fuerza al uploader y al input a limpiarse
                            st.session_state.uploader_key += 1
                            st.rerun()
