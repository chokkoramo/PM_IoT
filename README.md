# PM_IoT

Proyecto minimal de backend Flask + MongoDB (local con docker-compose o MongoDB Atlas). Incluye un formulario de prueba para insertar datos y endpoints JSON para listar/insertar.

## Estructura principal
- `docker-compose.yml` — orquesta `web`, `mongo` y `mongo-express`.
- `src/` — código de la app Flask.
  - `src/app.py` — aplicación Flask con endpoints (`/`, `/dashboard`, `/test-form`, `/api/data`).
  - `src/templates/` — templates Jinja (p. ej. `test_form.html`).
  - `src/requirements.txt` — dependencias Python.
- `.env` — variables de entorno (no commitear con credenciales).
- `README.md` — este archivo.

## Requisitos
- Python 3.8+ (o Docker).
- Si usas Atlas con `mongodb+srv://` necesitas `dnspython`.
- Docker & docker-compose (opcional para ejecutar en contenedores).

## Variables de entorno
Crear un `.env` en la raíz con las variables necesarias. Ejemplo (no incluir credenciales reales en el repositorio), el entorno fue creado en macOs:

````env
ENV=development
FLASK_APP=app.py
FLASK_ENV=development

# Para usar Atlas preferible: MONGO_URL
# MONGO_URL=mongodb+srv://<USER>:<PASSWORD>@<CLUSTER>.mongodb.net/<DB>?retryWrites=true&w=majority

# Alternativa local (docker-compose crea mongo)
MONGO_HOST=mongo
MONGO_PORT=27017
MONGO_DB=pm_proyect
MONGO_USER=admin
MONGO_PASSWORD=changeme