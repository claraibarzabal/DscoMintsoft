import os
from datetime import datetime
from typing import Dict, Any, List


DEFAULT_WAREHOUSE_ID = int(os.getenv("MINTSOFT_WAREHOUSE_ID", 1))
DEFAULT_CLIENT_ID = int(os.getenv("MINTSOFT_CLIENT_ID", 1))
DEFAULT_COURIER_ID = int(os.getenv("MINTSOFT_DEFAULT_COURIER_ID", 1006))

COURIER_SERVICE_MAP = {
    "UPS Ground": 1036,
    "UPS": 1036,
    "DHL": 1006,
    "FEDEX": 1007,
}


def map_dsco_order_to_mintsoft(dsco_order: Dict[str, Any]) -> Dict[str, Any]:
    """
    DSCO → Mintsoft Order mapper (production ready)
    """

    order_number = str(dsco_order.get("orderNumber", "")).strip()
    if not order_number:
        raise ValueError("DSCO order missing orderNumber")

    external_ref = dsco_order.get("externalOrderReference") or order_number

    customer = dsco_order.get("customer") or {}
    shipping = dsco_order.get("shippingAddress") or {}
    lines = dsco_order.get("orderLines") or []

    # Nombre
    first_name, last_name = _split_name(customer.get("name", ""))

    # Courier
    courier_name = dsco_order.get("shippingMethod")
    courier_service_id = COURIER_SERVICE_MAP.get(
        courier_name,
        DEFAULT_COURIER_ID
    )

    order_items = _map_order_items(lines)

    payload: Dict[str, Any] = {
        "OrderNumber": order_number,
        "ExternalOrderReference": external_ref,

        "FirstName": first_name,
        "LastName": last_name,
        "CompanyName": customer.get("company"),
        "Email": customer.get("email"),
        "Phone": customer.get("phone"),

        "Address1": shipping.get("address1"),
        "Address2": shipping.get("address2"),
        "Town": shipping.get("city"),
        "County": shipping.get("state"),
        "PostCode": shipping.get("postcode"),
        "Country": _normalize_country(shipping.get("country")),

        "WarehouseId": DEFAULT_WAREHOUSE_ID,
        "ClientId": DEFAULT_CLIENT_ID,
        "CourierServiceId": courier_service_id,

        "RequiredDespatchDate": _format_date(dsco_order.get("shipByDate")),
        "RequiredDeliveryDate": _format_date(dsco_order.get("deliverByDate")),

        "OrderItems": order_items,

        "Comments": dsco_order.get("notes"),
        "Channel": "DSCO",
    }

    return _remove_empty(payload)


# -------------------------------------------------
# Helpers
# -------------------------------------------------
def _map_order_items(lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []

    for line in lines:
        sku = line.get("sku")
        qty = int(line.get("quantity", 0))

        if not sku or qty <= 0:
            continue

        item = {
            "SKU": sku,
            "Quantity": qty,
            "WarehouseId": DEFAULT_WAREHOUSE_ID,
        }

        if line.get("unitPrice") is not None:
            item["UnitPrice"] = float(line["unitPrice"])

        items.append(item)

    return items


def _split_name(name: str):
    if not name:
        return "", ""
    parts = name.strip().split(" ", 1)
    return parts[0], parts[1] if len(parts) > 1 else ""


def _format_date(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "")).isoformat()
    except Exception:
        return None


def _normalize_country(value: str):
    if not value:
        return None
    if len(value) == 2:
        return value.upper()
    return value  # fallback


def _remove_empty(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        k: v
        for k, v in data.items()
        if v not in (None, "", [], {})
    }
