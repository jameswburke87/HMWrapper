# Rate Limiting

## Known Constraints

HallMaster enforces server-side rate limiting. The exact limits are not documented, but from observation:

- **Concurrent requests:** Keep to 2-3 simultaneous requests
- **Burst behaviour:** Rapid sequential requests may trigger 429 responses
- **Session limits:** Excessive requests may invalidate the session

## Recommended Practices

1. **Reuse sessions** — Avoid logging in on every request. Use session persistence.
2. **Add delays** — When making bulk requests, add a small delay between them.
3. **Retry with backoff** — HMWrapper's client includes automatic retry with exponential backoff for 429 and 5xx responses.
4. **Cache where possible** — Room lists, activity types, and price rates rarely change. Cache these locally.

## HMWrapper Retry Behaviour

The `HallmasterClient` retries automatically on:

- **429 (Too Many Requests)** — Retries up to `max_retries` times with exponential backoff
- **5xx (Server Error)** — Same retry behaviour
- **Connection errors** — Retries on network failures

Configure via constructor:

```python
client = HallmasterClient(
    max_retries=5,        # default: 3
    retry_backoff=2.0,    # default: 1.0 seconds (doubles each retry)
)
```
