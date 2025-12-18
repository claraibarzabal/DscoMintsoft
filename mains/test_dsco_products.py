from dotenv import load_dotenv
import json

from clients.dsco_product_client import DscoProductClient
from loggers.product_logger import get_product_logger

def main():
    load_dotenv()

    logger = get_product_logger()
    logger.info("===== DSCO PRODUCT TEST START =====")

    client = DscoProductClient()

    # 🔹 Traer 1 página solamente
    page_data = client.get_products_page(
        page=0,
        size=5
    )

    products = (
        page_data.get("content")
        or page_data.get("items")
        or page_data.get("products")
        or []
    )

    logger.info(f"Products fetched: {len(products)}")

    for i, product in enumerate(products, start=1):
        logger.info(f"--- PRODUCT #{i} ---")
        logger.info(json.dumps(product, indent=2))

    logger.info("===== DSCO PRODUCT TEST END =====")


if __name__ == "__main__":
    main()
