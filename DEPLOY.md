# Despliegue de Mecatech — Railway + Supabase

## Arquitectura

```
Browser / Celular
       │
       ▼
  Railway.app          ← corre el app Streamlit (Python)
       │
       ▼
  Supabase             ← base de datos permanente (PostgreSQL)
```

---

## Railway

**URL del app:** `https://mecatechdatabase.up.railway.app`

**Qué hace Railway:**
- Corre el archivo `FrontEnd/ventas_app_simple.py` con Streamlit
- Cada vez que se hace `git push` a `main`, redespliega automáticamente
- Los archivos del repo se resetean en cada deploy → por eso usamos Supabase para los datos

**Archivos de configuración:**
- `railway.toml` → define el comando de inicio y el puerto (8501)
- `nixpacks.toml` → define cómo construir el entorno Python
- `Procfile` → alternativa al comando de inicio
- `requirements.txt` → dependencias Python

**Variables de entorno en Railway** (Service → Variables):

| Variable | Descripción |
|----------|-------------|
| `SUPABASE_URL` | URL del proyecto Supabase (ej: `https://xxx.supabase.co`) |
| `SUPABASE_KEY` | Clave anon/public de Supabase |

> Para editar variables: Railway dashboard → tu servicio → pestaña **Variables**

---

## Supabase

**Qué hace Supabase:**
- Guarda clientes, pedidos y pagos de forma permanente
- Se puede ver y editar en `supabase.com` → Table Editor (como una planilla)
- No se borra nunca aunque se redespliege el app

**Tablas creadas:**

| Tabla | Contenido |
|-------|-----------|
| `clientes` | nombre + password de cada cliente |
| `pedidos` | todos los pedidos registrados |
| `pagos` | todos los pagos registrados |

> El catálogo de productos (`mecatech_database.json`) sigue en el repo, es solo lectura.

**Para ver los datos:** supabase.com → tu proyecto → **Table Editor**

**Para recrear las tablas desde cero:** ejecutar el archivo `supabase_setup.sql` en
supabase.com → **SQL Editor** → New query → pegar el contenido → Run

---

## Cómo obtener las credenciales de Supabase

1. Ir a `supabase.com` → tu proyecto
2. Click en **Settings** (engranaje, abajo a la izquierda)
3. Click en **API**
4. Copiar:
   - **Project URL** → es el `SUPABASE_URL`
   - **anon public** key → es el `SUPABASE_KEY`

---

## Flujo de trabajo normal

```
Editar código en VS Code
        │
        ▼
   git add .
   git commit -m "mensaje"
   git push
        │
        ▼
Railway redespliega automáticamente (~2 min)
        │
        ▼
App actualizado en la URL pública
```

---

## Indicadores del app

En el sidebar del app aparece:

- 🟢 **Supabase conectado** → todo funciona, los datos se guardan en la nube
- 🟡 **Modo local (CSV/JSON)** → Supabase no conectó, los datos se guardan localmente (no persisten en Railway)

Si aparece 🟡 en Railway, verificar que las variables `SUPABASE_URL` y `SUPABASE_KEY` estén correctas.

---

## Modo local (desarrollo en PC)

Al correr el app localmente con:
```
python -m streamlit run FrontEnd/ventas_app_simple.py
```

Va a mostrar 🟡 porque no tiene las variables de Supabase configuradas.
Eso es normal — los datos se guardan en `DataBase/Generated/` en los archivos CSV/JSON.
