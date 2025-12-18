import os
import requests
from typing import List, Dict, Optional, Union
from dotenv import load_dotenv

load_dotenv()


class DscoProductClient:
    """
    Cliente DSCO – Catalog / Products API
    Autenticación OAuth2 (client_credentials)
    """

    BASE_URL = "https://api.dsco.io"
    AUTH_URL = "https://auth.dsco.io/oauth/token"

    def __init__(self):
        self.client_id = os.getenv("DSCO_CLIENT_ID")
        self.client_secret = os.getenv("DSCO_CLIENT_SECRET")

        if not self.client_id or not self.client_secret:
            raise RuntimeError("Missing DSCO_CLIENT_ID or DSCO_CLIENT_SECRET")

        self._access_token: Optional[str] = None
        self.headers = self._build_headers()

    # -------------------------------------------------
    # OAuth
    # -------------------------------------------------
    def _get_oauth_token(self) -> str:
        """Obtiene access_token usando client_credentials"""

        if self._access_token:
            return self._access_token

        r = requests.post(
            self.AUTH_URL,
            auth=(self.client_id, self.client_secret),
            data={"grant_type": "client_credentials"},
            timeout=30,
        )
        r.raise_for_status()

        self._access_token = r.json()["access_token"]
        return self._access_token

    def _build_headers(self) -> Dict[str, str]:
        token = self._get_oauth_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    # -------------------------------------------------
    # Low level requests
    # -------------------------------------------------
    def _get(self, path: str, params: Optional[Dict] = None) -> Dict:
        url = f"{self.BASE_URL}{path}"

        r = requests.get(
            url,
            headers=self.headers,
            params=params,
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def _post(self, path: str, payload: Union[Dict, List[Dict]]) -> Dict:
        url = f"{self.BASE_URL}{path}"

        r = requests.post(
            url,
            headers=self.headers,
            json=payload,
            timeout=60,
        )
        r.raise_for_status()
        return r.json()

    # -------------------------------------------------
    # Catalog – single item lookup
    # -------------------------------------------------
    def get_catalog_item(
        self,
        *,
        item_key: str,
        value: str,
        dsco_retailer_id: Optional[str] = None,
        dsco_trading_partner_id: Optional[str] = None,
        return_multiple: bool = False,
    ) -> Dict:
        """
        GET /catalog
        item_key: dscoItemId | sku | partnerSku | upc | ean | mpn | isbn | gtin
        """

        params: Dict[str, Union[str, bool]] = {
            "itemKey": item_key,
            "value": value,
        }

        if return_multiple:
            params["returnMultiple"] = True

        if dsco_retailer_id:
            params["dscoRetailerId"] = dsco_retailer_id

        if dsco_trading_partner_id:
            params["dscoTradingPartnerId"] = dsco_trading_partner_id

        return self._get("/catalog", params=params)

    # -------------------------------------------------
    # Catalog – update small batch
    # -------------------------------------------------
    def update_catalog_small_batch(self, items: List[Dict]) -> Dict:
        """
        POST /catalog/batch/small
        items debe ser una lista de objetos ItemCatalog
        """

        if not isinstance(items, list) or not items:
            raise ValueError("items must be a non-empty list")

        return self._post("/catalog/batch/small", items)
