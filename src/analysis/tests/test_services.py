from django.test import TestCase, override_settings
from unittest.mock import patch, Mock
from ..models import Pokemon
from ..services import PokeService

class PokeServiceTest(TestCase):
    
    @override_settings(POKEAPI_URL="http://api-de-prueba.com/v2/pokemon")
    @patch('analysis.services.requests')
    def test_sync_uses_env_url(self, mock_requests):
        """
        Prueba que el servicio use la URL definida en settings (simulada aquí),
        y no una hardcodeada.
        """
        mock_list_resp = Mock()
        mock_list_resp.json.return_value = {'results': []} 
        mock_requests.get.return_value = mock_list_resp

        PokeService.sync_data()

        mock_requests.get.assert_called_with(
            "http://api-de-prueba.com/v2/pokemon?limit=50", 
            timeout=10
        )

    @patch('analysis.services.requests')
    def test_sync_data_creates_pokemon(self, mock_requests):
        """
        Prueba la sincronización simulando (Mocking) la respuesta de la API.
        """
        mock_list_resp = Mock()
        mock_list_resp.json.return_value = {
            'results': [{'name': 'pikachu', 'url': 'http://fake-url.com/25/'}]
        }
        mock_requests.get.return_value = mock_list_resp

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