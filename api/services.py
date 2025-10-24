import requests
from django.core.cache import cache
from datetime import datetime
from .models import Film
import logging

logger = logging.getLogger(__name__)


class SwapiService:
    """
    Service for interacting with the Star Wars API (SWAPI).
    """
    BASE_URL = "https://swapi.dev/api"
    CACHE_TIMEOUT = 60 * 60 * 24  # 24 hours

    def get_films(self):
        """
        Fetch all films from SWAPI with caching.
        """
        cache_key = 'swapi_films'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            logger.info("Returning cached SWAPI films data")
            return cached_data
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/films/",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            cache.set(cache_key, data, self.CACHE_TIMEOUT)
            logger.info("Fetched and cached films from SWAPI")
            return data
        
        except requests.RequestException as e:
            logger.error(f"Error fetching films from SWAPI: {str(e)}")
            raise Exception("Failed to fetch films from SWAPI")

    def sync_films(self):
        """
        Sync films from SWAPI to local database.
        """
        try:
            films_data = self.get_films()
            
            for film_data in films_data.get('results', []):
                # Extract ID from URL
                swapi_id = int(film_data['url'].strip('/').split('/')[-1])
                
                # Parse release date
                release_date = datetime.strptime(
                    film_data['release_date'],
                    '%Y-%m-%d'
                ).date()
                
                # Update or create film
                film, created = Film.objects.update_or_create(
                    swapi_id=swapi_id,
                    defaults={
                        'title': film_data['title'],
                        'episode_id': film_data['episode_id'],
                        'opening_crawl': film_data['opening_crawl'],
                        'director': film_data['director'],
                        'producer': film_data['producer'],
                        'release_date': release_date,
                    }
                )
                
                action = "Created" if created else "Updated"
                logger.info(f"{action} film: {film.title}")
            
            logger.info("Films sync completed successfully")
            return True
        
        except Exception as e:
            logger.error(f"Error syncing films: {str(e)}")
            raise

    def get_film_by_id(self, swapi_id):
        """
        Get a specific film from SWAPI by ID.
        """
        cache_key = f'swapi_film_{swapi_id}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/films/{swapi_id}/",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            cache.set(cache_key, data, self.CACHE_TIMEOUT)
            return data
        
        except requests.RequestException as e:
            logger.error(f"Error fetching film {swapi_id} from SWAPI: {str(e)}")
            raise Exception(f"Failed to fetch film {swapi_id} from SWAPI")