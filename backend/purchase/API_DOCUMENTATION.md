# Purchase Management API Documentation

## Base URL
```
http://localhost:8000/api/
```

## Authentication
This API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

---

## Purchase Management Endpoints

### 1. List All Purchases
- **URL:** `GET /api/purchases/`
- **Permission:** Authenticated
- **Description:** Get list of all purchases with pagination and filtering

**Query Parameters:**
- `customer_id`: Filter by specific customer ID
- `product_id`: Filter by specific product ID
- `shop_id`: Filter by specific shop ID (through product)
- `payment_status`: Filter by payment status (pending/completed/failed/refunded)
- `purchase_method`: Filter by purchase method (cash/card/bank_transfer/mobile_payment/credit)
- `is_active`: Filter by active status (true/false)
- `start_date`: Filter by start date (ISO format: 2025-09-25T10:00:00Z)
- `end_date`: Filter by end date (ISO format: 2025-09-25T18:00:00Z)
- `search`: Search in customer name, product name, shop name, or notes
- `page`: Page number for pagination
- `ordering`: Order by fields (date, total_amount, created_at)

**Response:**
```json
{
    "success": true,
    "message": "Purchases retrieved successfully",
    "data": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "date": "2025-09-25T14:30:00Z",
            "customer": 1,
            "customer_name": "John Doe",
            "customer_username": "johndoe",
            "product": "660e8400-e29b-41d4-a716-446655440001",
            "product_name": "Smartphone XYZ",
            "product_code": "PRD-660E8400",
            "shop_name": "Tech Store",
            "shop_id": 1,
            "quantity": 2,
            "unit_price": "299.99",
            "total_amount": "599.98",
            "payment_status": "completed",
            "purchase_method": "card",
            "purchase_code": "PUR-550E8400",
            "created_at": "2025-09-25T14:30:00Z"
        }
    ]
}
```

### 2. Create New Purchase
- **URL:** `POST /api/purchases/`
- **Permission:** Authenticated
- **Description:** Create a new purchase (automatically updates product stock)

**Request Body:**
```json
{
    "date": "2025-09-25T15:00:00Z",
    "product": "660e8400-e29b-41d4-a716-446655440001",
    "customer": 1,
    "quantity": 1,
    "unit_price": "299.99",
    "payment_status": "completed",
    "purchase_method": "cash",
    "notes": "Customer paid in cash"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Purchase created successfully",
    "data": {
        "id": "770e8400-e29b-41d4-a716-446655440002",
        "date": "2025-09-25T15:00:00Z",
        "product": "660e8400-e29b-41d4-a716-446655440001",
        "product_name": "Smartphone XYZ",
        "product_code": "PRD-660E8400",
        "customer": 1,
        "customer_name": "John Doe",
        "customer_username": "johndoe",
        "shop_name": "Tech Store",
        "shop_id": 1,
        "quantity": 1,
        "unit_price": "299.99",
        "total_amount": "299.99",
        "payment_status": "completed",
        "purchase_method": "cash",
        "notes": "Customer paid in cash",
        "is_active": true,
        "purchase_code": "PUR-770E8400",
        "customer_info": {
            "customer_id": 1,
            "customer_name": "John Doe",
            "customer_username": "johndoe"
        },
        "product_info": {
            "product_id": "660e8400-e29b-41d4-a716-446655440001",
            "product_name": "Smartphone XYZ",
            "product_code": "PRD-660E8400",
            "current_price": "299.99"
        },
        "shop_info": {
            "shop_id": 1,
            "shop_name": "Tech Store",
            "shop_address": "123 Main Street, Suite 101, Colombo, 10001"
        },
        "purchase_summary": {
            "purchase_code": "PUR-770E8400",
            "date": "2025-09-25T15:00:00Z",
            "customer": {
                "customer_id": 1,
                "customer_name": "John Doe",
                "customer_username": "johndoe"
            },
            "product": {
                "product_id": "660e8400-e29b-41d4-a716-446655440001",
                "product_name": "Smartphone XYZ",
                "product_code": "PRD-660E8400",
                "current_price": "299.99"
            },
            "shop": {
                "shop_id": 1,
                "shop_name": "Tech Store",
                "shop_address": "123 Main Street, Suite 101, Colombo, 10001"
            },
            "quantity": 1,
            "unit_price": "299.99",
            "total_amount": "299.99",
            "payment_status": "completed",
            "payment_method": "cash"
        },
        "created_at": "2025-09-25T15:00:00Z",
        "updated_at": "2025-09-25T15:00:00Z"
    }
}
```

### 3. Get Specific Purchase
- **URL:** `GET /api/purchases/{id}/`
- **Permission:** Authenticated
- **Description:** Get details of a specific purchase

### 4. Update Purchase
- **URL:** `PUT /api/purchases/{id}/`
- **Permission:** Authenticated
- **Description:** Update a purchase (automatically adjusts product stock if quantity changes)

**Request Body:**
```json
{
    "date": "2025-09-25T15:30:00Z",
    "quantity": 2,
    "unit_price": "289.99",
    "payment_status": "completed",
    "purchase_method": "card",
    "notes": "Updated quantity and payment method"
}
```

### 5. Partial Update Purchase
- **URL:** `PATCH /api/purchases/{id}/`
- **Permission:** Authenticated
- **Description:** Partially update specific fields of a purchase

### 6. Delete Purchase
- **URL:** `DELETE /api/purchases/{id}/`
- **Permission:** Authenticated
- **Description:** Delete a purchase (automatically restores product stock)

**Response:**
```json
{
    "success": true,
    "message": "Purchase deleted successfully"
}
```

### 7. Update Payment Status
- **URL:** `POST /api/purchases/{id}/update_payment_status/`
- **Permission:** Authenticated
- **Description:** Update the payment status of a specific purchase

**Request Body:**
```json
{
    "payment_status": "completed"
}
```

**Valid Payment Statuses:**
- `pending` - Payment is pending
- `completed` - Payment completed successfully
- `failed` - Payment failed
- `refunded` - Payment was refunded

**Response:**
```json
{
    "success": true,
    "message": "Payment status updated to completed",
    "data": {
        // ... full purchase data
    }
}
```

### 8. Toggle Purchase Status
- **URL:** `POST /api/purchases/{id}/toggle_status/`
- **Permission:** Authenticated
- **Description:** Toggle active/inactive status of a purchase

**Response:**
```json
{
    "success": true,
    "message": "Purchase activated successfully",
    "data": {
        // ... full purchase data
    }
}
```

### 9. Get Purchases by Customer
- **URL:** `GET /api/purchases/by_customer/`
- **Permission:** Authenticated
- **Description:** Get all purchases for a specific customer

**Query Parameters:**
- `customer_id`: Customer ID (required)
- `is_active`: Filter by active status (optional)

**Response:**
```json
{
    "success": true,
    "message": "Purchases for customer \"John Doe\" retrieved successfully",
    "data": {
        "id": 1,
        "username": "johndoe",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "purchases": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "date": "2025-09-25T14:30:00Z",
                "customer": 1,
                "customer_name": "John Doe",
                "product": "660e8400-e29b-41d4-a716-446655440001",
                "product_name": "Smartphone XYZ",
                "shop_name": "Tech Store",
                "quantity": 2,
                "unit_price": "299.99",
                "total_amount": "599.98",
                "payment_status": "completed",
                "purchase_method": "card",
                "purchase_code": "PUR-550E8400",
                "created_at": "2025-09-25T14:30:00Z"
            }
        ],
        "purchase_count": 1,
        "total_spent": "599.98"
    }
}
```

### 10. Get Purchases by Product
- **URL:** `GET /api/purchases/by_product/`
- **Permission:** Authenticated
- **Description:** Get all purchases for a specific product

**Query Parameters:**
- `product_id`: Product ID (required)

**Response:**
```json
{
    "success": true,
    "message": "Purchases for product \"Smartphone XYZ\" retrieved successfully",
    "data": {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "name": "Smartphone XYZ",
        "shop": 1,
        "price": "299.99",
        "stock_quantity": 48,
        "purchases": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "date": "2025-09-25T14:30:00Z",
                "customer": 1,
                "customer_name": "John Doe",
                "product": "660e8400-e29b-41d4-a716-446655440001",
                "product_name": "Smartphone XYZ",
                "shop_name": "Tech Store",
                "quantity": 2,
                "unit_price": "299.99",
                "total_amount": "599.98",
                "payment_status": "completed",
                "purchase_method": "card",
                "purchase_code": "PUR-550E8400",
                "created_at": "2025-09-25T14:30:00Z"
            }
        ],
        "purchase_count": 1,
        "total_sold_quantity": 2,
        "total_revenue": "599.98"
    }
}
```

### 11. Bulk Create Purchases
- **URL:** `POST /api/purchases/bulk_create/`
- **Permission:** Authenticated
- **Description:** Create multiple purchases at once (max 50)

**Request Body:**
```json
{
    "purchases": [
        {
            "date": "2025-09-25T16:00:00Z",
            "product": "660e8400-e29b-41d4-a716-446655440001",
            "customer": 1,
            "quantity": 1,
            "unit_price": "299.99",
            "payment_status": "completed",
            "purchase_method": "cash"
        },
        {
            "date": "2025-09-25T16:30:00Z",
            "product": "770e8400-e29b-41d4-a716-446655440002",
            "customer": 2,
            "quantity": 3,
            "unit_price": "149.99",
            "payment_status": "pending",
            "purchase_method": "card"
        }
    ]
}
```

**Response:**
```json
{
    "success": true,
    "message": "2 purchases created successfully",
    "data": [
        {
            "id": "880e8400-e29b-41d4-a716-446655440003",
            "date": "2025-09-25T16:00:00Z",
            "customer": 1,
            "customer_name": "John Doe",
            "product": "660e8400-e29b-41d4-a716-446655440001",
            "product_name": "Smartphone XYZ",
            "shop_name": "Tech Store",
            "quantity": 1,
            "unit_price": "299.99",
            "total_amount": "299.99",
            "payment_status": "completed",
            "purchase_method": "cash",
            "purchase_code": "PUR-880E8400",
            "created_at": "2025-09-25T16:00:00Z"
        }
        // ... more purchases
    ]
}
```

### 12. Purchase Statistics
- **URL:** `GET /api/purchases/stats/`
- **Permission:** Authenticated
- **Description:** Get comprehensive purchase statistics

**Response:**
```json
{
    "success": true,
    "message": "Purchase statistics retrieved successfully",
    "data": {
        "total_purchases": 250,
        "completed_purchases": 200,
        "pending_purchases": 30,
        "failed_purchases": 15,
        "refunded_purchases": 5,
        "total_revenue": "125000.00",
        "average_purchase_amount": "625.00",
        "unique_customers": 85,
        "unique_products": 120,
        "purchases_today": 15,
        "revenue_today": "4500.00"
    }
}
```

### 13. Today's Purchases
- **URL:** `GET /api/purchases/today/`
- **Permission:** Authenticated
- **Description:** Get all purchases made today

**Response:**
```json
{
    "success": true,
    "message": "Today's purchases retrieved successfully",
    "data": {
        "date": "2025-09-25",
        "purchases": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "date": "2025-09-25T14:30:00Z",
                "customer": 1,
                "customer_name": "John Doe",
                "product": "660e8400-e29b-41d4-a716-446655440001",
                "product_name": "Smartphone XYZ",
                "shop_name": "Tech Store",
                "quantity": 2,
                "unit_price": "299.99",
                "total_amount": "599.98",
                "payment_status": "completed",
                "purchase_method": "card",
                "purchase_code": "PUR-550E8400",
                "created_at": "2025-09-25T14:30:00Z"
            }
        ],
        "count": 15
    }
}
```

### 14. Recent Purchases
- **URL:** `GET /api/purchases/recent/`
- **Permission:** Authenticated
- **Description:** Get recent purchases (last 7 days by default)

**Query Parameters:**
- `days`: Number of days to look back (default: 7)

**Response:**
```json
{
    "success": true,
    "message": "Recent purchases (last 7 days) retrieved successfully",
    "data": {
        "period": "Last 7 days",
        "start_date": "2025-09-18T15:00:00Z",
        "purchases": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "date": "2025-09-25T14:30:00Z",
                "customer": 1,
                "customer_name": "John Doe",
                "product": "660e8400-e29b-41d4-a716-446655440001",
                "product_name": "Smartphone XYZ",
                "shop_name": "Tech Store",
                "quantity": 2,
                "unit_price": "299.99",
                "total_amount": "599.98",
                "payment_status": "completed",
                "purchase_method": "card",
                "purchase_code": "PUR-550E8400",
                "created_at": "2025-09-25T14:30:00Z"
            }
        ],
        "count": 45
    }
}
```

---

## Data Models

### Purchase Model Fields
- **Required Fields:**
  - `product`: Foreign key to Product (cannot be changed after creation)
  - `customer`: Foreign key to Customer (cannot be changed after creation)
  - `unit_price`: Price per unit at time of purchase

- **Optional Fields:**
  - `date`: Purchase date/time (defaults to current time)
  - `quantity`: Quantity purchased (defaults to 1)
  - `payment_status`: Payment status (defaults to 'pending')
  - `purchase_method`: Method of payment (defaults to 'cash')
  - `notes`: Additional notes about the purchase
  - `is_active`: Active status (defaults to true)

- **Auto-generated Fields:**
  - `id`: UUID primary key
  - `total_amount`: Auto-calculated (quantity × unit_price)
  - `created_at`: Creation timestamp
  - `updated_at`: Last update timestamp

### Purchase Computed Properties
- `purchase_code`: Human-readable code (PUR-{first8chars})
- `customer_info`: Dictionary with customer information
- `product_info`: Dictionary with product information
- `shop_info`: Dictionary with shop information (through product)
- `purchase_summary`: Complete purchase summary dictionary

---

## Payment Status Options

- **pending** - Payment is pending (default)
- **completed** - Payment completed successfully
- **failed** - Payment failed
- **refunded** - Payment was refunded

## Purchase Method Options

- **cash** - Cash payment (default)
- **card** - Card payment (credit/debit)
- **bank_transfer** - Bank transfer
- **mobile_payment** - Mobile payment (e.g., mobile banking)
- **credit** - Credit/on account

---

## Data Validation

### Purchase Validation Rules
- Product must be active to create purchase
- Customer must be active to create purchase
- Quantity must be greater than 0
- Unit price must be greater than 0
- Product must have sufficient stock for the quantity
- Cannot change product or customer after creation

### Business Rules
- Creating a purchase reduces product stock by the quantity
- Updating purchase quantity adjusts product stock accordingly
- Deleting a purchase restores product stock
- Total amount is automatically calculated (quantity × unit_price)
- If no unit_price provided, uses current product price

### Stock Management
- **Purchase Creation**: Reduces product stock by purchase quantity
- **Purchase Update**: Adjusts product stock based on quantity change
- **Purchase Deletion**: Restores product stock by purchase quantity
- **Stock Validation**: Ensures sufficient stock before allowing purchase

---

## Error Responses

All endpoints return consistent error responses:

```json
{
    "success": false,
    "message": "Error description",
    "errors": {
        "field_name": ["Error message for this field"]
    }
}
```

Common error scenarios:
- **400 Bad Request**: Invalid data, insufficient stock, validation errors
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Permission denied
- **404 Not Found**: Purchase, product, customer, or related resource not found
- **500 Internal Server Error**: Server error

---

## Relationships

### Database Relationships
- **Purchase → Product:** Many-to-One (FK with CASCADE delete)
- **Purchase → Customer:** Many-to-One (FK with CASCADE delete)
- **Product → Purchase:** One-to-Many (related_name='purchases')
- **Customer → Purchase:** One-to-Many (related_name='purchases')

### API Relationships
- Purchases include product and customer information
- Customer endpoints can include purchase history
- Product endpoints can include purchase statistics
- Shop information available through product relationship

---

## Performance Considerations

### Optimizations
- Uses `select_related()` for product and customer data
- Database indexes on frequently filtered fields (date, customer, product, payment_status)
- Pagination for large result sets
- Separate serializers for list vs detail views

### Bulk Operations
- Bulk create supports up to 50 purchases per request
- Bulk operations include validation and error reporting
- Automatic stock updates for all purchases in bulk operations

---

## HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Purchase created successfully
- `204 No Content` - Purchase deleted successfully
- `207 Multi-Status` - Bulk operation with some errors
- `400 Bad Request` - Invalid request data, insufficient stock, or validation errors
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Purchase, product, customer, or related resource not found
- `500 Internal Server Error` - Server error