from dotenv import load_dotenv
import json
import os
import sys

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
    # Variable de PO Number
    # -------------------------------------------------
    poNumber = "600000499859"

    try:
        # Buscar orden usando poNumber como valor
        order = order_client.get_order(
            order_key="poNumber",  # usamos "poNumber" como key
            value=poNumber,
        )
    except Exception as e:
        logger.error(f"Error fetching order: {e}")
        return

    # -------------------------------------------------
    # Imprimir JSON completo de la orden
    # -------------------------------------------------
    logger.info(f"Order fetched successfully for PO Number: {poNumber}")
    logger.info(json.dumps(order, indent=2))

    logger.info("===== DSCO ORDER TEST END =====")

if __name__ == "__main__":
    main()
