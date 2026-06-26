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
if "uploader_key" not in st.session_state: st.session_state.uploader_key = 0
# Eliminamos "acceso_carpeta" del estado permanente

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

# --- PESTAÑA ADMIN (No necesita cambios) ---
if st.session_state.nivel == 'admin':
    with selector[2]:
        st.subheader("Gestión de Carpetas")
        nueva_cat = st.text_input("Nombre del evento:", key="new_cat_admin")
        new_pw = st.text_input("Contraseña:", type="password", key="new_pw_admin")
        if st.button("Crear Carpeta"):
            if nueva_cat and new_pw:
                os.makedirs(os.path.join(CARPETA_BASE, nueva_cat), exist_ok=True)
                guardar_password(nueva_cat, new_pw)
                st.success("✅ Carpeta creada.")
                st.rerun()
        # ... (borrado igual)

# --- LÓGICA VER Y SUBIR ---
for i, tab_name in enumerate(["Ver", "Subir"]):
    with selector[i]:
        cats = ["Selecciona una carpeta..."] + [d for d in os.listdir(CARPETA_BASE) if os.path.isdir(os.path.join(CARPETA_BASE, d))]
        sel_cat = st.selectbox(f"Elige evento:", cats, key=f"sel_{tab_name}")
        
        if sel_cat != "Selecciona una carpeta...":
            # Usamos un formulario temporal para la contraseña
            pw_input = st.text_input(f"Introduce contraseña para {sel_cat}:", type="password", key=f"pw_input_{tab_name}")
            
            # Solo si el usuario pulsa el botón se verifica
            if st.button(f"Entrar a {sel_cat}", key=f"btn_check_{tab_name}"):
                passwords = cargar_passwords()
                if pw_input == passwords.get(sel_cat):
                    st.session_state[f"acceso_{tab_name}"] = True # Acceso temporal
                else:
                    st.error("❌ Contraseña incorrecta.")
                    st.session_state[f"acceso_{tab_name}"] = False

            # Comprobamos acceso temporal
            if st.session_state.get(f"acceso_{tab_name}"):
                st.success("✅ Acceso concedido.")
                ruta_cat = os.path.join(CARPETA_BASE, sel_cat)
                
                # ... (Lógica de Ver / Subir igual que antes)
            
            # OPCIÓN PARA CERRAR CARPETA:
            if st.session_state.get(f"acceso_{tab_name}"):
                if st.button("🚪 Cerrar carpeta", key=f"close_{tab_name}"):
                    st.session_state[f"acceso_{tab_name}"] = False
                    st.rerun()
