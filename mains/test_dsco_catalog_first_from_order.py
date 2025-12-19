from dotenv import load_dotenv
import json
from datetime import datetime, timedelta, timezone

from clients.dsco_order_client import DscoOrderClient
from clients.dsco_product_client import DscoProductClient
from loggers.product_logger import get_product_logger


def main():
    load_dotenv()

    logger = get_product_logger()
    logger.info("===== DSCO CATALOG TEST FROM ORDER START =====")

    order_client = DscoOrderClient()
    product_client = DscoProductClient()

    # -------------------------------------------------
    # Fechas requeridas por DSCO /order/page
    # -------------------------------------------------

    orders_updated_since = "2024-01-01T00:00:00Z"
    until = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


    # -------------------------------------------------
    # 1️⃣ Traer UNA orden
    # -------------------------------------------------
    orders_updated_since = "2024-01-01T00:00:00Z"
    until = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    orders_page = order_client.get_orders_page(
        updated_since=orders_updated_since,
        updated_until=until,
        limit=1,
    )


    logger.debug("Raw orders_page response:")
    logger.debug(json.dumps(orders_page, indent=2))

    orders = orders_page.get("orders") or []

    if not orders:
        logger.warning("No orders found in response")
        return

    order = orders[0]
    order_number = order.get("consumerOrderNumber")

    logger.info(f"Order number: {order_number}")

    # -------------------------------------------------
    # 2️⃣ Obtener el primer SKU
    # -------------------------------------------------
    order_lines = order.get("orderLines") or []

    if not order_lines:
        logger.warning("Order has no orderLines")
        logger.info(json.dumps(order, indent=2))
        return

    line = order_lines[0]

    sku = (
        line.get("sku")
        or line.get("partnerSku")
        or line.get("item", {}).get("sku")
    )

    if not sku:
        logger.warning("No SKU found in order line")
        logger.info(json.dumps(line, indent=2))
        return

    logger.info(f"Using SKU: {sku}")

    # -------------------------------------------------
    # 3️⃣ Buscar el producto en catálogo
    # -------------------------------------------------
    catalog_item = product_client.get_catalog_item(
        item_key="sku",
        value=sku,
    )

    if not catalog_item:
        logger.warning("Catalog item not found for SKU")
        return

    logger.info("===== CATALOG ITEM =====")
    logger.info(json.dumps(catalog_item, indent=2))

    logger.info("===== DSCO CATALOG TEST FROM ORDER END =====")


if __name__ == "__main__":
    main()
