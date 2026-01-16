# 🛠️ Guía de Configuración y Ejecución

Esta guía detalla los pasos para levantar el entorno de desarrollo. Se prioriza el uso de **Make** para la automatización multiplataforma, pero se documentan los comandos de Docker subyacentes para referencia manual.

## 📋 Prerrequisitos

El proyecto es agnóstico al sistema operativo, pero requiere las siguientes herramientas:

### Generales
*   **Docker Engine** (v20.10+) o **Docker Desktop**.
*   **Docker Compose** (v2.0+).
*   **Git**.

### Específicos por Sistema Operativo
*   **Linux / macOS:** La herramienta `make` suele venir preinstalada.
*   **Windows:** Se recomienda utilizar **WSL2 (Windows Subsystem for Linux)** o la terminal **Git Bash** para ejecutar los comandos de automatización (`make`). Si utiliza PowerShell nativo, deberá optar por la [Configuración Manual](#-configuración-manual-docker-puro).

---

## 🔧 Configuración del Entorno

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/zantgo/pokedex.git
    cd pokedex
    ```

2.  **Configurar Variables de Entorno:**
    El sistema requiere un archivo `.env` en la raíz.

    **En Linux/macOS/Git Bash:**
    ```bash
    cp .env.example .env
    ```

    **En Windows (CMD/PowerShell):**
    ```powershell
    copy .env.example .env
    ```

    > **Nota:** El archivo `.env` incluye configuración predeterminada segura para desarrollo (`DEBUG=True`). Para producción, asegúrese de cambiar `SECRET_KEY`.

---

## ⚡ Automatización con Makefile (Recomendado)

Si dispone de `make`, este es el método más rápido y estandarizado.

### Comandos de Ciclo de Vida

| Comando | Descripción | Qué ejecuta internamente |
| :--- | :--- | :--- |
| `make start` | **Arranque completo.** Configura `.env`, construye imagen, migra BD y levanta servidor. | `build` + `migrate` + `up` |
| `make up` | Levanta el servidor (sin reconstruir ni migrar). | `docker compose up` |
| `make stop` | Pausa los contenedores sin eliminarlos. | `docker compose stop` |
| `make down` | Apaga y elimina contenedores y redes. | `docker compose down` |
| `make clean` | Limpieza profunda (contenedores + archivos `.pyc` + caché). | `down` + `rm` |

### Comandos de Desarrollo

| Comando | Descripción |
| :--- | :--- |
| `make test` | Ejecuta la suite de pruebas completa (`analysis`). |
| `make shell` | Abre una terminal `bash` dentro del contenedor web. |
| `make fix-perms` | (Solo Linux) Arregla permisos de `root` en archivos generados. |

---

## 🔧 Configuración Manual (Docker Puro)

Si se encuentra en Windows sin WSL o prefiere ejecutar los comandos paso a paso, utilice Docker Compose directamente.

### 1. Construcción de Contenedores
Descarga la imagen base e instala dependencias.

```bash
docker compose build
```

### 2. Inicialización de Base de Datos
Esencial antes del primer inicio.

```bash
docker compose run --rm web python manage.py migrate
```

### 3. Ejecución del Servidor
Levanta el servicio en el puerto **8000**.

```bash
docker compose up
```

---

## 🧪 Ejecución de Pruebas (Testing)

### Vía Make (Simplificado)
```bash
make test
```

### Vía Docker Compose (Granular)
Útil para depurar componentes específicos.

*   **Suite Completa:**
    ```bash
    docker compose run --rm web python manage.py test analysis
    ```

*   **Solo Modelos (Base de Datos):**
    ```bash
    docker compose run --rm web python manage.py test analysis.tests.test_models
    ```

*   **Solo Servicios (Integración API):**
    ```bash
    docker compose run --rm web python manage.py test analysis.tests.test_services
    ```

*   **Solo Vistas (Lógica HTTP):**
    ```bash
    docker compose run --rm web python manage.py test analysis.tests.test_views
    ```

---

## 🛠️ Tareas de Mantenimiento

### Acceso a la Terminal del Contenedor
Para inspeccionar archivos internamente.

```bash
docker compose exec web bash
```
*(O `make shell`)*

### Shell de Django
Para interactuar directamente con el ORM.

```bash
docker compose run --rm web python manage.py shell
```

### Reconstrucción del Entorno
Si modifica `requirements.txt` o el `Dockerfile`:

```bash
docker compose up --build
```

---

## 🐧 Solución de Problemas (Linux)

### Error de Permisos en `db.sqlite3`
Docker en Linux monta los volúmenes con el usuario `root`. Si encuentra errores de `Permission denied`:

**Opción A (Make):**
```bash
make fix-perms
```

**Opción B (Manual):**
```bash
sudo chown -R $USER:$USER .
```