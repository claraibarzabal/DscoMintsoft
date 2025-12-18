"""
Entry point for Product Sync
DSCO / XoroSoft → Mintsoft
"""

from dotenv import load_dotenv

from services.product_service import ProductSyncService
from loggers.product_logger import get_product_logger


def main():
    load_dotenv()

    logger = get_product_logger()
    logger.info("===== PRODUCT SYNC STARTED =====")

    try:
        service = ProductSyncService()

        # 🔹 Sync de un producto puntual (para testing)
        # service.sync_one_product("TEST-SKU-001")

        # 🔹 Sync masivo de productos
        service.sync_all_products()

        logger.info("===== PRODUCT SYNC FINISHED SUCCESSFULLY =====")

    except Exception:
        logger.exception("PRODUCT SYNC FAILED")


if __name__ == "__main__":
    main()
