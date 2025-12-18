from dotenv import load_dotenv
import json

from clients.dsco_product_client import DscoProductClient
from loggers.product_logger import get_product_logger


def main():
    load_dotenv()

    logger = get_product_logger()
    logger.info("===== DSCO CATALOG PRODUCT TEST START =====")

    client = DscoProductClient()

    # 🔹 USÁ UN SKU REAL DE DSCO
    ITEM_CODE = "REEMPLAZAR_POR_UN_SKU_REAL"

    try:
        product = client.get_catalog_item(item_code=ITEM_CODE)

        if not product:
            logger.warning(f"No product found | itemCode={ITEM_CODE}")
            return

        logger.info("Product fetched successfully")
        logger.info(json.dumps(product, indent=2))

    except Exception as e:
        logger.exception(
            f"Failed to fetch catalog product | itemCode={ITEM_CODE}"
        )

    logger.info("===== DSCO CATALOG PRODUCT TEST END =====")


if __name__ == "__main__":
    main()
