# Payment Gateway API Documentation

## Overview
This module handles subscription management with manual payment verification for the Kabadi Techno marketplace. It supports trial subscriptions and paid subscriptions (3-month, 6-month, and 1-year plans) with NEFT/QR code payment methods.

## Features
- ✅ Multiple subscription plans (Trial, 3M, 6M, 1Y)
- ✅ Manual payment verification system
- ✅ NEFT and QR code payment support
- ✅ Admin panel for payment verification
- ✅ Automatic subscription status management
- ✅ Payment screenshot upload
- ✅ Bank details API for frontend display

## API Endpoints

### 1. Get Subscription Plans
**GET** `/api/subscription/plans/`

Returns all available subscription plans.

**Response:**
```json
[
  {
    "id": 1,
    "plan_type": "trial",
    "name": "1 Month Free Trial",
    "duration_days": 30,
    "price": "0.00",
    "description": "Free trial for 1 month"
  },
  {
    "id": 2,
    "plan_type": "3_month", 
    "name": "3 Month Plan",
    "duration_days": 90,
    "price": "999.00",
    "description": "3 months access to marketplace"
  }
]
```

### 2. Create Subscription
**POST** `/api/subscription/subscription/`

Create a new subscription for authenticated dealer.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "plan_id": 2
}
```

**Response:**
```json
{
  "message": "Subscription created successfully. Please submit payment details to activate.",
  "subscription": {
    "id": 123,
    "plan_name": "3 Month Plan",
    "status": "pending",
    "start_date": "2025-08-04T10:30:00Z",
    "end_date": "2025-11-02T10:30:00Z"
  },
  "next_step": "submit_payment"
}
```

### 3. Submit Payment Details
**POST** `/api/subscription/submit-payment/`

Submit payment details after making NEFT transfer or QR payment.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
```
subscription: 123
transaction_id: "TXN202508041030"
amount: 999.00
payment_method: "neft" // or "qr_code"
payment_screenshot: <file> // Optional image file
```

**Response:**
```json
{
  "message": "Payment details submitted successfully. Awaiting admin verification.",
  "payment_transaction": {
    "id": 456,
    "transaction_id": "TXN202508041030",
    "amount": "999.00",
    "payment_method": "neft",
    "verified": false,
    "created_at": "2025-08-04T10:35:00Z"
  },
  "status": "pending_verification"
}
```

### 4. Get Bank Details
**GET** `/api/subscription/bank-details/`

Get company bank account details for NEFT transfer and QR code.

**Response:**
```json
{
  "account_name": "Kabadi Techno Pvt Ltd",
  "account_number": "123456789012",
  "ifsc_code": "HDFC0001234",
  "bank_name": "HDFC Bank",
  "branch_name": "Electronic City Branch",
  "qr_code_url": "/media/static_qr/payment_qr.png"
}
```

### 5. Check Payment Status
**GET** `/api/subscription/payment-status/<subscription_id>/`

Check payment verification status for a subscription.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "payment_submitted": true,
  "payment_verified": false,
  "subscription_status": "pending",
  "payment_details": {
    "transaction_id": "TXN202508041030",
    "amount": "999.00",
    "payment_method": "neft",
    "verified": false,
    "created_at": "2025-08-04T10:35:00Z"
  }
}
```

### 6. Check Marketplace Access
**GET** `/api/subscription/access/check/`

Check if dealer has active marketplace access.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (Active):**
```json
{
  "access_granted": true,
  "subscription_type": "3_month",
  "days_remaining": 85,
  "expires_on": "2025-11-02T10:30:00Z"
}
```

**Response (No Access):**
```json
{
  "access_granted": false,
  "message": "Your subscription has expired. Please renew to access the marketplace.",
  "available_plans_url": "/api/subscription/plans/"
}
```

### 7. Get Subscription History
**GET** `/api/subscription/subscription/history/`

Get dealer's subscription history.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 123,
    "plan_name": "3 Month Plan",
    "status": "active",
    "start_date": "2025-08-04T10:30:00Z",
    "end_date": "2025-11-02T10:30:00Z",
    "days_remaining": 85,
    "is_trial": false
  }
]
```

## Admin Endpoints

### 8. Verify Payment (Admin Only)
**POST** `/api/subscription/verify-payment/<payment_id>/`

Admin endpoint to verify or reject payment.

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Request Body:**
```json
{
  "action": "approve", // or "reject"
  "notes": "Payment verified successfully"
}
```

**Response:**
```json
{
  "message": "Payment verified and subscription activated successfully",
  "subscription_id": 123,
  "status": "active"
}
```

## Payment Flow

### For Paid Subscriptions:

1. **Select Plan**: User calls `/plans/` to see available plans
2. **Create Subscription**: User calls `/subscription/` with `plan_id` 
   - Status becomes `pending`
3. **Get Bank Details**: User calls `/bank-details/` to get payment info
4. **Make Payment**: User transfers money via NEFT or scans QR code
5. **Submit Details**: User calls `/submit-payment/` with transaction details
6. **Admin Verification**: Admin reviews and approves/rejects via admin panel
7. **Activation**: Upon approval, subscription status becomes `active`

### For Trial Subscriptions:

1. **Select Trial**: User calls `/subscription/` with trial `plan_id`
2. **Immediate Activation**: Status becomes `active` immediately

## Database Models

### PaymentTransaction
Stores user-submitted payment details:
- `subscription` - ForeignKey to DealerSubscription
- `transaction_id` - User provided transaction ID
- `amount` - Payment amount
- `payment_method` - 'neft' or 'qr_code'
- `payment_screenshot` - Optional uploaded image
- `verified` - Boolean for admin verification
- `verified_by` - Admin username who verified
- `verified_at` - Verification timestamp

### BankDetails
Stores company bank account information:
- `account_name` - Company account name
- `account_number` - Bank account number
- `ifsc_code` - IFSC code
- `bank_name` - Bank name
- `qr_code_image` - QR code image for payments

## Setup Instructions

1. **Run Migrations:**
```bash
python manage.py makemigrations payment_gateway
python manage.py migrate
```

2. **Load Initial Data:**
```bash
python manage.py loaddata payment_gateway/fixtures/initial_data.json
```

3. **Create Bank Details:**
- Login to admin panel
- Go to Payment Gateway > Bank Details
- Add your company's bank account details
- Upload QR code image if needed

4. **Setup Periodic Tasks:**
```bash
# Run this command daily to update subscription statuses
python manage.py update_subscriptions
```

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error

Error responses include detailed error messages:
```json
{
  "error": "Dealer profile not found"
}
```

## Security Considerations

- All endpoints (except bank details) require authentication
- Payment verification should only be accessible to admin users
- File uploads are validated and stored securely
- Transaction IDs should be unique per payment

## Testing

Use the provided fixtures to test the system:
1. Create a dealer account
2. Load initial subscription plans
3. Test the complete payment flow
4. Verify admin functionality
