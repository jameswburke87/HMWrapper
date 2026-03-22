# Admin Endpoints

## Activity Types

```http
GET /api/ActivityTypes/GetForHall?id={hall_id}
```

**Response:**

```json
[
  {"Id": 1, "Name": "Meeting", "HallId": {hall_id}},
  {"Id": 2, "Name": "Party", "HallId": {hall_id}}
]
```

## Price Rates

```http
GET /api/PriceRates/GetForHall?id={hall_id}
```

**Response:**

```json
[
  {"Id": 1, "Name": "Standard Rate", "HallId": {hall_id}},
  {"Id": 2, "Name": "Charity Rate", "HallId": {hall_id}}
]
```

## Charge Matrix

```http
GET /api/ChargeMatrix/GetRoomsForHall?id={hall_id}
GET /api/ChargeMatrix/GetPriceRatesForHall?id={hall_id}&dateRangeId={id}&newDateRange=false
```

## Tax Rates

```http
GET /api/Halls/GetTaxRatesForHall?id={hall_id}
```

## Fixed Time Slots

```http
GET /api/TimeSlots/GetFixedSlots
```

## Line Items

```http
GET /api/lineitemgroups/getforhall?id={hall_id}
GET /api/LineItemGroups/GetLineItemsByGroupId?id={group_id}
```

## Reports

```http
GET /api/reports/getreports?hallid={hall_id}
```

## Audit Log

```http
GET /api/audits/getforhall?id={hall_id}&timerange={timerange}
```

**timerange values:** `0`=Today, `1`=Last7Days, `2`=LastMonth, `3`=Last3Months, `4`=LastYear, `5`=All

## Invoicing

```http
GET /api/Invoicing/GetInvoiceCounter?hallid={hall_id}
```

## Subscription

```http
GET /api/Subscription/HasOutstandingInvoice?hallid={hall_id}
```

## IoT / Heating Access

```http
GET /api/HeatingAccess/GenerateAccessPIN?hallid={hall_id}
```
