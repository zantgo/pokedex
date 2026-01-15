# 💾 Modelo de Datos

Este documento detalla el esquema de persistencia y las estructuras de datos efímeras utilizadas en la aplicación.

## Entidad Principal: `Pokemon`

La aplicación utiliza una única tabla desnormalizada para optimizar la lectura y el filtrado simple.

| Campo | Tipo Django | Descripción | Nota Técnica |
| :--- | :--- | :--- | :--- |
| `id` | `BigAutoField` | PK interna de Django | Autoincremental. |
| `pokedex_id` | `IntegerField` | ID oficial (National Pokedex) | **Unique**. Usado para ordenamiento canónico. |
| `name` | `CharField` | Nombre de la especie | Almacenado en minúsculas (lowercase). |
| `types` | `CharField` | Lista de tipos | Almacenado como CSV (ej: "grass, poison") para simplificar búsquedas `icontains`. |
| `height` | `FloatField` | Altura física | Unidad: **Decímetros (dm)** (Estándar PokeAPI). |
| `weight` | `FloatField` | Peso físico | Unidad: **Hectogramos (hg)** (Estándar PokeAPI). |

## Campos Calculados (Runtime)

Estos atributos **no** se persisten en la base de datos; se calculan en la vista (`views.py`) o en el template para la presentación al usuario.

1.  **`height_cm` (Centímetros):**
    *   Cálculo: `db_height * 10`
    *   Uso: Visualización amigable al usuario.

2.  **`weight_kg` (Kilogramos):**
    *   Cálculo: `db_weight / 10`
    *   Uso: Visualización y filtros de entrada de usuario.

3.  **`transformed_value` (Nombre Invertido):**
    *   Lógica: Inversión de cadena (`string[::-1]`).
    *   Uso: Requerimiento específico de análisis de datos.

4.  **`types_count`:**
    *   Lógica: Conteo de elementos tras hacer split al string de tipos.
    *   Uso: Ordenamiento dinámico en la tabla.