import os
import time
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()


class DscoOrderClient:
    """
    Cliente DSCO Orders API (OAuth2)
    Implementación correcta según documentación oficial
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
            "Accept": "application/json",
        }

    # -------------------------------------------------
    # Low level request
    # -------------------------------------------------
    def _get(self, path: str, params: Dict) -> Dict:
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
    # Orders – paginated (scrollId)
    # -------------------------------------------------
    def get_orders_page(
        self,
        *,
        orders_created_since: Optional[str] = None,
        orders_updated_since: Optional[str] = None,
        until: str,
        status: Optional[List[str]] = None,
        include_test_orders: bool = False,
        orders_per_page: int = 1000,
        scroll_id: Optional[str] = None,
    ) -> Dict:
        """
        GET /order/page

        Reglas DSCO:
        - Si scrollId existe, ignora el resto
        - until es obligatorio
        - ordersCreatedSince o ordersUpdatedSince es obligatorio
        """

        params: Dict = {}

        if scroll_id:
            params["scrollId"] = scroll_id
            return self._get("/order/page", params)

        if not until:
            raise ValueError("until is required")

        if not (orders_created_since or orders_updated_since):
            raise ValueError(
                "ordersCreatedSince or ordersUpdatedSince is required"
            )

        params["until"] = until
        params["ordersPerPage"] = min(max(orders_per_page, 10), 1000)

        if orders_created_since:
            params["ordersCreatedSince"] = orders_created_since

        if orders_updated_since:
            params["ordersUpdatedSince"] = orders_updated_since

        if include_test_orders:
            params["includeTestOrders"] = "true"

        if status:
            for s in status:
                params.setdefault("status", []).append(s)

        return self._get("/order/page", params)

    # -------------------------------------------------
    # Orders – all (auto scroll)
    # -------------------------------------------------
    def get_all_orders(
        self,
        *,
        orders_updated_since: str,
        until: str,
        status: Optional[List[str]] = None,
    ) -> List[Dict]:
        """
        Descarga todas las órdenes usando scrollId
        """

        orders: List[Dict] = []
        scroll_id: Optional[str] = None

        while True:
            data = self.get_orders_page(
                orders_updated_since=orders_updated_since,
                until=until,
                status=status,
                scroll_id=scroll_id,
            )

            batch = data.get("orders", [])
            if not batch:
                break

            orders.extend(batch)
            scroll_id = data.get("scrollId")

            if not scroll_id:
                break

        return orders
