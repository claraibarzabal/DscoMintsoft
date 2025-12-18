from time import time
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional

from clients.dsco_product_client import DscoProductClient
from clients.mintsoft_product_client import MintsoftProductClient
from mappers.product_mapper import map_dsco_product_to_mintsoft
from loggers.product_logger import get_product_logger


class ProductSyncService:
    """
    Orquesta la sincronización de productos:
    DSCO → Mintsoft
    """

    def __init__(self):
        self.logger = get_product_logger()
        self.dsco_client = DscoProductClient()
        self.mintsoft_client = MintsoftProductClient()

    # -------------------------------------------------
    # Utils
    # -------------------------------------------------
    @staticmethod
    def _iso(dt: datetime) -> str:
        return dt.astimezone(timezone.utc).isoformat()

    # -------------------------------------------------
    # Sync de un solo producto
    # -------------------------------------------------
    def sync_one_product(self, dsco_product: Dict[str, Any]) -> bool:
        sku = dsco_product.get("sku") or dsco_product.get("itemCode")

        if not sku:
            self.logger.warning("[PRODUCT] Missing SKU / itemCode")
            return False

        start = time()
        self.logger.info(f"[PRODUCT] Sync started | SKU={sku}")

        try:
            payload = map_dsco_product_to_mintsoft(dsco_product)

            existing = self.mintsoft_client.get_product_by_sku(sku)

            if existing:
                product_id = existing.get("ID")
                if not product_id:
                    raise RuntimeError(
                        f"Mintsoft product without ID | SKU={sku}"
                    )

                self.logger.info(
                    f"[PRODUCT] Updating Mintsoft product | "
                    f"SKU={sku} | ID={product_id}"
                )

                response = self.mintsoft_client.update_product(
                    product_id,
                    payload
                )
            else:
                self.logger.info(
                    f"[PRODUCT] Creating Mintsoft product | SKU={sku}"
                )

                response = self.mintsoft_client.create_product(payload)

            elapsed = round(time() - start, 2)
            self.logger.info(
                f"[PRODUCT] Synced OK | "
                f"SKU={sku} | "
                f"ProductId={response.get('ID')} | "
                f"{elapsed}s"
            )

            return True

        except Exception as e:
            self.logger.exception(
                f"[PRODUCT] Sync FAILED | SKU={sku} | {str(e)}"
            )
            return False

    # -------------------------------------------------
    # Sync masivo con fechas
    # -------------------------------------------------
    def sync_all_products(
        self,
        page_size: int = 100,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
        updated_from: Optional[datetime] = None,
        updated_to: Optional[datetime] = None,
    ):
        """
        Sincroniza productos DSCO → Mintsoft
        filtrando por fechas de creación / actualización
        """

        now = datetime.now(timezone.utc)

        if not created_to:
            created_to = now
        if not updated_to:
            updated_to = now

        # Defaults razonables: última hora
        if not created_from:
            created_from = created_to - timedelta(hours=1)
        if not updated_from:
            updated_from = updated_to - timedelta(hours=1)

        created_from_iso = self._iso(created_from)
        created_to_iso = self._iso(created_to)
        updated_from_iso = self._iso(updated_from)
        updated_to_iso = self._iso(updated_to)

        self.logger.info(
            "[BATCH] Product sync started | "
            f"createdFrom={created_from_iso} | "
            f"createdTo={created_to_iso} | "
            f"updatedFrom={updated_from_iso} | "
            f"updatedTo={updated_to_iso}"
        )

        page = 0
        total = success = failed = 0

        while True:
            page_data = self.dsco_client.get_products_page(
                page=page,
                size=page_size,
                created_at_min=created_from_iso,
                created_at_max=created_to_iso,
                updated_at_min=updated_from_iso,
                updated_at_max=updated_to_iso,
            )

            products = (
                page_data.get("content")
                or page_data.get("items")
                or page_data.get("products")
                or []
            )

            if not products:
                break

            self.logger.info(
                f"[BATCH] Page {page} fetched | products={len(products)}"
            )

            for product in products:
                total += 1
                if self.sync_one_product(product):
                    success += 1
                else:
                    failed += 1

            total_pages = page_data.get("totalPages")
            if total_pages is not None and page >= total_pages - 1:
                break

            page += 1

        self.logger.info(
            "[BATCH] Product sync finished | "
            f"Total={total} | Success={success} | Failed={failed}"
        )
