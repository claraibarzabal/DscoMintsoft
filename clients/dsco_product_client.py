import os
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class DscoProductClient:
    """
    Cliente DSCO – Products API
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
    # Products – paginated
    # -------------------------------------------------
    def get_products_page(
        self,
        page: int = 0,
        size: int = 100,
        created_at_min: Optional[str] = None,
        created_at_max: Optional[str] = None,
        updated_at_min: Optional[str] = None,
        updated_at_max: Optional[str] = None,
    ) -> Dict:
        """
        GET /product/page

        Fechas en formato ISO 8601:
        - createdAtMin / createdAtMax
        - updatedAtMin / updatedAtMax
        """

        params = {
            "page": page,
            "size": size,
        }

        if created_at_min:
            params["createdAtMin"] = created_at_min
        if created_at_max:
            params["createdAtMax"] = created_at_max
        if updated_at_min:
            params["updatedAtMin"] = updated_at_min
        if updated_at_max:
            params["updatedAtMax"] = updated_at_max

        return self._get("/product/page", params=params)

    # -------------------------------------------------
    # Products – all (auto pagination)
    # -------------------------------------------------
    def get_all_products(
        self,
        created_at_min: Optional[str] = None,
        created_at_max: Optional[str] = None,
        updated_at_min: Optional[str] = None,
        updated_at_max: Optional[str] = None,
        page_size: int = 100,
        max_pages: int = 200,
    ) -> List[Dict]:
        """
        Devuelve TODOS los productos iterando páginas
        respetando filtros de fecha si se pasan
        """

        products: List[Dict] = []
        page = 0

        while page < max_pages:
            data = self.get_products_page(
                page=page,
                size=page_size,
                created_at_min=created_at_min,
                created_at_max=created_at_max,
                updated_at_min=updated_at_min,
                updated_at_max=updated_at_max,
            )

            items = (
                data.get("content")
                or data.get("items")
                or data.get("products")
                or []
            )

            if not items:
                break

            products.extend(items)

            total_pages = data.get("totalPages")
            if total_pages is not None and page >= total_pages - 1:
                break

            page += 1

        return products

    # -------------------------------------------------
    # Single product (fallback)
    # -------------------------------------------------
    def get_product(self, sku: str) -> Optional[Dict]:
        """
        Busca un producto por SKU.

        ⚠️ Fallback costoso: trae todos los productos sin filtros.
        """

        for product in self.get_all_products():
            if product.get("sku") == sku:
                return product

        return None
