# Free Trial Restriction Implementation

## Overview
This implementation ensures that dealers can only use the free trial subscription once. After using the free trial, dealers must choose paid subscription plans for any future subscriptions or renewals.

## Changes Made

### 1. Views.py Changes

#### New Utility Function
- `check_trial_eligibility(dealer)`: Checks if a dealer is eligible for free trial
- `check_trial_eligibility_view()`: API endpoint to check trial eligibility

#### Modified Endpoints

##### SubscriptionPlanListView.get()
- Now includes `trial_already_used` and `available` flags for each plan
- Helps frontend determine which plans to show/enable for the user

##### DealerSubscriptionView.post()
- Added validation to prevent dealers from selecting trial plan if already used
- Returns clear error message with redirect guidance

##### renew_subscription()
- Added same trial validation for subscription renewals
- Prevents dealers from using trial during renewal process

### 2. URLs.py Changes
- Added new endpoint: `trial/eligibility/` for checking trial eligibility

## API Endpoints

### Check Trial Eligibility
```
GET /api/payment/trial/eligibility/
```
**Authentication Required**: Yes

**Response**:
```json
{
    "trial_eligible": true/false,
    "message": "You are eligible for free trial" or "You have already used your one-time free trial",
    "previous_trial": {  // Only if trial was used before
        "start_date": "2024-01-01T00:00:00Z",
        "end_date": "2024-01-31T23:59:59Z",
        "status": "expired"
    }
}
```

### Get Subscription Plans
```
GET /api/payment/plans/
```
**Authentication Required**: No (but enhanced response when authenticated)

**Enhanced Response** (when authenticated):
```json
[
    {
        "id": 1,
        "plan_type": "trial",
        "name": "1 Month Free Trial",
        "duration_days": 30,
        "price": "0.00",
        "description": "Free trial for new users",
        "trial_already_used": false,
        "available": true
    },
    {
        "id": 2,
        "plan_type": "3_month",
        "name": "3 Month Plan",
        "duration_days": 90,
        "price": "500.00",
        "description": "3 month subscription",
        "available": true
    }
]
```

### Create Subscription
```
POST /api/payment/subscription/
```
**Authentication Required**: Yes

**Error Response** (when trial already used):
```json
{
    "error": "Free trial can only be used once. Please choose a paid subscription plan.",
    "message": "You have already used your one-time free trial period. Please select from our paid subscription plans to continue.",
    "redirect_to_paid_plans": true
}
```

### Renew Subscription
```
POST /api/payment/subscription/renew/
```
**Authentication Required**: Yes

**Error Response** (when trying to renew with trial):
```json
{
    "error": "Free trial can only be used once. Please choose a paid subscription plan.",
    "message": "You have already used your one-time free trial period. Please select from our paid subscription plans to renew.",
    "redirect_to_paid_plans": true
}
```

## Frontend Integration Guidelines

### 1. Plan Selection UI
- Use the `available` flag to disable/grey out unavailable plans
- Show appropriate message for trial plans when `trial_already_used` is true
- Hide trial option completely for users who have already used it

### 2. Error Handling
- Watch for `redirect_to_paid_plans: true` in error responses
- Redirect users to paid plans section when this flag is present
- Display the error message to inform users why trial is not available

### 3. User Experience
- Consider showing a badge/indicator on trial plans like "New Users Only"
- Provide clear messaging about trial being a one-time offer
- Guide users to paid plans with better value propositions

## Database Schema Impact
No changes to database schema were required. The implementation uses existing models:
- `DealerSubscription.plan.plan_type` to identify trial subscriptions
- Existing relationships to track subscription history per dealer

## Testing Scenarios

1. **New Dealer**: Should be able to select trial plan
2. **Dealer with Previous Trial**: Should be blocked from selecting trial
3. **Dealer Renewal**: Should be blocked from renewing with trial if previously used
4. **Plan List API**: Should show appropriate availability flags
5. **Trial Eligibility Check**: Should return correct status

## Security Considerations
- All endpoints are properly authenticated
- No bypass mechanisms for trial restrictions
- Server-side validation prevents trial abuse
- Clear audit trail through existing subscription history
