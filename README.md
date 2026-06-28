# 🛼 Galería Club Patinaje Villarrubia

App Streamlit con almacenamiento persistente en Supabase.

## Configuración inicial en Supabase

### 1. Crea el proyecto
- Ve a https://supabase.com y crea una cuenta gratuita
- Crea un nuevo proyecto

### 2. Crea la tabla de eventos
En el SQL Editor de Supabase ejecuta:

```sql
create table eventos (
  id bigint generated always as identity primary key,
  nombre text unique not null,
  password text not null
);
```

### 3. Crea el bucket de almacenamiento
- Ve a Storage → New bucket
- Nombre: `galeria-patinaje`
- Marca "Public bucket" ✅

### 4. Configura las variables secretas
Crea el archivo `.streamlit/secrets.toml` con:

```toml
SUPABASE_URL = "https://xxxxxxxxxxxx.supabase.co"
SUPABASE_KEY = "eyJ..."   # anon public key
PASS_ADMIN = "AdminVillarrubia2026"
```

En Streamlit Cloud, añade estos mismos valores en: App → Settings → Secrets

## Despliegue en Streamlit Cloud

1. Sube este repositorio a GitHub
2. Ve a https://share.streamlit.io
3. Conecta el repo y selecciona `galeria.py`
4. En Settings → Secrets, pega el contenido del secrets.toml
5. Deploy ✅
