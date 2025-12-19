import os
import requests
from typing import Dict, Optional, List
from dotenv import load_dotenv
import time


load_dotenv()


class DscoOrderClient:
    """
    Cliente DSCO – Orders API
    OAuth2 client_credentials
    """

    AUTH_URL = "https://api.dsco.io/api/v3/oauth2/token"
    BASE_URL = "https://api.dsco.io/api/v3"

    def __init__(self):
        self.client_id = os.getenv("DSCO_CLIENT_ID")
        self.client_secret = os.getenv("DSCO_CLIENT_SECRET")

        if not self.client_id or not self.client_secret:
            raise RuntimeError("Missing DSCO_CLIENT_ID or DSCO_CLIENT_SECRET")

        self._access_token: Optional[str] = None

    # -------------------------------------------------
    # OAuth
    # -------------------------------------------------
    def _get_access_token(self) -> str:
        if self._access_token and self._token_expiry and time.time() < self._token_expiry:
            return self._access_token

        response = requests.post(
            self.AUTH_URL,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            timeout=30,
        )

        if not response.ok:
            raise RuntimeError(
                f"OAuth failed {response.status_code}: {response.text}"
            )

        data = response.json()
        self._access_token = data["access_token"]
        self._token_expiry = time.time() + data.get("expires_in", 3600) - 60

        return self._access_token



    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Accept": "application/json",
            "Content-Type": "application/json",
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

    # ------------------------------------------------
    # Get single order
    # -----------------------------------------------
    def get_order(
        self,
        *,
        order_key: str,
        value: str,
        dsco_account_id: Optional[str] = None,
        dsco_trading_partner_id: Optional[str] = None,
        return_multiple: bool = False,
    ) -> Dict:
        params = {
            "orderKey": order_key,
            "value": value,
        }

        if return_multiple:
            params["returnMultiple"] = True

        if dsco_account_id:
            params["dscoAccountId"] = dsco_account_id

        if dsco_trading_partner_id:
            params["dscoTradingPartnerId"] = dsco_trading_partner_id

        return self._get("/order/", params)

    # -------------------------------------------------
    # Orders – paginated
    # -------------------------------------------------
    def get_orders_page(
        self,
        *,
        limit: int = 100,
        scroll_id: Optional[str] = None,
        ordersCreatedSince: Optional[str] = None,
        until: Optional[str] = None,
    ) -> Dict:
        payload = {}

        if scroll_id:
            payload["scrollId"] = scroll_id
        else:
            payload["limit"] = limit
            if not ordersCreatedSince and not until:
                raise ValueError("Must provide ordersCreatedSince and/or until")
            if ordersCreatedSince:
                payload["ordersCreatedSince"] = ordersCreatedSince
            if until:
                payload["until"] = until

        r = requests.post(
            url=f"{self.BASE_URL}/order/page",
            headers=self._headers(),
            json=payload,
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

 #   def get_orders_page(
 #       self,
 #       *,
 #       updated_since: str,
 #       updated_until: str,
 #       limit: int = 100,
 #       scroll_id: Optional[str] = None,
  #  ) -> Dict:
  #      payload = {}
 #       if scroll_id:
 #           payload["scrollId"] = scroll_id
 #       else:
 #           payload = {
 #               "updatedSince": updated_since,
 #               "updatedUntil": updated_until,
 #               "limit": limit,
 #           }

 #       r = requests.post(
 #           url=f"{self.BASE_URL}/order/page",
 #           headers=self._headers(),
 #           json=payload,  # ⚠️ body JSON, no query string
 #           timeout=30,
 #       )
 #       r.raise_for_status()
 #       return r.json()

        # params = {}
       
        # if scroll_id:
        #    params["scrollId"] = scroll_id
        # else:
        #   params["updatedSince"] = updated_since
        #    params["updatedUntil"] = updated_until
        #    params["limit"] = limit

        #return self._get("/order/page", params)


    # -------------------------------------------------
    # Orders – all (auto scroll)
    # -------------------------------------------------
    def get_all_orders(
        self,
        *,
        orders_updated_since: str,
        until: str,
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
