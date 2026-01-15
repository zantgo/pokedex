from django.shortcuts import render
from .models import Pokemon
from .services import PokeService

def pokedex_view(request):
    """
    Controlador principal del Dashboard de Análisis.
    
    Orquesta la sincronización de datos, aplica filtros complejos sobre el QuerySet
    y prepara el contexto para la renderización de la plantilla.

    Query Parameters soportados:
    ---------------------------
    name : str
        Filtro parcial por nombre del Pokémon (insensible a mayúsculas).
    type : str
        Filtro por tipo (ej: 'grass', 'poison').
    min_weight / max_weight : float
        Rango de peso en Kg.
    min_height / max_height : float
        Rango de altura en Cm.
    range_mode : str ('strict' | 'inclusive')
        Define si los rangos numéricos incluyen los límites (>=) o no (>).
    sort : str
        Campo por el cual ordenar ('pokedex_id', 'name', 'weight', etc.).
    transform_func : str
        Función de transformación en tiempo de ejecución (ej: 'invert').

    Context Context:
    ----------------
    pokemons : QuerySet
        Lista paginada/limitada de objetos Pokemon filtrados.
    total_found : int
        Cantidad total de registros que coinciden antes del corte (limit).
    filters : dict
        Estado actual de los filtros para mantener la persistencia en la UI.
    """
    PokeService.sync_data()

    # --- 1. Captura de Filtros ---
    search_name = request.GET.get('name', '').strip()
    search_type = request.GET.get('type', '').strip()
    
    # Inputs crudos
    min_weight_input = request.GET.get('min_weight', '').strip()
    max_weight_input = request.GET.get('max_weight', '').strip()
    min_height_input = request.GET.get('min_height', '').strip()
    max_height_input = request.GET.get('max_height', '').strip()

    # Captura del Límite de Registros
    limit_input = request.GET.get('limit', '50')
    try:
        limit = int(limit_input)
        if limit not in [10, 25, 50]: limit = 50
    except ValueError:
        limit = 50

    # Limpieza de "None"
    if min_weight_input == 'None': min_weight_input = ''
    if max_weight_input == 'None': max_weight_input = ''
    if min_height_input == 'None': min_height_input = ''
    if max_height_input == 'None': max_height_input = ''

    # Configuración
    range_mode = request.GET.get('range_mode', 'strict')
    transform_func = request.GET.get('transform_func', 'invert')
    
    # Ordenamiento
    sort_param = request.GET.get('sort', 'pokedex_id')
    sort_dir = request.GET.get('direction', 'asc')

    db_sort_fields = ['pokedex_id', 'name', 'weight', 'height']
    
    pokemons_qs = Pokemon.objects.all()

    if sort_param in db_sort_fields:
        order_string = sort_param
        if sort_dir == 'desc':
            order_string = f"-{sort_param}"
        pokemons_qs = pokemons_qs.order_by(order_string)

    # --- 2. Aplicación de Filtros ---
    if search_name:
        pokemons_qs = pokemons_qs.filter(name__icontains=search_name)
    
    if search_type and search_type != 'all':
        pokemons_qs = pokemons_qs.filter(types__icontains=search_type)
        
    is_inclusive = (range_mode == 'inclusive')

    # PESO (Input KG -> DB HG) (1 kg = 10 hg)
    if min_weight_input:
        try:
            val_hg = float(min_weight_input) * 10
            if is_inclusive: pokemons_qs = pokemons_qs.filter(weight__gte=val_hg)
            else: pokemons_qs = pokemons_qs.filter(weight__gt=val_hg)
        except ValueError: pass

    if max_weight_input:
        try:
            val_hg = float(max_weight_input) * 10
            if is_inclusive: pokemons_qs = pokemons_qs.filter(weight__lte=val_hg)
            else: pokemons_qs = pokemons_qs.filter(weight__lt=val_hg)
        except ValueError: pass

    # ALTURA (Input CM -> DB DM) 
    # Conversión: 10 cm = 1 dm. Por tanto: cm / 10 = dm
    if min_height_input:
        try:
            val_dm = float(min_height_input) / 10
            if is_inclusive: pokemons_qs = pokemons_qs.filter(height__gte=val_dm)
            else: pokemons_qs = pokemons_qs.filter(height__gt=val_dm)
        except ValueError: pass

    if max_height_input:
        try:
            val_dm = float(max_height_input) / 10
            if is_inclusive: pokemons_qs = pokemons_qs.filter(height__lte=val_dm)
            else: pokemons_qs = pokemons_qs.filter(height__lt=val_dm)
        except ValueError: pass

    # --- 3. Procesamiento y Transformación ---
    pokemons_list = list(pokemons_qs)

    for p in pokemons_list:
        p.type_list = [t.strip() for t in p.types.split(',')]
        p.types_count = len(p.type_list)
        
        # DISPLAY: DB (dm) -> CM (dm * 10)
        p.height_cm = int(p.height * 10) # Usamos int para que se vea "170 cm"
        p.weight_kg = round(p.weight / 10, 2)

        if transform_func == 'invert':
            p.transformed_value = p.name[::-1]
        else:
            p.transformed_value = p.name 

    # --- 4. Ordenamiento Personalizado ---
    reverse_sort = (sort_dir == 'desc')

    if sort_param == 'transformed':
        pokemons_list.sort(key=lambda x: x.transformed_value, reverse=reverse_sort)
    elif sort_param == 'types_count':
        pokemons_list.sort(key=lambda x: x.types_count, reverse=reverse_sort)

    # --- 5. Paginación ---
    total_found = len(pokemons_list)
    pokemons_display = pokemons_list[:limit]

    all_types = [
        "normal", "fighting", "flying", "poison", "ground", "rock", "bug", 
        "ghost", "steel", "fire", "water", "grass", "electric", "psychic", 
        "ice", "dragon", "dark", "fairy"
    ]

    context = {
        'pokemons': pokemons_display,
        'total_found': total_found,
        'current_limit': limit,
        'types_options': all_types,
        'filters': {
            'name': search_name,
            'type': search_type,
            'min_weight': min_weight_input,
            'max_weight': max_weight_input,
            'min_height': min_height_input,
            'max_height': max_height_input,
            'range_mode': range_mode,
            'current_sort': sort_param,
            'current_dir': sort_dir,
            'transform_func': transform_func
        }
    }

    return render(request, 'analysis/index.html', context)