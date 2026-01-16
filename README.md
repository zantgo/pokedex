# 🧪 Pokedex Analytics Infrastructure

Este repositorio aloja la infraestructura técnica **backend** y **frontend** desarrollada para el Laboratorio del Profesor Oak. El sistema funciona como una plataforma de ingestión, persistencia y análisis de datos biológicos de especímenes Pokémon, implementando patrones de arquitectura modular y contenerización para garantizar la portabilidad y escalabilidad del entorno de desarrollo.

---

## 📚 Documentación

Para facilitar la navegación técnica y la comprensión de las decisiones de diseño, la documentación se ha modularizado. Consulte los siguientes recursos para una visión profunda del sistema:

- 🏗️ **[Arquitectura del Sistema](./docs/architecture.md)**
- 💾 **[Modelo de Datos](./docs/data_model.md)**
- 🔄 **[Flujo de Datos](./docs/data_flow.md)**
- 🧠 **[Registro de Decisiones (ADR)](./docs/decisions.md)**
- 🛠️ **[Guía de Configuración Manual](./docs/setup.md)**

---

## 📋 Especificaciones Técnicas

El proyecto se adhiere a estándares modernos de desarrollo en Python/Django:

- **Backend Framework:** Django 6.0+ (Python 3.12)
- **Base de Datos:** SQLite
- **Contenerización:** Docker & Docker Compose (v2)
- **Automatización:** Makefile para estandarización de comandos
- **Ingestión de Datos:** Cliente HTTP `requests` con manejo de sesiones y reintentos
- **Arquitectura:** Monolito modularizado (app `analysis`) siguiendo el patrón MVT

---

## 🚀 Despliegue Rápido (Quick Start)

El entorno está totalmente contenerizado y automatizado. Siga estos pasos para iniciar la aplicación.

### 1. Configuración Inicial

Clone el repositorio y configure las variables de entorno.

```bash
# Copiar la plantilla de configuración
cp .env.example .env

# Nota: .env viene preconfigurado para desarrollo (DEBUG=True).
# Para producción, es mandatorio rotar la SECRET_KEY.
````

### 2. Ejecución Automatizada (Recomendado)

El proyecto incluye un `Makefile` para estandarizar el ciclo de vida en Linux, macOS y Windows (WSL/Git Bash).

```bash
# Configura el entorno, construye la imagen, migra la BD y levanta el servidor
make start
```

El servicio estará disponible en: 👉 **[http://localhost:8000](http://localhost:8000)**

### 3. Ejecución Manual (Alternativa)

Si no dispone de `make`, puede utilizar los comandos de Docker Compose directamente:

```bash
# 1. Construir la imagen del sistema
docker compose build

# 2. Inicializar el esquema de base de datos
docker compose run --rm web python manage.py migrate

# 3. Levantar el servidor
docker compose up
```

---

## 🔍 Funcionalidades y Reglas de Negocio

El sistema implementa lógica de negocio específica para el filtrado y la transformación de datos:

1. **Sincronización Inteligente**
    
    - Al inicio, el sistema verifica la integridad de la base de datos local.
        
    - Si existen menos de 50 registros, se dispara un proceso de **Carga Diferida (Deferred Loading)**.  
        El sistema activa la sincronización vía AJAX en segundo plano para poblar la base de datos sin bloquear el renderizado inicial de la interfaz.
        
2. **Motor de Filtros Avanzados**
    
    - **Filtros Dimensionales:** Búsqueda por rangos de peso (kg) y altura (cm) con conversión automática de unidades  
        (input humano → almacenamiento API).
        
    - **Modos de Precisión:** El usuario puede alternar entre búsqueda **Estricta** (`>` / `<`) o **Inclusiva** (`≥` / `≤`).
        
    - **Búsqueda Semántica:** Filtrado por tipos parciales (ej.: `flying`) sobre estructuras de datos desnormalizadas.
        
3. **Transformación en Tiempo de Ejecución (Runtime)**
    
    - Generación de atributos calculados (ej.: _Nombre Invertido_) en la capa de vista para evitar redundancia de datos y demostrar manipulación de strings en memoria.
        

---

## 🧪 Aseguramiento de Calidad (QA)

El proyecto incluye una suite de pruebas automatizadas y granularizadas que cubren modelos, servicios de integración y vistas.

### Ejecución Simplificada

```bash
make test
```

### Ejecución Granular (Manual)

Para depurar componentes específicos durante el desarrollo:

```bash
# Pruebas de Modelos (Persistencia)
docker compose run --rm web python manage.py test analysis.tests.test_models

# Pruebas de Servicios (Integración API y Mocks)
docker compose run --rm web python manage.py test analysis.tests.test_services

# Pruebas de Vistas (HTTP, filtros y lógica de negocio)
docker compose run --rm web python manage.py test analysis.tests.test_views
```

---

## 🐧 Solución de Problemas (Entornos Linux)

Debido al manejo de permisos de volúmenes en Docker sobre Linux, los archivos generados (por ejemplo, `db.sqlite3`) pueden pertenecer al usuario `root`.

Si encuentra errores de permisos (`Permission denied`), puede corregirlos automáticamente con Make:

```bash
make fix-perms
```

O ejecutar el comando manualmente:

```bash
sudo chown -R $USER:$USER .
```

---

## 📂 Estructura del Proyecto

```text
pokedex/
├── docs/                           # Documentación técnica modular
│   ├── architecture.md             # Diagramas y stack tecnológico
│   ├── data_flow.md                # Flujo de sincronización y lectura
│   ├── data_model.md               # Esquema de DB y campos calculados
│   ├── decisions.md                # Registro de decisiones (ADR)
│   └── setup.md                    # Guía de instalación manual / Make
├── src/                            # Código fuente del proyecto
│   ├── analysis/                   # App principal (lógica de negocio)
│   │   ├── migrations/             # Historial de cambios en DB
│   │   │   ├── 0001_initial.py
│   │   │   └── __init__.py
│   │   ├── static/analysis/        # Archivos estáticos
│   │   │   └── style.css           # Estilos personalizados (dark mode)
│   │   ├── templates/analysis/     # Plantillas HTML
│   │   │   ├── components/         # Fragmentos reutilizables
│   │   │   │   ├── filters.html    # Formulario de filtros
│   │   │   │   ├── loader.html     # Lógica AJAX y spinner
│   │   │   │   └── table.html      # Tabla de resultados
│   │   │   ├── base.html           # Layout base
│   │   │   └── index.html          # Vista principal
│   │   ├── tests/                  # Suite de pruebas automatizadas
│   │   │   ├── __init__.py
│   │   │   ├── test_models.py      # Tests unitarios de modelos
│   │   │   ├── test_services.py    # Tests de integración (mocks)
│   │   │   └── test_views.py       # Tests de lógica de vistas
│   │   ├── __init__.py
│   │   ├── admin.py                # Configuración del panel de admin
│   │   ├── apps.py                 # Configuración de la app Django
│   │   ├── models.py               # Definición del modelo Pokémon
│   │   ├── services.py             # Lógica de consumo de PokeAPI
│   │   └── views.py                # Controladores y orquestación
│   ├── pokedex_project/            # Configuración global de Django
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py             # Variables globales y configuración
│   │   ├── urls.py                 # Enrutamiento principal
│   │   └── wsgi.py
│   ├── db.sqlite3                  # Base de datos local (generada)
│   └── manage.py                   # Entrypoint de comandos Django
├── .env                            # Variables de entorno (no versionado)
├── .env.example                    # Plantilla de configuración segura
├── .gitignore                      # Exclusiones de Git
├── docker-compose.yml              # Orquestación de servicios
├── Dockerfile                      # Definición de imagen del contenedor
├── Makefile                        # Automatización (start, test, clean)
├── README.md                       # Documentación principal
└── requirements.txt                # Dependencias (Django, requests, etc.)
```
