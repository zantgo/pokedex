# 🏗️ Arquitectura del Sistema

Este documento describe la arquitectura técnica de la plataforma de análisis Pokedex. El sistema sigue un diseño monolítico modularizado basado en el patrón **MVT (Model-View-Template)** de Django.

## Diagrama Lógico de Componentes

El flujo de la aplicación se divide en cuatro capas principales:

1.  **Capa de Infraestructura (Docker):**
    *   Orquestación de contenedores para asegurar consistencia entre entornos (Dev/Prod).
    *   Volúmenes persistentes para la base de datos SQLite.

2.  **Capa de Datos (External & Persistence):**
    *   **Fuente de Verdad:** PokeAPI (REST).
    *   **Persistencia Local:** SQLite (`db.sqlite3`).
    *   **Adaptador:** `PokeService` (Patrón Facade para consumo y sincronización).

3.  **Capa de Negocio (Django App `analysis`):**
    *   **Models:** Definición de estructuras de datos.
    *   **Views:** Lógica de orquestación, filtrado avanzado (rangos estrictos/inclusivos) y paginación.
    *   **Services:** Lógica de sincronización y reglas de negocio encapsuladas.

4.  **Capa de Presentación (Templates):**
    *   Renderizado HTML5 + CSS3 (Bootstrap).
    *   Lógica de presentación (formateo de unidades, badges de tipos).

## Stack Tecnológico

*   **Runtime:** Python 3.12 (Imagen `slim`).
*   **Framework Web:** Django 6.0.1.
*   **Base de Datos:** SQLite 3 (Integrada en Python).
*   **Cliente HTTP:** `requests` (con manejo de sesiones y timeouts).
*   **Gestión de Configuración:** `python-decouple` (Variables de entorno).