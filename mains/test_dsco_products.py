from dotenv import load_dotenv
import json
import os 
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from clients.dsco_product_client import DscoProductClient
from loggers.product_logger import get_product_logger

def main():
    load_dotenv()

    logger = get_product_logger()
    logger.info("===== DSCO PRODUCT TEST START =====")

    client = DscoProductClient()

    page_data = client._get(
        "/catalog",
        params={
            "itemKey": "dscoItemId",
            "value": "1298680805"
        }
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
