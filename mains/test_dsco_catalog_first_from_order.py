from dotenv import load_dotenv
import json

from clients.dsco_order_client import DscoOrderClient
from clients.dsco_product_client import DscoProductClient
from loggers.product_logger import get_product_logger


def main():
    load_dotenv()

    logger = get_product_logger()
    logger.info("===== DSCO CATALOG TEST FROM ORDER START =====")

    order_client = DscoOrderClient()
    product_client = DscoProductClient()

    # 🔹 Traemos 1 order
    orders_page = order_client.get_orders_page(page=0, size=1)

    orders = (
        orders_page.get("content")
        or orders_page.get("items")
        or orders_page.get("orders")
        or []
    )

    if not orders:
        logger.warning("No orders found")
        return

    order = orders[0]

    lines = order.get("orderLines") or order.get("lines") or []
    if not lines:
        logger.warning("Order has no lines")
        return

    item_code = lines[0].get("itemCode")
    if not item_code:
        logger.warning("Order line has no itemCode")
        return

    logger.info(f"Using itemCode from order: {item_code}")

    # 🔹 Llamada REAL a /catalog
    product = product_client.get_catalog_item(item_code=item_code)

    logger.info("Catalog product fetched:")
    logger.info(json.dumps(product, indent=2))

    logger.info("===== DSCO CATALOG TEST FROM ORDER END =====")


if __name__ == "__main__":
    main()
