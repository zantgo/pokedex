# 🔄 Flujo de Datos (Data Flow)

Descripción del ciclo de vida de la información dentro del sistema.

## 1. Sincronización (Ingesta)
La sincronización ocurre bajo demanda al iniciar la vista principal (`PokeService.sync_data`).

1.  **Verificación:** El sistema consulta `Pokemon.objects.count()`.
2.  **Condición:** Si el conteo es < 50, se activa la sincronización.
3.  **Fetching (Lista):** `GET /pokemon?limit=50`.
4.  **Fetching (Detalle):** Se itera la lista y se realiza un `GET` por cada URL de detalle (usando `requests.Session` para reutilizar conexiones TCP).
5.  **Persistencia:** Se utiliza `get_or_create` basado en `pokedex_id` para evitar duplicados. Los tipos se aplanan a un string (ej: `['grass', 'poison']` -> `"grass, poison"`).

## 2. Consulta y Filtrado (Lectura)
Cuando el usuario solicita el dashboard:

1.  **Recepción:** La vista captura los *Query Params* (ej: `min_weight=30`, `range_mode=inclusive`).
2.  **Conversión de Unidades:**
    *   El input del usuario (Kg/Cm) se convierte a la unidad de la DB (Hg/Dm) antes de la consulta.
    *   *Ejemplo:* Si busca `> 30kg`, la query filtra `weight > 300`.
3.  **Aplicación de Filtros:** Se encadenan filtros sobre el `QuerySet` (Lazy evaluation).
    *   Si `range_mode == 'strict'`: Operadores `gt`, `lt`.
    *   Si `range_mode == 'inclusive'`: Operadores `gte`, `lte`.
4.  **Limiting:** Se aplica el corte (`[:limit]`) según la selección del usuario (10, 25, 50).

## 3. Transformación y Presentación (Output)
Sobre la lista resultante de objetos en memoria:

1.  **Iteración:** Se recorre la lista de objetos `Pokemon`.
2.  **Decoración:** Se inyectan los atributos calculados (`transformed_value`, `weight_kg`, etc.).
3.  **Renderizado:** Django Templates genera el HTML final inyectando estos valores en la tabla.