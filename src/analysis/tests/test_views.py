from django.test import TestCase, Client
from unittest.mock import patch
from ..models import Pokemon

class PokedexViewTest(TestCase):
    def setUp(self):

        # La DB guarda Hectogramos (HG). La vista recibe Kilogramos (KG).
        # Factor de conversión: 1 KG = 10 HG.
        # Queremos probar filtros entre 10kg y 50kg.
        
        # 'light': 10kg -> En DB debe ser 100
        Pokemon.objects.create(pokedex_id=1, name="light", types="normal", height=10, weight=100)
        
        # 'medium': 50kg -> En DB debe ser 500
        Pokemon.objects.create(pokedex_id=2, name="medium", types="grass", height=10, weight=500)
        
        # 'heavy': 100kg -> En DB debe ser 1000 (Fuera de rango superior)
        Pokemon.objects.create(pokedex_id=3, name="heavy", types="rock", height=10, weight=1000)
                
        self.client = Client()

    @patch('analysis.services.PokeService.sync_data') 
    def test_view_filter_weight_strict(self, mock_sync):
        """
        Prueba ESTRICTA (> 10kg y < 50kg).
        DB busca: weight > 100 AND weight < 500.
        'light' (100) se excluye. 'medium' (500) se excluye.
        Resultado esperado: 0.
        """
        mock_sync.return_value = None 
        
        response = self.client.get('/', {
            'min_weight': 10,
            'max_weight': 50,
            'range_mode': 'strict'
        })
        pokemons = response.context['pokemons']
        
        self.assertEqual(len(pokemons), 0)

    @patch('analysis.services.PokeService.sync_data') 
    def test_view_filter_weight_inclusive(self, mock_sync):
        """
        Prueba INCLUSIVA (>= 10kg y <= 50kg).
        DB busca: weight >= 100 AND weight <= 500.
        'light' (100) entra. 'medium' (500) entra.
        Resultado esperado: 2.
        """
        mock_sync.return_value = None 
        
        response = self.client.get('/', {
            'min_weight': 10,
            'max_weight': 50,
            'range_mode': 'inclusive'
        })
        pokemons = response.context['pokemons']
        
        self.assertEqual(len(pokemons), 2)
        names = [p.name for p in pokemons]
        self.assertIn('light', names)
        self.assertIn('medium', names)

    @patch('analysis.services.PokeService.sync_data')
    def test_view_default_mode(self, mock_sync):
        """Si no se especifica modo, debe ser estricto por defecto."""
        mock_sync.return_value = None
        
        # Buscamos > 10 y < 50
        response = self.client.get('/', {'min_weight': 10, 'max_weight': 50})
        pokemons = response.context['pokemons']
        
        # 0 resultados (igual que el test estricto)
        self.assertEqual(len(pokemons), 0)

    @patch('analysis.services.PokeService.sync_data')
    def test_reversed_name_logic(self, mock_sync):
        mock_sync.return_value = None
        
        response = self.client.get('/')
        pokemons_list = response.context['pokemons']
        
        p_light = next(p for p in pokemons_list if p.name == "light")
        self.assertEqual(p_light.transformed_value, "thgil")

    @patch('analysis.services.PokeService.sync_data')
    def test_view_resilience_bad_data(self, mock_sync):
        mock_sync.return_value = None
        
        params = {
            'min_weight': 'None',
            'max_weight': 'grandote',
            'range_mode': 'strict'
        }
        
        try:
            response = self.client.get('/', params)
            self.assertEqual(response.status_code, 200)
            # Debería devolver todos (3) ya que ignoró los filtros corruptos
            self.assertGreaterEqual(len(response.context['pokemons']), 1)
        except ValueError:
            self.fail("La vista lanzó un ValueError con datos sucios.")

    @patch('analysis.services.PokeService.sync_data')
    def test_decimal_inputs(self, mock_sync):
        """
        Verifica decimales. Creamos el pokemon específico aquí 
        para no ensuciar los otros tests.
        """
        mock_sync.return_value = None
        
        # Pokemon con peso 10.5 kg (105 hg en DB)
        Pokemon.objects.create(
            pokedex_id=999, 
            name="decimal_mon", 
            types="normal", 
            height=10, 
            weight=105
        )
        
        response = self.client.get('/', {
            'min_weight': '10.4', # 10.4 kg -> 104 hg
            'max_weight': '10.6', # 10.6 kg -> 106 hg
            'range_mode': 'inclusive'
        })
        
        pokemons = response.context['pokemons']
        nombres = [p.name for p in pokemons]
        
        self.assertIn("decimal_mon", nombres)