import os
import requests
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()


class BaseDscoClient:
    BASE_URL = "https://api.dsco.io"

    def __init__(self):
        api_key = os.getenv("DSCO_API_KEY")
        if not api_key:
            raise RuntimeError("Missing DSCO_API_KEY")

        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _get(self, path: str, params: Optional[Dict] = None) -> Dict:
        url = f"{self.BASE_URL}{path}"

        r = requests.get(
            url,
            headers=self.headers,
            params=params,
            timeout=30
        )
        r.raise_for_status()
        return r.json()
