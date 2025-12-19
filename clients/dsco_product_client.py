import os
import time
import requests
from typing import List, Dict, Optional, Union
from dotenv import load_dotenv

load_dotenv()


class DscoProductClient:
    """
    Cliente DSCO – Catalog / Products API
    Autenticación OAuth2 (client_credentials)
    """

    BASE_URL = "https://api.dsco.io/api/v3"
    TOKEN_URL = "https://api.dsco.io/api/v3/oauth2/token"


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
    def _get_oauth_token(self) -> str:
        if self._access_token and time.time() < self._token_expiry:
            return self._access_token

        r = requests.post(
            self.TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            timeout=30,
        )
        r.raise_for_status()

        data = r.json()
        self._access_token = data["access_token"]
        self._token_expiry = time.time() + data.get("expires_in", 3600) - 60

        return self._access_token

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._get_oauth_token()}",
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
            headers=self._headers(),
            params=params,
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def _post(self, path: str, payload: Union[Dict, List[Dict]]) -> Dict:
        url = f"{self.BASE_URL}{path}"

        r = requests.post(
            url,
            headers=self._headers(),
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
        item_key: sku | partnerSku | upc | ean | mpn | gtin | dscoItemId
        """

        params: Dict[str, Union[str, bool]] = {
            item_key: value,
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
        """

        if not isinstance(items, list) or not items:
            raise ValueError("items must be a non-empty list")

        return self._post("/catalog/batch/small", items)

