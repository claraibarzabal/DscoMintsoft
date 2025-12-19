from dotenv import load_dotenv
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from clients.dsco_order_client import DscoOrderClient
from loggers.product_logger import get_product_logger

def main():
    load_dotenv()

    logger = get_product_logger()
    logger.info("===== DSCO ORDER TEST START =====")

    order_client = DscoOrderClient()

    # -------------------------------------------------
    # Fechas para traer órdenes
    # -------------------------------------------------
    updated_since = "2024-01-01T00:00:00Z"  
    updated_until = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        # Traer 5 órdenes
        orders_page = order_client.get_orders_page(
            updated_since=updated_since,
            updated_until=updated_until,
            limit=5,
        )
        orders = orders_page.get("orders", [])

        if not orders:
            logger.warning("No orders found")
            return

        logger.info(f"Fetched {len(orders)} orders")

        # Imprimir cada orden en JSON
        for i, order in enumerate(orders, start=1):
            logger.info(f"--- ORDER #{i} ---")
            logger.info(json.dumps(order, indent=2))

    except Exception as e:
        logger.error(f"Error fetching orders: {e}")

    logger.info("===== DSCO ORDER TEST END =====")

if __name__ == "__main__":
    main()
