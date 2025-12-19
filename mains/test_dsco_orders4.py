from dotenv import load_dotenv
import json
import os
import sys
from datetime import datetime, timedelta, timezone

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
    # Fechas de esta semana (UTC) para retailerCreateDate
    # -------------------------------------------------
    today = datetime.now(timezone.utc)
    start_of_week = today - timedelta(days=today.weekday())  # lunes
    end_of_week = today  # hasta ahora

    orders_created_since = start_of_week.strftime("%Y-%m-%dT%H:%M:%SZ")
    until = (end_of_week - timedelta(seconds=5)).strftime("%Y-%m-%dT%H:%M:%SZ")  # al menos 5 seg en el pasado

    logger.info(f"Fetching orders between {orders_created_since} and {until}")

    try:
        # -------------------------------------------------
        # Traer 5 órdenes usando retailerCreateDate
        # -------------------------------------------------
        orders_page = order_client.get_orders_page(
            limit=5,
            ordersCreatedSince=orders_created_since,
            until=until
        )

        orders = orders_page.get("orders", [])

        if not orders:
            logger.warning("No orders found")
            return

        logger.info(f"Fetched {len(orders)} orders")

        # -------------------------------------------------
        # Imprimir cada orden en JSON
        # -------------------------------------------------
        for i, order in enumerate(orders, start=1):
            logger.info(f"--- ORDER #{i} ---")
            logger.info(json.dumps(order, indent=2))

    except Exception as e:
        logger.error(f"Error fetching orders: {e}")

    logger.info("===== DSCO ORDER TEST END =====")

if __name__ == "__main__":
    main()
