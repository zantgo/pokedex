from django.test import TestCase
from ..models import Pokemon

class PokemonModelTest(TestCase):
    def test_pokemon_str(self):
        """Prueba que el método __str__ devuelva el nombre"""
        p = Pokemon.objects.create(
            pokedex_id=1, name="bulbasaur", types="grass, poison", height=7, weight=69
        )
        self.assertEqual(str(p), "bulbasaur")