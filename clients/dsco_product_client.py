import os
import base64
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class DscoProductClient:
    """
    Cliente DSCO – Products API
    Usa Basic Auth (client_id + client_secret)
    """

    BASE_URL = "https://api.dsco.io"

    def __init__(self):
        self.client_id = os.getenv("DSCO_CLIENT_ID")
        self.client_secret = os.getenv("DSCO_CLIENT_SECRET")

        if not self.client_id or not self.client_secret:
            raise RuntimeError("Missing DSCO_CLIENT_ID or DSCO_CLIENT_SECRET")

        # Basic Auth token
        token = f"{self.client_id}:{self.client_secret}"
        encoded = base64.b64encode(token.encode()).decode()

        self.headers = {
            "Authorization": f"Basic {encoded}",
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

        return self._get("/item/page", params=params)

    # -------------------------------------------------
    # Products – all
    # -------------------------------------------------
    def get_all_products(
        self,
        page_size: int = 100,
        max_pages: int = 200,
    ) -> List[Dict]:

        products: List[Dict] = []
        page = 0

        while page < max_pages:
            data = self.get_products_page(
                page=page,
                size=page_size,
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

    def get_catalog_item(
        self,
        item_code: Optional[str] = None,
        upc: Optional[str] = None,
    ) -> Optional[Dict]:

        params = {}

        if item_code:
            params["itemCode"] = item_code
        elif upc:
            params["upc"] = upc
        else:
            raise ValueError("Must provide itemCode or UPC")

        return self._get("/catalog", params=params)

   