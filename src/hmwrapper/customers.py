"""Customers API — list, details, notes, blocking."""

from __future__ import annotations

from typing import Any

from .client import HallmasterClient
from .models import Customer


class CustomersAPI:
    """Interface to Hallmaster customer endpoints."""

    def __init__(self, client: HallmasterClient):
        self.client = client
        self.hall_id = client.hall_id

    def list_customers(
        self,
        include_deleted: bool = False,
        only_new: bool = False,
    ) -> list[Customer]:
        """Get all customers for the hall."""
        data = self.client.get(
            "/api/customers/getforhall",
            params={
                "id": self.hall_id,
                "customer": "true",
                "includeDeleted": str(include_deleted).lower(),
                "onlyNew": str(only_new).lower(),
            },
        )
        rows = data if isinstance(data, list) else data.get("Data", data.get("data", []))
        return [Customer.from_api(row) for row in rows]

    def get_customer_details(self) -> Any:
        """Get customer detail for the current hall context."""
        return self.client.get(
            "/api/Customers/GetCustomerDetails",
            params={"hallid": self.hall_id},
        )

    def get_customer_notes(self, customer_id: str) -> Any:
        """Get notes for a specific customer.

        Args:
            customer_id: Customer GUID.
        """
        return self.client.get(
            "/api/Customers/GetCustomerNotes",
            params={"hallid": self.hall_id, "customerid": customer_id},
        )

    def get_existing_addresses(self, customer_id: str) -> Any:
        """Get saved addresses for a customer.

        Args:
            customer_id: Customer GUID.
        """
        return self.client.get(
            "/api/Customers/GetExistingAddresses",
            params={"uid": customer_id},
        )

    def get_all_customers(self) -> list[Customer]:
        """Get all customers (no hall filter)."""
        data = self.client.get("/api/Customers/GetAllCustomer")
        rows = data if isinstance(data, list) else data.get("Data", data.get("data", []))
        return [Customer.from_api(row) for row in rows]

    def get_groups(self) -> Any:
        """Get customer groups."""
        return self.client.get("/api/Customers/GetGroupsForCustomer")

    def get_unverified_count(self) -> int:
        """Get count of unverified users."""
        return self.client.get(
            "/api/Customers/GetUnverifiedUsersCount",
            params={"hallid": self.hall_id},
        )

    def get_new_count(self) -> int:
        """Get count of new customers."""
        return self.client.get(
            "/api/Customers/GetNewCustomersCount",
            params={"hallid": self.hall_id},
        )

    def block_customer(self, customer_id: str) -> Any:
        """Block a customer.

        Args:
            customer_id: Customer GUID to block.
        """
        r = self.client.post(
            "/api/Customers/BlockUser",
            json={"CustomerId": customer_id, "HallId": self.hall_id},
        )
        try:
            return r.json()
        except ValueError:
            return r.text
