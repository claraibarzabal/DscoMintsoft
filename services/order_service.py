from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List

from loggers.order_logger import get_logger
from clients.dsco_order_client import DscoOrderClient
from clients.mintsoft_order_client import MintsoftOrderClient
from mappers.order_mapper import map_dsco_order_to_mintsoft


class OrderSyncService:
    """
    Orquesta la sincronización de órdenes:
    DSCO → Mintsoft
    """

    def __init__(self):
        self.logger = get_logger("order_service", "orders.log")
        self.dsco_client = DscoOrderClient()
        self.mintsoft_client = MintsoftOrderClient()

    # -------------------------------------------------
    # Utils
    # -------------------------------------------------
    @staticmethod
    def _iso(dt: datetime) -> str:
        """Convierte datetime a ISO 8601 UTC"""
        return dt.astimezone(timezone.utc).isoformat()

    # -------------------------------------------------
    # Single order sync
    # -------------------------------------------------
    def sync_one_order(self, order_number: str) -> bool:
        self.logger.info(f"[ORDER] Sync start | order={order_number}")

        try:
            dsco_order = self.dsco_client.get_order(order_number)

            if not dsco_order:
                self.logger.warning(
                    f"[ORDER] Not found in DSCO | order={order_number}"
                )
                return False

            payload = map_dsco_order_to_mintsoft(dsco_order)
            response = self.mintsoft_client.create_order(payload)

            self.logger.info(
                f"[ORDER] Synced successfully | "
                f"order={order_number} | "
                f"mintsoft_id={response.get('OrderId')}"
            )
            return True

        except Exception:
            self.logger.exception(
                f"[ORDER] Sync failed | order={order_number}"
            )
            return False

    # -------------------------------------------------
    # Batch sync con fechas
    # -------------------------------------------------
    def sync_all_orders(
        self,
        status: str = "released",
        updated_from: Optional[datetime] = None,
        updated_to: Optional[datetime] = None,
    ):
        """
        Sincroniza órdenes DSCO → Mintsoft
        filtradas por fecha de actualización
        """

        # Default: última hora → ahora
        if not updated_to:
            updated_to = datetime.now(timezone.utc)

        if not updated_from:
            updated_from = updated_to - timedelta(hours=1)

        updated_from_iso = self._iso(updated_from)
        updated_to_iso = self._iso(updated_to)

        self.logger.info(
            "[BATCH] Order sync started | "
            f"status={status} | "
            f"from={updated_from_iso} | "
            f"to={updated_to_iso}"
        )

        total = success = failed = 0
        page = 0

        while True:
            response = self.dsco_client.get_orders_page(
                page=page,
                size=50,
                status=status,
                updated_from=updated_from_iso,
                updated_to=updated_to_iso,
            )

            orders: List[Dict] = (
                response.get("content")
                or response.get("items")
                or response.get("orders")
                or []
            )

            if not orders:
                break

            self.logger.info(
                f"[BATCH] Page {page} fetched | orders={len(orders)}"
            )

            for order in orders:
                order_number = order.get("orderNumber")

                if not order_number:
                    self.logger.warning(
                        "[BATCH] Skipping order without orderNumber"
                    )
                    failed += 1
                    continue

                total += 1
                if self.sync_one_order(order_number):
                    success += 1
                else:
                    failed += 1

            # Control de última página
            total_pages = response.get("totalPages")
            if total_pages is not None and page >= total_pages - 1:
                break

            page += 1

        self.logger.info(
            "[BATCH] Order sync finished | "
            f"Total={total} | Success={success} | Failed={failed}"
        )
