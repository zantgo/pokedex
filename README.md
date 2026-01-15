# 🧪 Pokedex Analytics Infrastructure

Este repositorio aloja la infraestructura técnica backend y frontend desarrollada para el Laboratorio del Profesor Oak. El sistema funciona como una plataforma de ingestión, persistencia y análisis de datos biológicos de especímenes Pokémon, implementando patrones de arquitectura modular y contenerización para garantizar la portabilidad y escalabilidad del entorno de desarrollo.

---

## 📚 Documentación de Ingeniería

Para facilitar la navegación técnica y la comprensión de las decisiones de diseño, la documentación se ha modularizado. Consulte los siguientes recursos para una visión profunda del sistema:

| Recurso | Descripción |
| :--- | :--- |
| 🏗️ **[Arquitectura del Sistema](./docs/architecture.md)** | Visión general del diseño monolítico, stack tecnológico y diagrama lógico de componentes. |
| 💾 **[Modelo de Datos](./docs/data_model.md)** | Especificación del esquema de base de datos, tipos de datos y atributos calculados en *runtime*. |
| 🔄 **[Flujo de Datos](./docs/data_flow.md)** | Ciclo de vida de la información: desde la ingesta de la API externa hasta la renderización en la UI. |
| 🧠 **[Registro de Decisiones (ADR)](./docs/decisions.md)** | Justificación de decisiones técnicas críticas (SQLite, Sincronización Sincrónica, etc.). |
| 🛠️ **[Guía de Configuración Manual](./docs/setup.md)** | Instrucciones detalladas de despliegue, mantenimiento y comandos administrativos manuales. |

---

## 📋 Especificaciones Técnicas

El proyecto se adhiere a estándares modernos de desarrollo Python/Django:

*   **Backend Framework:** Django 6.0+ (Python 3.12).
*   **Base de Datos:** SQLite (Persistencia local optimizada para entornos de análisis).
*   **Contenerización:** Docker & Docker Compose (V2).
*   **Automatización:** Makefile para estandarización de comandos.
*   **Ingestión de Datos:** Cliente HTTP `requests` con manejo de sesiones y reintentos.
*   **Arquitectura:** Monolito modularizado (App `analysis`) siguiendo el patrón MVT.

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
```

### 2. Ejecución Automatizada (Recomendado)
El proyecto incluye un `Makefile` para estandarizar el ciclo de vida en Linux, macOS y Windows (WSL/Git Bash).

```bash
# Configura entorno, construye imagen, migra BD y levanta el servidor
make start
```

El servicio estará disponible en: 👉 **http://localhost:8000**

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

El sistema implementa lógica de negocio específica para el filtrado y transformación de datos:

1.  **Sincronización Inteligente:**
    *   Al inicio, el sistema verifica la integridad de la base de datos local.
    *   Si existen < 50 registros, se activa el proceso de **Ingesta Sincrónica** desde la PokeAPI para poblar el sistema.

2.  **Motor de Filtros Avanzados:**
    *   **Filtros Dimensionales:** Búsqueda por rangos de Peso (Kg) y Altura (Cm) con conversión automática de unidades (Input Humano → Almacenamiento API).
    *   **Modos de Precisión:** El usuario puede alternar entre búsqueda **Estricta** (`>` / `<`) o **Inclusiva** (`≥` / `≤`).
    *   **Búsqueda Semántica:** Filtrado por tipos parciales (ej: "flying") sobre estructuras de datos desnormalizadas.

3.  **Transformación en Tiempo de Ejecución (Runtime):**
    *   Generación de atributos calculados (ej: "Nombre Invertido") en la capa de vista para evitar redundancia de datos y demostrar manipulación de strings en memoria.

---

## 🧪 Aseguramiento de Calidad (QA)

El proyecto incluye una suite de pruebas automatizadas granularizada que cubre modelos, servicios de integración y vistas.

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

# Pruebas de Vistas (HTTP, Filtros y Lógica de Negocio)
docker compose run --rm web python manage.py test analysis.tests.test_views
```

---

## 📂 Estructura del Proyecto

```text
pokedex/
├── Makefile                # Automatización de comandos (Start, Test, Clean)
├── docs/                   # Hub de documentación técnica
├── Dockerfile              # Definición de imagen (Python 3.12 Slim)
├── docker-compose.yml      # Orquestación de servicios
├── requirements.txt        # Dependencias (Pinned versions)
├── .env.example            # Plantilla de configuración
├── src/
    ├── manage.py           # Entrypoint de Django
    ├── pokedex_project/    # Configuración del proyecto (Settings, URLs)
    └── analysis/           # Aplicación principal
        ├── models.py       # Definición del esquema de datos
        ├── services.py     # Lógica de negocio e integración externa
        ├── views.py        # Controladores y orquestación de filtros
        ├── tests/          # Suite de pruebas unitarias y de integración
        └── templates/      # Capa de presentación (HTML/Bootstrap)
```

---

## 🐧 Solución de Problemas (Entornos Linux)

Debido al manejo de permisos de volúmenes en Docker sobre Linux, los archivos generados (`db.sqlite3`) pueden pertenecer al usuario `root`.

Si encuentra errores de permisos (`Permission denied`), puede corregirlo automáticamente con Make:

```bash
make fix-perms
```

O ejecutar el comando manual:
```bash
sudo chown -R $USER:$USER .
```