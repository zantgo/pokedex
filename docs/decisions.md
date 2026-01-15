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

## 4. Sincronización Sincrónica
*   **Decisión:** Llamada bloqueante en la vista principal.
*   **Contexto:** Requerimiento de "minimizar tráfico" y persistencia local.
*   **Justificación (Trade-off):** Aunque idealmente esto iría en una tarea asíncrona (Celery), para el alcance de esta prueba técnica añade una sobrecarga de infraestructura (Redis + Worker) injustificada. La carga inicial demora unos segundos una única vez, lo cual es aceptable para un MVP.

## 5. Validación de Inputs
*   **Decisión:** Coerción silenciosa con `try/except` en la vista.
*   **Contexto:** Filtros URL manipulables por el usuario.
*   **Justificación:** En lugar de mostrar errores 500 o 400 al usuario si escribe texto en un campo numérico, el sistema simplemente ignora el filtro corrupto y devuelve resultados generales. Esto mejora la experiencia de usuario (Resilience).