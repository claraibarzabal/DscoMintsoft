import os
import time
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class DscoOrderClient:
    """
    Cliente para DSCO Orders API (OAuth2)
    """

    BASE_URL = "https://api.dsco.io"
    TOKEN_URL = "https://api.dsco.io/oauth/token"

    def __init__(self):
        self.client_id = os.getenv("DSCO_CLIENT_ID")
        self.client_secret = os.getenv("DSCO_CLIENT_SECRET")

        if not self.client_id or not self.client_secret:
            raise RuntimeError("Missing DSCO_CLIENT_ID or DSCO_CLIENT_SECRET")

        self._access_token: Optional[str] = None
        self._token_expiry: float = 0

    # -------------------------------------------------
    # OAuth
    # -------------------------------------------------
    def _get_access_token(self) -> str:
        if self._access_token and time.time() < self._token_expiry:
            return self._access_token

        response = requests.post(
            self.TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            timeout=30,
        )

        response.raise_for_status()
        data = response.json()

        self._access_token = data["access_token"]
        self._token_expiry = time.time() + data.get("expires_in", 3600) - 60

        return self._access_token

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._get_access_token()}",
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
            headers=self._headers(),
            params=params,
            timeout=30,
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
        updated_from / updated_to en ISO 8601
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
    # Orders – all
    # -------------------------------------------------
    def get_orders(
        self,
        status: Optional[str] = None,
        updated_from: Optional[str] = None,
        updated_to: Optional[str] = None,
        page_size: int = 50,
        max_pages: int = 100,
    ) -> List[Dict]:

        orders: List[Dict] = []
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

            orders.extend(items)

            total_pages = data.get("totalPages")
            if total_pages is not None and page >= total_pages - 1:
                break

            page += 1

        return orders

    # -------------------------------------------------
    # Single order
    # -------------------------------------------------
    def get_order(self, order_number: str) -> Optional[Dict]:
        """
        GET /order/{orderNumber}
        """

        try:
            return self._get(f"/order/{order_number}")
        except requests.HTTPError as e:
            if e.response.status_code != 404:
                raise
        return None
