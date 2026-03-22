"""Admin API — activity types, pricing, line items, reports, audits."""

from __future__ import annotations

from typing import Any

from .client import HallmasterClient
from .models import ActivityType, PriceRate


class AdminAPI:
    """Interface to Hallmaster admin/config endpoints."""

    def __init__(self, client: HallmasterClient):
        self.client = client
        self.hall_id = client.hall_id

    # --- Activity Types ---

    def get_activity_types(self) -> list[ActivityType]:
        """Get booking types/categories for the hall."""
        data = self.client.get(
            "/api/ActivityTypes/GetForHall",
            params={"id": self.hall_id},
        )
        rows = data if isinstance(data, list) else data.get("Data", data.get("data", []))
        return [ActivityType.from_api(row) for row in rows]

    # --- Pricing ---

    def get_price_rates(self) -> list[PriceRate]:
        """Get price rates for the hall."""
        data = self.client.get(
            "/api/PriceRates/GetForHall",
            params={"id": self.hall_id},
        )
        rows = data if isinstance(data, list) else data.get("Data", data.get("data", []))
        return [PriceRate.from_api(row) for row in rows]

    def get_charge_matrix_rooms(self) -> Any:
        """Get rooms in the charge matrix."""
        return self.client.get(
            "/api/ChargeMatrix/GetRoomsForHall",
            params={"id": self.hall_id},
        )

    def get_charge_matrix_rates(
        self, date_range_id: int, new_date_range: bool = False
    ) -> Any:
        """Get price rates for a specific date range."""
        return self.client.get(
            "/api/ChargeMatrix/GetPriceRatesForHall",
            params={
                "id": self.hall_id,
                "dateRangeId": date_range_id,
                "newDateRange": str(new_date_range).lower(),
            },
        )

    def get_tax_rates(self) -> Any:
        """Get tax rates for the hall."""
        return self.client.get(
            "/api/Halls/GetTaxRatesForHall",
            params={"id": self.hall_id},
        )

    def get_fixed_time_slots(self) -> Any:
        """Get fixed time slots."""
        return self.client.get("/api/TimeSlots/GetFixedSlots")

    # --- Line Items ---

    def get_line_item_groups(self) -> Any:
        """Get line item groups for the hall."""
        return self.client.get(
            "/api/lineitemgroups/getforhall",
            params={"id": self.hall_id},
        )

    def get_line_items_by_group(self, group_id: int) -> Any:
        """Get line items within a group."""
        return self.client.get(
            "/api/LineItemGroups/GetLineItemsByGroupId",
            params={"id": group_id},
        )

    # --- Reports & Audits ---

    def get_reports(self) -> Any:
        """Get available report templates."""
        return self.client.get(
            "/api/reports/getreports",
            params={"hallid": self.hall_id},
        )

    def get_audit_log(self, timerange: int = 5) -> Any:
        """Get audit log entries.

        Args:
            timerange: 0=Today, 1=Last7Days, ..., 5=All.
        """
        return self.client.get(
            "/api/audits/getforhall",
            params={"id": self.hall_id, "timerange": timerange},
        )

    # --- Misc ---

    def get_invoice_counter(self) -> Any:
        """Get the invoice counter."""
        return self.client.get(
            "/api/Invoicing/GetInvoiceCounter",
            params={"hallid": self.hall_id},
        )

    def has_outstanding_invoice(self) -> Any:
        """Check subscription status."""
        return self.client.get(
            "/api/Subscription/HasOutstandingInvoice",
            params={"hallid": self.hall_id},
        )

    def generate_access_pin(self) -> Any:
        """Generate an IoT access PIN."""
        return self.client.get(
            "/api/HeatingAccess/GenerateAccessPIN",
            params={"hallid": self.hall_id},
        )
