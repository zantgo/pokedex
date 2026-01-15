from django.contrib import admin
from .models import Pokemon

@admin.register(Pokemon)
class PokemonAdmin(admin.ModelAdmin):
    # Muestra las columnas clave en la lista
    list_display = ('pokedex_id', 'name', 'types', 'height', 'weight')
    
    # Permite buscar por nombre y tipo desde el panel
    search_fields = ('name', 'types')
    
    # Permite filtrar por tipo rápidamente
    list_filter = ('types',)
    
    # Orden por defecto
    ordering = ('pokedex_id',)