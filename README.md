# PM_IoT — Informe del proyecto

## Resumen ejecutivo
PM_IoT es una solución mínima para la adquisición, transporte y almacenamiento de datos de sensores de material particulado (PM) en el aire. La aplicación recoge lecturas desde sensores instalados en campo, las envía a un backend Flask y las almacena en MongoDB (Atlas o local). El servicio está desplegado en Render para acceso público y pruebas remotas.

## Objetivos
- Medir y almacenar concentraciones de PM (p. ej. PM1, PM2.5, PM10).
- Proveer endpoints HTTP para insertar y consultar datos.
- Facilitar pruebas mediante un formulario web y comandos desde consola.
- Desplegar de forma fiable en la nube (Render) y soportar ejecución local con Docker.

## Hardware (sensores)
El sistema está pensado para integrarse con sensores de material particulado comunes (ej.: PMS5003, SDS011 u otros que entreguen concentraciones en µg/m3). Cada unidad de sensor debe enviar JSON con al menos:
- sensor: identificador del sensor
- value: valor numérico (concentración)
- ts: timestamp (opcional)
- meta: información opcional (ubicación, dispositivo, etc.)

## Arquitectura y componentes
- Sensores → HTTP (POST) → Backend Flask
- Backend Flask:
  - Endpoints REST para insertar/listar datos
  - Renders de plantillas para pruebas (formulario)
- Base de datos: MongoDB (Atlas recomendado) para almacenamiento flexible de documentos
- Orquestación local: Docker / docker-compose
- Despliegue: Render (servicio web que ejecuta la app)

Diagrama simplificado:
Sensor (HTTP) --> Flask (API) --> MongoDB (Atlas)

## Stack tecnológico
- Lenguaje: Python 3.8+
- Framework web: Flask
- Base de datos: MongoDB (Atlas o contenedor local)
- Librerías clave: pymongo, dnspython (si usa mongodb+srv)
- Contenerización: Docker + docker-compose (opcional)
- Hosting: Render

## Flujo de datos
1. El sensor envía una petición POST con JSON a `/api/data` o al endpoint de prueba `/test-form` (POST).
2. Flask valida el JSON y enriquece con timestamp si hace falta.
3. El documento se inserta en la colección `data` de la base de datos configurada.
4. Consultas a `/api/data` (GET) devuelven los registros ordenados por fecha.

## Esquema de documento (ejemplo)
{
  "sensor": "temp1",
  "value": 23.5,
  "meta": {"ubicacion":"azotea"},
  "ts": "2025-10-30T12:00:00Z"
}

## Variables de entorno importantes
- MONGO_URL — URI completo de Atlas (recomendado, p. ej. mongodb+srv://USER:PASS@cluster.mongodb.net/DB?retryWrites=true&w=majority)
- MONGO_DB — nombre de la base de datos (ej. pm_proyect)
- FLASK_APP, FLASK_ENV, ENV — configuración de Flask / entorno
Nota: no subir `.env` con credenciales al repositorio. Usar `.env.example` como plantilla.

## Ejecutar local (sin Docker)
1. Crear y activar venv:
   ```
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r src/requirements.txt
   ```
2. Exportar conexión a Atlas (si aplica):
   ```
   export MONGO_URL='mongodb+srv://USER:PASS@cluster.mongodb.net/pm_proyect?retryWrites=true&w=majority'
   ```
3. Ejecutar:
   ```
   cd src
   python3 app.py
   ```
4. Acceder a: `http://localhost:7001/test-form` para pruebas manuales.

## Ejecutar con Docker (local)
1. Desde la raíz del proyecto:
   ```
   docker-compose up --build -d
   docker-compose logs -f web
   ```
2. El servicio web estará en `http://localhost:7001`.

## Envío de datos (consola)
- Usando curl al endpoint:
  ```
  curl -X POST http://localhost:7001/api/data \
    -H "Content-Type: application/json" \
    -d '{"sensor":"temp1","value":23.5,"meta":{"ubicacion":"azotea"}}'
  ```
- Insertar directo en Atlas con mongosh:
  ```
  mongosh "mongodb+srv://USER:PASS@cluster.mongodb.net/pm_proyect" --eval 'db.getSiblingDB("pm_proyect").data.insertOne({sensor:"temp1", value:23.5, ts:new Date()})'
  ```

## Despliegue en Render
- Crear un nuevo servicio tipo "Web Service" en Render apuntando al repo.
- Configurar la rama a desplegar y el comando de start (por defecto se usa el `app.py` con Flask).
- Añadir las variables de entorno en el panel de Render (MONGO_URL, MONGO_DB, FLASK_ENV).
- Asegurarse de que el servicio tenga acceso a MongoDB Atlas (Atlas permite conexiones desde la IP de Render o usar 0.0.0.0/0 temporalmente).

## Comprobaciones y errores comunes
- "command insert not found": indica conexión a un endpoint no compatible con MongoDB. Asegurar que `MONGO_URL` es el connection string de MongoDB Atlas (mongodb+srv o mongodb://) y no URL de otro servicio.
- `ServerSelectionTimeoutError`: revisar credenciales, reglas de Network Access en Atlas y que dnspython esté instalado si usa `mongodb+srv`.
- Asegurar que la contraseña en la URI esté correctamente URL-encoded si contiene caracteres especiales.

## Seguridad y buenas prácticas
- No versionar `.env` con credenciales. Mantener `.env.example`.
- Usar usuarios de base de datos con permisos mínimos.
- Para producción usar un servidor WSGI (Gunicorn) y configurar logs/monitoring.

## Próximos pasos sugeridos
- Añadir autenticación básica para la API.
- Normalizar y validar datos de sensores (esquema, unidades).
- Implementar agregaciones y visualizaciones (promedios por periodo, alarmas).
- Registrar metadatos del dispositivo (ubicación GPS, calibración).

---

Este documento describe qué se hará, con qué componentes y cómo ejecutar y probar el sistema. Para cambios rápidos (crear `.env.example`, actualizar `src/app.py` para aceptar POST en `/test-form`) indicar y se aplican en el repositorio.