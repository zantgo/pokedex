from django.test import TestCase, Client
from unittest.mock import patch, Mock
from .models import Pokemon
from .services import PokeService

class PokemonModelTest(TestCase):
    def test_pokemon_str(self):
        """Prueba que el método __str__ devuelva el nombre"""
        p = Pokemon.objects.create(
            pokedex_id=1, name="bulbasaur", types="grass, poison", height=7, weight=69
        )
        self.assertEqual(str(p), "bulbasaur")

class PokeServiceTest(TestCase):
    @patch('analysis.services.requests')
    def test_sync_data_creates_pokemon(self, mock_requests):
        """
        Prueba la sincronización simulando (Mocking) la respuesta de la API.
        """
        # 1. Simular respuesta del listado
        mock_list_resp = Mock()
        mock_list_resp.json.return_value = {
            'results': [{'name': 'pikachu', 'url': 'http://fake-url.com/25/'}]
        }
        mock_requests.get.return_value = mock_list_resp

        # 2. Simular respuesta del detalle dentro de la Session
        mock_detail_resp = Mock()
        mock_detail_resp.json.return_value = {
            'id': 25,
            'name': 'pikachu',
            'types': [{'type': {'name': 'electric'}}],
            'height': 4,
            'weight': 60
        }
        
        mock_session = Mock()
        mock_session.get.return_value = mock_detail_resp
        mock_requests.Session.return_value.__enter__.return_value = mock_session

        PokeService.sync_data()

        self.assertTrue(Pokemon.objects.filter(name='pikachu').exists())
        pika = Pokemon.objects.get(name='pikachu')
        self.assertEqual(pika.weight, 60)
        self.assertEqual(pika.types, "electric")

class PokedexViewTest(TestCase):
    def setUp(self):
        # Datos de prueba controlados
        Pokemon.objects.create(pokedex_id=1, name="light", types="normal", height=10, weight=10)   # Límite inferior
        Pokemon.objects.create(pokedex_id=2, name="medium", types="grass", height=10, weight=50)   # Límite superior
        Pokemon.objects.create(pokedex_id=3, name="heavy", types="rock", height=10, weight=100)    # Fuera de rango
        self.client = Client()

    @patch('analysis.services.PokeService.sync_data') 
    def test_view_filter_weight_strict(self, mock_sync):
        """
        Prueba el modo ESTRICTO (> y <).
        Si buscamos entre 10 y 50, NO debería incluir ni a 'light' (10) ni a 'medium' (50).
        """
        mock_sync.return_value = None 
        
        # Enviamos los parámetros tal como los espera la nueva vista
        response = self.client.get('/', {
            'min_weight': 10,
            'max_weight': 50,
            'range_mode': 'strict' # Valor explícito del nuevo radio button
        })
        pokemons = response.context['pokemons']
        
        # En modo estricto: 10 < weight < 50. Ninguno cumple la condición.
        self.assertEqual(len(pokemons), 0)

    @patch('analysis.services.PokeService.sync_data') 
    def test_view_filter_weight_inclusive(self, mock_sync):
        """
        Prueba el modo INCLUSIVO (>= y <=).
        Si buscamos entre 10 y 50, DEBERÍA incluir a 'light' (10) y 'medium' (50).
        """
        mock_sync.return_value = None 
        
        response = self.client.get('/', {
            'min_weight': 10,
            'max_weight': 50,
            'range_mode': 'inclusive' # Valor explícito del nuevo radio button
        })
        pokemons = response.context['pokemons']
        
        # En modo inclusivo: 10 <= weight <= 50. 'light' y 'medium' cumplen.
        self.assertEqual(len(pokemons), 2)
        names = [p.name for p in pokemons]
        self.assertIn('light', names)
        self.assertIn('medium', names)

    @patch('analysis.services.PokeService.sync_data')
    def test_view_default_mode(self, mock_sync):
        """
        Verifica que si no se envía range_mode, el sistema use 'strict' por defecto
        (para proteger compatibilidad o enlaces viejos).
        """
        mock_sync.return_value = None
        
        # Buscamos > 10 y < 50 sin especificar modo
        response = self.client.get('/', {'min_weight': 10, 'max_weight': 50})
        pokemons = response.context['pokemons']
        
        # Debería comportarse como estricto (0 resultados)
        self.assertEqual(len(pokemons), 0)

    @patch('analysis.services.PokeService.sync_data')
    def test_reversed_name_logic(self, mock_sync):
        """Prueba que la transformación de nombre invertido ocurra en la vista"""
        mock_sync.return_value = None
        
        response = self.client.get('/')
        pokemons_list = response.context['pokemons']
        
        p_light = next(p for p in pokemons_list if p.name == "light")
        self.assertEqual(p_light.reversed_name, "thgil")

    @patch('analysis.services.PokeService.sync_data')
    def test_view_resilience_bad_data(self, mock_sync):
        """
        Prueba CRÍTICA: Verifica que la vista NO explote (Error 500) cuando
        llegan valores corruptos como 'None' (string), textos o vacíos.
        Esto valida el arreglo del ValueError.
        """
        mock_sync.return_value = None
        
        # Simulamos la URL que causó el error anteriormente
        params = {
            'min_weight': 'None',      # El culpable del error anterior
            'max_weight': 'grandote',  # Texto basura
            'min_height': '',          # Vacío
            'max_height': 'None',      # Otro 'None'
            'range_mode': 'strict'
        }
        
        try:
            response = self.client.get('/', params)
            # Si llega aquí y el status es 200, el try/except de la vista funcionó
            self.assertEqual(response.status_code, 200)
            
            # Al fallar la conversión, debería ignorar los filtros y devolver todo
            # (o lo que corresponda según tu lógica, pero sin error 500)
            self.assertGreaterEqual(len(response.context['pokemons']), 1)
            
        except ValueError:
            self.fail("La vista lanzó un ValueError con datos sucios. El parche no funciona.")

    @patch('analysis.services.PokeService.sync_data')
    def test_decimal_inputs(self, mock_sync):
        """
        Verifica que los decimales funcionen correctamente ahora que el frontend los permite.
        """
        mock_sync.return_value = None
        
        # Pokemon con peso 10.5 kg (105 hg en DB)
        # Creamos uno específico para esta prueba
        Pokemon.objects.create(pokedex_id=999, name="decimal_mon", types="normal", height=10, weight=105)
        
        response = self.client.get('/', {
            'min_weight': '10.4', # 10.4 kg -> 104 hg
            'max_weight': '10.6', # 10.6 kg -> 106 hg
            'range_mode': 'inclusive'
        })
        
        pokemons = response.context['pokemons']
        nombres = [p.name for p in pokemons]
        
        self.assertIn("decimal_mon", nombres)