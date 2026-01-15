# 🧪 Pokedex Analytics Infrastructure

Este proyecto contiene la infraestructura técnica backend y frontend diseñada para el Laboratorio del Profesor Oak. Su objetivo es consumir datos de la PokeAPI, persistirlos en una base de datos local y proveer una interfaz de análisis con filtros avanzados y transformación de datos.

## 📋 Especificaciones Técnicas

*   **Backend Framework:** Django 4.2+ (Python 3.12)
*   **Base de Datos:** SQLite (Persistencia local)
*   **Contenerización:** Docker & Docker Compose
*   **API Cliente:** Requests (Consumo sincrónico de PokeAPI)
*   **Arquitectura:** Monolito modularizado (App `analysis`).

## ⚙️ Prerrequisitos

El proyecto es agnóstico al sistema operativo. Funciona en **Linux, Windows y macOS**.

Requisitos únicos:
*   [Docker Engine](https://docs.docker.com/engine/install/)
*   [Docker Compose](https://docs.docker.com/compose/install/)

### 🐧 Nota para usuarios Linux
Para ejecutar los comandos de Docker sin utilizar `sudo` constantemente, asegúrese de que su usuario pertenezca al grupo `docker`.
Si no lo ha configurado, ejecute:
```bash
sudo usermod -aG docker $USER
# Requiere cerrar y volver a iniciar sesión para aplicar los cambios.
```
*(Si decide no hacer esto, deberá anteponer `sudo` a los comandos `docker compose` a continuación).*

---

## 🚀 Instalación y Despliegue

Siga estos pasos estrictamente para levantar el entorno de desarrollo.

### 1. Clonar o entrar al directorio
Navegue hasta la carpeta raíz del proyecto donde se encuentra el archivo `docker-compose.yml`.

```bash
cd pokedex
```

### 2. Configurar Variables de Entorno
El proyecto incluye una plantilla de configuración segura. Genere su archivo de secretos copiando el ejemplo incluido:

**En Linux/macOS:**
```bash
cp .env.example .env
```

**En Windows:**
```powershell
copy .env.example .env
```

*(Opcional: Puede editar el archivo `.env` resultante si necesita cambiar la `SECRET_KEY` o activar el modo `DEBUG`).*

### 3. Construcción del Contenedor
Ejecute el siguiente comando para descargar la imagen de Python e instalar las dependencias.

```bash
docker compose build
```

### 4. Inicialización de Base de Datos
Antes de iniciar el servidor, debe aplicar las migraciones para generar la estructura de la base de datos (SQLite).

```bash
docker compose run --rm web python manage.py migrate
```

### 5. Ejecución del Servidor
Levante los servicios.

```bash
docker compose up
```

Una vez iniciado, el servidor estará disponible en:
👉 **http://localhost:8000**

---

## 🔍 Funcionalidades y Lógica de Negocio

El sistema implementa estrictamente los requerimientos del Profesor Oak:

1.  **Persistencia y Sincronización (API):**
    *   Al acceder a la aplicación, se verifica si la base de datos local tiene registros.
    *   Si hay menos de 50 registros, el sistema consume automáticamente la PokeAPI y guarda los datos en `db.sqlite3`.
    *   Esto minimiza el tráfico de red y permite trabajar offline tras la primera carga.

2.  **Filtros Implementados:**
    *   **Peso (30-80):** Filtra Pokémon con peso estrictamente mayor a 30 y menor a 80.
    *   **Tipo Planta:** Identifica todos los Pokémon que contengan el tipo "grass" (incluso si tienen doble tipo).
    *   **Filtro Combinado:** Identifica Pokémon tipo "flying" que además midan más de 10.

3.  **Transformación de Datos:**
    *   Se genera una columna calculada "Nombre Invertido" (ej: `bulbasaur` -> `ruasablub`) en tiempo de ejecución (Runtime) para no redundar datos en la DB.

---

## 🐧 Solución de Problemas (Linux)

Debido a la naturaleza de Docker en Linux, los archivos creados por el contenedor (como `db.sqlite3` o las migraciones) pueden aparecer como propiedad del usuario `root`.

Si encuentra errores de permisos (`Permission denied`), ejecute el siguiente comando en la raíz del proyecto para recuperar la propiedad de los archivos:

```bash
sudo chown -R $USER:$USER .
```

---

## 📂 Estructura del Proyecto

```text
pokedex/
├── Dockerfile              # Definición de la imagen del sistema (Python 3.12 Slim)
├── docker-compose.yml      # Orquestación de servicios y volúmenes
├── requirements.txt        # Dependencias de Python
├── .env.example            # Plantilla de configuración (Repositorio)
├── .env                    # Variables de entorno (Local/Ignorado)
└── src/                    # Código Fuente Django
    ├── manage.py
    ├── db.sqlite3          # Base de datos (Generada automáticamente)
    ├── pokedex_project/    # Configuración principal
    └── analysis/           # Aplicación de Análisis
        ├── models.py       # Modelo de datos Pokemon
        ├── services.py     # Lógica de consumo de API y Persistencia
        ├── views.py        # Controladores y lógica de filtros
        └── templates/      # Interfaz de usuario HTML/Bootstrap
```

---

## 🛠 Comandos Útiles

**Detener el servidor:**
Presione `Ctrl + C` en la terminal donde corre el servidor.

**Reconstruir desde cero:**
Si modifica el `Dockerfile` o agrega librerías al `requirements.txt`:
```bash
docker compose up --build
```

**Acceder a la terminal del contenedor:**
```bash
docker compose exec web bash
```

