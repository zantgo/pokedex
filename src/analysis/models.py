from django.db import models

class Pokemon(models.Model):
    """
    Representa un espécimen Pokémon almacenado para análisis local.
    
    Attributes:
        pokedex_id (int): Identificador único oficial en la Pokedex Nacional.
        name (str): Nombre del Pokémon en minúsculas (ej: 'bulbasaur').
        types (str): Cadena de texto con los tipos separados por coma (ej: 'grass, poison').
        height (float): Altura en decímetros.
        weight (float): Peso en hectogramos.
    """
    pokedex_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    types = models.CharField(max_length=200)
    height = models.FloatField()
    weight = models.FloatField()

    def __str__(self) -> str:
        return str(self.name)
