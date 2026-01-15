# src/analysis/services.py
import requests
import logging
from django.conf import settings
from .models import Pokemon

logger = logging.getLogger(__name__)

class PokeService:
    """
    Fachada para la comunicación con la API externa (PokeAPI) y 
    la persistencia de datos en el sistema local.
    """
    
    @staticmethod
    def sync_data() -> None:
        """
        Verifica el estado de la base de datos local y realiza una carga inicial
        de datos si existen menos de 50 registros.
        
        Logica de Negocio:
            1. Verifica conteo en DB (Cheap query).
            2. Si faltan datos, consume endpoint 'list' de PokeAPI.
            3. Itera y consume endpoint 'detail' por cada item.
            4. Persiste usando 'get_or_create' para evitar duplicados.
        
        Raises:
            Maneja internamente requests.RequestException para asegurar 
            que la vista no colapse ante fallos de red.
        """

        if Pokemon.objects.count() >= 50:
            return

        # Leemos la URL dinámicamente desde settings (.env)
        api_url: str = settings.POKEAPI_URL

        print(f"--- 📡 Iniciando Sincronización con {api_url} ---")
        
        try:
            # Usamos la variable api_url en lugar de la constante fija
            response = requests.get(f"{api_url}?limit=50", timeout=10)
            response.raise_for_status()
            results = response.json().get('results', [])

            # Usar Session mejora rendimiento en múltiples peticiones al mismo host
            with requests.Session() as session:
                for item in results:
                    try:
                        detail_resp = session.get(item['url'], timeout=5)
                        detail_resp.raise_for_status()
                        detail = detail_resp.json()

                        # Procesar tipos
                        types_list = [t['type']['name'] for t in detail['types']]
                        types_str = ", ".join(types_list)

                        Pokemon.objects.get_or_create(
                            pokedex_id=detail['id'],
                            defaults={
                                'name': detail['name'],
                                'types': types_str,
                                'height': detail['height'],
                                'weight': detail['weight']
                            }
                        )
                    except requests.RequestException as e:
                        logger.error(f"Error obteniendo detalles de {item['name']}: {e}")
                        continue # Saltamos al siguiente si uno falla

        except requests.RequestException as e:
            logger.error(f"Error fatal conectando con PokeAPI: {e}")
