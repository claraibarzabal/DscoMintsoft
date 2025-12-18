import os
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class MintsoftProductClient:
    """
    Cliente Mintsoft – Products API
    """

    BASE_URL = "https://api.mintsoft.co.uk/api"

    def __init__(self):
        self.username = os.getenv("MINTSOFT_USERNAME")
        self.password = os.getenv("MINTSOFT_PASSWORD")
        self.client_id = os.getenv("MINTSOFT_CLIENT_ID")

        if not all([self.username, self.password, self.client_id]):
            raise RuntimeError("Missing Mintsoft credentials")

        self.api_key = self._authenticate()

    # -------------------------------------------------
    # Auth
    # -------------------------------------------------
    def _authenticate(self) -> str:
        url = f"{self.BASE_URL}/Auth"

        payload = {
            "Username": self.username,
            "Password": self.password,
        }

        r = requests.post(url, json=payload, timeout=30)
        r.raise_for_status()

        return r.json()

    # -------------------------------------------------
    # Headers
    # -------------------------------------------------
    def _headers(self) -> dict:
        return {
            "ms-apikey": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    # -------------------------------------------------
    # Create product
    # -------------------------------------------------
    def create_product(self, payload: Dict) -> Dict:
        url = f"{self.BASE_URL}/Product"

        r = requests.put(
            url,
            headers=self._headers(),
            json=payload,
            timeout=30
        )

        r.raise_for_status()
        return r.json() if r.text else {}

    # -------------------------------------------------
    # Update product
    # -------------------------------------------------
    def update_product(self, product_id: int, payload: Dict) -> Dict:
        body = dict(payload)
        body["ID"] = product_id

        url = f"{self.BASE_URL}/Product"

        r = requests.post(
            url,
            headers=self._headers(),
            json=body,
            timeout=30
        )

        r.raise_for_status()
        return r.json() if r.text else {}

    # -------------------------------------------------
    # Get all products (auto pagination)
    # -------------------------------------------------
    def get_all_products(
        self,
        page_size: int = 100,
        max_pages: int = 200
    ) -> List[Dict]:

        products: List[Dict] = []
        page = 1

        while page <= max_pages:
            batch = self._get_products_page(page, page_size)

            if not batch:
                break

            products.extend(batch)
            page += 1

        return products

    # -------------------------------------------------
    # Get products page
    # -------------------------------------------------
    def _get_products_page(
        self,
        page: int,
        limit: int
    ) -> List[Dict]:

        url = f"{self.BASE_URL}/Product/List"

        params = {
            "PageNo": page,
            "Limit": limit,
            "ClientId": self.client_id,
        }

        r = requests.get(
            url,
            headers=self._headers(),
            params=params,
            timeout=30
        )

        r.raise_for_status()
        return r.json()

    # -------------------------------------------------
    # Get product by SKU
    # -------------------------------------------------
    def get_product_by_sku(self, sku: str) -> Optional[Dict]:
        """
        Mintsoft no tiene endpoint directo por SKU,
        así que buscamos en memoria.
        """

        for product in self.get_all_products():
            if product.get("SKU") == sku:
                return product

        return None
