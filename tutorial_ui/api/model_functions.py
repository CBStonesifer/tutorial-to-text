import requests
import logging
from .settings import settings

logger = logging.getLogger(__name__)

class BasetenClient:
    _session = None

    def __init__(self):
        self.api_key = settings.baseten_api_key
        self.base_url = "https://model-4w5ne9jw.api.baseten.co/development/predict"
        if BasetenClient._session is None:
            BasetenClient._session = requests.Session()

    def predict(self, data: dict) -> dict:
        headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json"
        }

        logger.info(f"Sending request to Baseten: {self.base_url}")
        logger.info(f"Request payload: {data}")

        response = self._session.post(
            self.base_url,
            json=data,
            headers=headers,
            timeout=120.0
        )

        logger.info(f"Baseten response status: {response.status_code}")
        response.raise_for_status()

        result = response.json()
        logger.info(f"Baseten response body: {result}")

        return result
