# Classification Taxonomy

This document defines the first version of support ticket categories and confidence handling.

The classifier returns a structured `TicketClassification` object with:

- `category`
- `confidence`
- `reasoning`

## Categories

### `billing`

Use this category when the user asks about payments, invoices, receipts, taxes, or charges.

Examples:

- "Where can I find my invoice?"
- "I was charged twice."
- "Can I get a receipt for my last payment?"

Initial routing expectation:

- Usually needs review when money movement or account-specific billing changes are requested.
- May be safe for auto-reply when the user only asks for general billing instructions.

### `refund`

Use this category when the user asks for money back, refund review, chargebacks, duplicate charges, or accidental renewal correction.

Examples:

- "I want a refund for my last payment."
- "Can I get my money back?"
- "I was charged twice and need a refund."

Initial routing expectation:

- Treat as high risk.
- Prepare a grounded draft, but route to human review before promising or issuing a refund.

### `account`

Use this category when the user asks about account deletion, identity-sensitive account changes, data removal, or closing an account.

Examples:

- "Please delete my account."
- "Remove all of my personal data."
- "How do I close my account?"

Initial routing expectation:

- Treat direct account actions as high risk.
- General instructions may be drafted automatically, but final account actions need human review or a verified workflow.

### `technical`

Use this category when the user asks about API behavior, errors, integrations, bugs, timeouts, or rate limits.

Examples:

- "Why does your API return rate limit errors?"
- "My integration times out."
- "I get an error when calling the API."

Initial routing expectation:

- Usually safe for auto-reply when the answer is grounded in retrieved documentation.
- Route to review when the question needs account-specific debugging or undocumented behavior.

### `pricing`

Use this category when the user asks about plans, prices, upgrades, downgrades, or differences between tiers.

Examples:

- "What is the difference between Pro and Team?"
- "How much does the Pro plan cost?"
- "Can I downgrade at the end of the month?"

Initial routing expectation:

- Usually safe for auto-reply when relevant pricing documentation is retrieved.
- Route to review if the user asks for custom discounts, exceptions, or account-specific commitments.

### `other`

Use this category when no category has a clear signal or when the ticket is ambiguous.

Examples:

- "Can you help me with something unusual?"
- "I have a custom enterprise exception from last year."
- "I need help but I am not sure what is wrong."

Initial routing expectation:

- Usually requires human review or a request for more information.
- Avoid confident answers when the category is unclear.

## Confidence Handling

`confidence` is a float from `0.0` to `1.0`.

Initial interpretation:

- `0.00` to `0.49`: low confidence
- `0.50` to `0.79`: medium confidence
- `0.80` to `1.00`: high confidence

The current local classifier is keyword-based:

- no keyword matches returns `other` with low confidence;
- one keyword match returns medium confidence;
- multiple keyword matches increase confidence;
- confidence is capped below full certainty.

## Routing Guidelines

Classification is not the final safety decision. It is an input into risk assessment.

Risk assessment should also consider:

- retrieved context quality;
- whether the requested action is sensitive;
- whether the answer would make an account-specific promise;
- whether the draft response is sufficiently grounded.

Recommended first-pass routing:

- `pricing` with high confidence and good retrieval context -> auto-send candidate
- `technical` with high confidence and good retrieval context -> auto-send candidate
- `refund` -> human review
- `account` with direct action request -> human review
- `billing` with money movement or account-specific action -> human review
- `other` -> human review or request more information

## Example Classifications

| Ticket message | Category | Expected confidence | Reason |
| --- | --- | --- | --- |
| "I want a refund for the last payment." | `refund` | medium | Refund keyword signal |
| "Why does your API return rate limit errors?" | `technical` | high | API, error, and rate limit signals |
| "Can you explain the Pro and Team plans?" | `pricing` | high | Plan and tier-name signals |
| "Please delete my account immediately." | `account` | medium | Account deletion signal |
| "Where can I find my invoice?" | `billing` | medium | Invoice keyword signal |
| "Can you help with something unusual?" | `other` | low | No clear category signal |
