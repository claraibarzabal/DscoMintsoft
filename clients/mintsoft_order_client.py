import os
import requests
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()


class MintsoftOrderClient:
    """
    Cliente Mintsoft – Orders API
    """

    BASE_URL = "https://api.mintsoft.co.uk"

    def __init__(self):
        self.username = os.getenv("MINTSOFT_USERNAME")
        self.password = os.getenv("MINTSOFT_PASSWORD")
        self.client_id = os.getenv("MINTSOFT_CLIENT_ID")

        if not all([self.username, self.password, self.client_id]):
            raise RuntimeError(
                "Missing Mintsoft credentials "
                "(MINTSOFT_USERNAME / MINTSOFT_PASSWORD / MINTSOFT_CLIENT_ID)"
            )

        self.api_key = self._authenticate()

    # -------------------------------------------------
    # Auth
    # -------------------------------------------------
    def _authenticate(self) -> str:
        url = f"{self.BASE_URL}/api/Auth"

        payload = {
            "Username": self.username,
            "Password": self.password,
        }

        r = requests.post(url, json=payload, timeout=30)
        r.raise_for_status()

        # Mintsoft devuelve directamente la API key como string
        return r.json()

    # -------------------------------------------------
    # Headers
    # -------------------------------------------------
    @property
    def headers(self) -> Dict[str, str]:
        return {
            "ms-apikey": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    # -------------------------------------------------
    # Orders – Create
    # -------------------------------------------------
    def create_order(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/api/Order"

        r = requests.put(
            url,
            headers=self.headers,
            json=payload,
            timeout=30,
        )
        r.raise_for_status()

        return r.json() if r.text else {}

    # -------------------------------------------------
    # Orders – Update
    # -------------------------------------------------
    def update_order(
        self,
        order_id: int,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:

        url = f"{self.BASE_URL}/api/Order/{order_id}"

        r = requests.post(
            url,
            headers=self.headers,
            json=payload,
            timeout=30,
        )
        r.raise_for_status()

        return r.json() if r.text else {}

    # -------------------------------------------------
    # Orders – Get all (auto pagination)
    # -------------------------------------------------
    def get_orders(
        self,
        page_size: int = 100,
        max_pages: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Obtiene TODAS las órdenes de Mintsoft
        usando /api/Order/List (el endpoint real)
        """

        orders: List[Dict[str, Any]] = []
        page = 1

        while page <= max_pages:
            batch = self._get_orders_page(page, page_size)

            if not batch:
                break

            orders.extend(batch)
            page += 1

        return orders

    # -------------------------------------------------
    # Orders – Get page
    # -------------------------------------------------
    def _get_orders_page(
        self,
        page: int,
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        GET /api/Order/List
        """

        url = f"{self.BASE_URL}/api/Order/List"

        params = {
            "ClientId": self.client_id,
            "PageNo": page,
            "Limit": limit,
        }

        r = requests.get(
            url,
            headers=self.headers,
            params=params,
            timeout=30,
        )
        r.raise_for_status()

        return r.json()

    # -------------------------------------------------
    # Orders – Get by OrderNumber
    # -------------------------------------------------
    def get_order_by_number(
        self,
        order_number: str
    ) -> Optional[Dict[str, Any]]:
        """
        Busca una orden en Mintsoft por OrderNumber
        (Mintsoft NO tiene endpoint directo por número)
        """

        for order in self.get_orders():
            if order.get("OrderNumber") == order_number:
                return order

        return None
