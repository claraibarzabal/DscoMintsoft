"""
Entry point for Order Sync
DSCO → Mintsoft
"""

from dotenv import load_dotenv

from services.order_service import OrderSyncService
from loggers.order_logger import get_logger


def main():
    load_dotenv()

    logger = get_logger("order_main", "orders.log")
    logger.info("===== ORDER SYNC STARTED =====")

    try:
        service = OrderSyncService()

        # ---------------------------------
        # Sync de una orden puntual (debug)
        # ---------------------------------
        # service.sync_one_order("TEST-LOCAL-001")

        # ---------------------------------
        # Sync masivo por estado
        # ---------------------------------
        service.sync_all_orders(status="released")

        logger.info("===== ORDER SYNC FINISHED SUCCESSFULLY =====")

    except Exception:
        logger.exception("===== ORDER SYNC FAILED =====")


if __name__ == "__main__":
    main()
