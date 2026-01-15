# ===== FILE: ./src/analysis/views.py =====

from django.shortcuts import render
from .models import Pokemon
from .services import PokeService

def pokedex_view(request):
    PokeService.sync_data()

    # --- Filtros ---
    search_name = request.GET.get('name', '').strip()
    search_type = request.GET.get('type', '').strip()
    min_weight = request.GET.get('min_weight')
    max_weight = request.GET.get('max_weight')
    range_mode = request.GET.get('range_mode', 'strict')
    
    # --- LOGICA DE ORDENAMIENTO (CORREGIDA) ---
    sort_param = request.GET.get('sort', 'pokedex_id')
    sort_dir = request.GET.get('direction', 'asc') # Capturamos dirección (asc/desc)

    valid_sort_fields = ['pokedex_id', 'name', 'weight', 'height']
    if sort_param not in valid_sort_fields:
        sort_param = 'pokedex_id'

    # Construimos el string de ordenamiento para Django
    # Si es descendente, se antepone un "-" (ej: "-weight")
    order_string = sort_param
    if sort_dir == 'desc':
        order_string = f"-{sort_param}"
    
    pokemons_qs = Pokemon.objects.all().order_by(order_string)
    # ------------------------------------------

    if search_name:
        pokemons_qs = pokemons_qs.filter(name__icontains=search_name)
    
    if search_type and search_type != 'all':
        pokemons_qs = pokemons_qs.filter(types__icontains=search_type)
        
    is_inclusive = (range_mode == 'inclusive')

    if min_weight:
        if is_inclusive:
            pokemons_qs = pokemons_qs.filter(weight__gte=float(min_weight))
        else:
            pokemons_qs = pokemons_qs.filter(weight__gt=float(min_weight))
        
    if max_weight:
        if is_inclusive:
            pokemons_qs = pokemons_qs.filter(weight__lte=float(max_weight))
        else:
            pokemons_qs = pokemons_qs.filter(weight__lt=float(max_weight))

    pokemons_list = list(pokemons_qs)

    all_types = [
        "normal", "fighting", "flying", "poison", "ground", "rock", "bug", 
        "ghost", "steel", "fire", "water", "grass", "electric", "psychic", 
        "ice", "dragon", "dark", "fairy"
    ]

    for p in pokemons_list:
        p.reversed_name = p.name[::-1]
        p.type_list = [t.strip() for t in p.types.split(',')]

    context = {
        'pokemons': pokemons_list,
        'types_options': all_types,
        'filters': {
            'name': search_name,
            'type': search_type,
            'min_weight': min_weight,
            'max_weight': max_weight,
            'range_mode': range_mode,
            # Pasamos el estado actual al template para pintar las flechas correctas
            'current_sort': sort_param,
            'current_dir': sort_dir
        }
    }

    return render(request, 'analysis/index.html', context)