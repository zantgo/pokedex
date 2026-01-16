# 🧠 Registro de Decisiones de Arquitectura (ADR)

## 1. Persistencia: SQLite vs PostgreSQL
*   **Decisión:** Uso de **SQLite**.
*   **Contexto:** El requerimiento es una herramienta de análisis local portable.
*   **Justificación:** Elimina la necesidad de configurar un contenedor de base de datos dedicado, reduciendo el consumo de recursos de Docker y simplificando el "Cold Start" de la aplicación. Para < 10,000 registros y un solo usuario concurrente, SQLite es extremadamente performante.

## 2. Modelo de Datos: Tipos como String (CSV) vs Many-to-Many
*   **Decisión:** Almacenar tipos como `CharField` ("grass, poison").
*   **Contexto:** Necesidad de filtrar texto simple y visualización rápida.
*   **Justificación:** Dado que la PokeAPI devuelve una lista pequeña (1 o 2 tipos) y el requerimiento de análisis es de lectura (`icontains`), crear una tabla relacional `Type` + Tabla intermedia agregaría complejidad al ORM y `JOINs` innecesarios para una operación de lectura tan simple.

## 3. Integridad de Datos: Unidades Raw
*   **Decisión:** Guardar Hectogramos y Decímetros (como vienen de la API).
*   **Contexto:** Discrepancia entre unidades de API y unidades de visualización (Kg/Cm).
*   **Justificación:** Se prioriza la fidelidad del dato. Almacenar el dato "crudo" permite que, si en el futuro se requiere cambiar la visualización (ej: a sistema imperial: libras/pies), la base de datos no necesita migración, solo la capa de vista cambia.

## 4. Sincronización Diferida (Defer Loading)
*   **Decisión:** Carga inicial asíncrona vía AJAX.
*   **Contexto:** Necesidad de mejorar la experiencia de usuario (UX) durante la carga inicial de datos (Cold Start), evitando la percepción de una página "congelada".
*   **Justificación:** Se elimina el bloqueo del servidor en el primer renderizado. La vista principal carga instantáneamente y delega la sincronización al cliente mediante un endpoint ligero. Esto ofrece feedback visual inmediato (Loader) sin agregar la complejidad de infraestructura de colas de tareas (Redis/Celery).

## 5. Validación de Inputs
*   **Decisión:** Coerción silenciosa con `try/except` en la vista.
*   **Contexto:** Filtros URL manipulables por el usuario.
*   **Justificación:** En lugar de mostrar errores 500 o 400 al usuario si escribe texto en un campo numérico, el sistema simplemente ignora el filtro corrupto y devuelve resultados generales. Esto mejora la experiencia de usuario (Resilience).

## 6. Estrategia de Tipado (Type Hints)
*   **Decisión:** Tipado selectivo (Core Logic only).
*   **Contexto:** Balance entre seguridad de tipos y agilidad de desarrollo en Python.
*   **Justificación:** Se aplican Type Hints estrictos (`mypy` style) únicamente en capas críticas de negocio (`Models`, `Services`, `Views`) para facilitar el mantenimiento y autocompletado. Se omiten deliberadamente en Pruebas y Archivos de Configuración para mantener la flexibilidad y reducir la verbosidad en código que no es de producción.