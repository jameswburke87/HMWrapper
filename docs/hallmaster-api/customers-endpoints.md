# Customers Endpoints

## List Customers (Hall)

```http
GET /api/customers/getforhall
```

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `id` | int | Yes | Hall ID |
| `customer` | string | No | `"true"` to filter to customers |
| `includeDeleted` | string | No | `"true"` or `"false"` |
| `onlyNew` | string | No | `"true"` or `"false"` |

**Response:**

```json
[
  {
    "UserId": "guid-string",
    "Name": "Jane Doe",
    "Email": "jane@example.com",
    "Phone": "01onal234",
    "Organisation": "Community Group",
    "IsBlocked": false
  }
]
```

Note: Some responses use `FullName` instead of `Name`, and `PhoneNumber` instead of `Phone`.

## List All Customers

```http
GET /api/Customers/GetAllCustomer
```

Returns all customers across all halls. Same response format.

## Customer Details

```http
GET /api/Customers/GetCustomerDetails?hallid={hall_id}
```

## Customer Notes

```http
GET /api/Customers/GetCustomerNotes?hallid={hall_id}&customerid={customer_guid}
```

## Customer Addresses

```http
GET /api/Customers/GetExistingAddresses?uid={customer_guid}
```

## Customer Groups

```http
GET /api/Customers/GetGroupsForCustomer
```

## Customer Counts

```http
GET /api/Customers/GetUnverifiedUsersCount?hallid={hall_id}
GET /api/Customers/GetNewCustomersCount?hallid={hall_id}
```

## Block Customer

```http
POST /api/Customers/BlockUser
Content-Type: application/json
RequestVerificationToken: {token}
```

**Body:**

```json
{
  "CustomerId": "guid-string",
  "HallId": {hall_id}
}
```
