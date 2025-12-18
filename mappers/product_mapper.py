import os
from typing import Dict, Any, Optional


DEFAULT_WAREHOUSE_ID = int(os.getenv("MINTSOFT_WAREHOUSE_ID", 1))
DEFAULT_CLIENT_ID = int(os.getenv("MINTSOFT_CLIENT_ID", 1))


def map_dsco_product_to_mintsoft(dsco_product: Dict[str, Any]) -> Dict[str, Any]:
    """
    DSCO → Mintsoft Product mapper
    Safe for create & update
    """

    sku = _clean_str(dsco_product.get("sku"))
    if not sku:
        raise ValueError(f"DSCO product missing SKU: {dsco_product}")

    name = (
        _clean_str(dsco_product.get("name"))
        or _clean_str(dsco_product.get("description"))
        or sku
    )

    barcode = _clean_str(dsco_product.get("barcode"))

    price = _to_float(dsco_product.get("price"))
    weight = _to_float(dsco_product.get("weight"))

    # Dimensiones
    dims = dsco_product.get("dimensions") or {}

    length = _to_float(dims.get("length"))
    width = _to_float(dims.get("width"))
    height = _to_float(dims.get("height"))

    # Sólo enviar dimensiones completas
    has_dimensions = all(v is not None for v in (length, width, height))

    payload: Dict[str, Any] = {
        "SKU": sku,
        "Name": name,
        "Barcode": barcode,

        "ClientId": DEFAULT_CLIENT_ID,
        "WarehouseId": DEFAULT_WAREHOUSE_ID,

        "RetailPrice": price if price is not None else 0.0,
        "Weight": weight,

        "IsActive": True,
        "IsStockItem": True,
        "IsSerialized": False,
        "IsBatchTracked": False,
    }

    if has_dimensions:
        payload.update({
            "Length": length,
            "Width": width,
            "Height": height,
        })

    return _remove_empty(payload)


# -------------------------------------------------
# Helpers
# -------------------------------------------------
def _clean_str(value: Any) -> Optional[str]:
    if not value:
        return None
    value = str(value).strip()
    return value if value else None


def _to_float(value: Any) -> Optional[float]:
    try:
        if value in (None, "", "null"):
            return None
        return float(value)
    except Exception:
        return None


def _remove_empty(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        k: v
        for k, v in data.items()
        if v not in (None, "", [], {})
    }
