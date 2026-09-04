# API Rate Limits

## Overview

Rate limits help protect system stability and ensure fair access across users.

## Common Causes of Rate Limit Errors

- too many requests in a short time window;
- too many concurrent requests;
- bursts that exceed per-minute or per-second thresholds;
- account-level limits based on the current plan.

## Recommended Troubleshooting

- retry with exponential backoff;
- reduce request concurrency;
- smooth burst traffic;
- inspect whether the workload fits the current plan limits.

## Support Guidance

- Technical support responses may explain rate limiting at a high level.
- The system may suggest backoff, queuing, and concurrency controls.
- If a customer asks whether their plan has enough capacity, the response may reference pricing or plan documentation.

## Safe Auto-Reply Cases

Rate-limit questions are usually safe for automated responses when:

- relevant documentation was retrieved successfully;
- the answer stays within documented behavior;
- the response does not promise account-specific changes or exceptions.
