import os
import requests
from typing import List, Dict, Optional


class DscoOrderClient:
    """
    Cliente para DSCO Orders API
    """

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

    # -------------------------------------------------
    # Low level request
    # -------------------------------------------------
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

    # -------------------------------------------------
    # Orders – paginated
    # -------------------------------------------------
    def get_orders_page(
        self,
        page: int = 0,
        size: int = 50,
        status: Optional[str] = None,
        updated_from: Optional[str] = None,
        updated_to: Optional[str] = None,
    ) -> Dict:
        """
        GET /order/page
        Filtros de fecha en ISO 8601
        """

        params = {
            "page": page,
            "size": size,
        }

        if status:
            params["status"] = status

        if updated_from:
            params["updatedAtMin"] = updated_from

        if updated_to:
            params["updatedAtMax"] = updated_to

        return self._get("/order/page", params=params)

    # -------------------------------------------------
    # Orders – all (auto pagination)
    # -------------------------------------------------
    def get_orders(
        self,
        status: Optional[str] = None,
        updated_from: Optional[str] = None,
        updated_to: Optional[str] = None,
        page_size: int = 50,
        max_pages: int = 100,
    ) -> List[Dict]:
        """
        Devuelve TODAS las órdenes iterando páginas
        (respetando filtros si se pasan)
        """

        all_orders: List[Dict] = []
        page = 0

        while page < max_pages:
            data = self.get_orders_page(
                page=page,
                size=page_size,
                status=status,
                updated_from=updated_from,
                updated_to=updated_to,
            )

            items = (
                data.get("content")
                or data.get("items")
                or data.get("orders")
                or []
            )

            if not items:
                break

            all_orders.extend(items)

            total_pages = data.get("totalPages")
            if total_pages is not None and page >= total_pages - 1:
                break

            page += 1

        return all_orders

    # -------------------------------------------------
    # Single order
    # -------------------------------------------------
    def get_order(self, order_number: str) -> Optional[Dict]:
        """
        Busca una orden puntual por orderNumber

        ⚠️ Fallback sin filtros de fecha ni status
        """

        try:
            return self._get(f"/order/{order_number}")
        except requests.HTTPError as e:
            if e.response.status_code != 404:
                raise

        # Fallback: búsqueda completa
        for order in self.get_orders():
            if order.get("orderNumber") == order_number:
                return order

        return None
