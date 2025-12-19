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

    client = DscoProductClient()

    client._get_oauth_token()


if __name__ == "__main__":
    main()
