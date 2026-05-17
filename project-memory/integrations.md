# AI CFO - Integrations

## Connector Policy
- Integrations are read-only by default.
- Provider implementations must stay isolated behind `BaseConnector`.
- Stripe is not a locked business dependency; it is one replaceable provider.
- Real provider access may be unavailable during development, so validation uses test-only mocks where needed.
- No mock provider is exposed in production API contracts.

## Stripe
- **Status**: Implemented as a Stage 1 connector skeleton
- **SDK**: stripe 11.4.1
- **Auth**: API key
- **Permissions**: Read-only default
- **Data**: Charges and refunds
- **Normalization**: charge -> revenue, refund -> negative refund record, failed charges skipped
- **Sync**: Every 6h through Celery, with shared upsert service
- **Validation**: Test-only mocked Stripe E2E is complete; real Stripe validation pending approval/access

## Plaid
- **Status**: Implemented as a Stage 1 connector skeleton
- **Auth**: Access token + client ID + secret
- **Data**: Bank transactions
- **Normalization**: Plaid positive debit -> negative outflow
- **Sync**: Every 6h through Celery, with shared upsert service

## Future / Alternative Providers
- QuickBooks - Stage 3 planned
- Xero - Stage 3 planned
- Razorpay - Stage 3 planned
- Chargebee, Paddle, Razorpay, or other billing alternatives may replace or complement Stripe based on launch market constraints

