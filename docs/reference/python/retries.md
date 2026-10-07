# Retries

[← Python reference](README.md) · [Python SDK guide](../../10-sdk-python.md) · Official: <https://docs.typesafe.ai/sdk/python/api/retries>


> Configure retries with RetryPolicy — attempt count, retryable statuses, backoff, and retry headers handling.

<a id="retries"></a>

<a id="typesafe_sdk.RetryPolicy"></a>

## `typesafe_sdk.RetryPolicy`

`dataclass`

```python
RetryPolicy(
    max_retries: int = 2,
    backoff_initial: float = 0.5,
    backoff_max: float = 5.0,
    backoff_jitter: float = 0.25,
    http_statuses: set[int] = (
        lambda: {408, 429, *range(500, 600)}
    )(),
    respect_retry_after: bool = True,
    api_connection_error: bool = True,
    api_timeout_error: bool = True,
    exceptions: set[
        type[BaseException]
    ] = set(),
    predicate: Callable[[BaseException], bool]
    | None = None,
    timeout: float | None = 30.0,
)
```

Configuration for SDK retry behavior.

Examples:

```python
from typesafe_sdk import RetryPolicy, TypeSafeClient

client = TypeSafeClient(
    retry=RetryPolicy(
        max_retries=3, timeout=10.0, http_statuses={429, 500, 502, 503, 504}
    )
)
```

<a id="typesafe_sdk.RetryPolicy.max_retries"></a>

### `max_retries`

`class-attribute` `instance-attribute`

```python
max_retries: int = 2
```

Maximum retries after the initial attempt; `0` disables retries.

<a id="typesafe_sdk.RetryPolicy.backoff_initial"></a>

### `backoff_initial`

`class-attribute` `instance-attribute`

```python
backoff_initial: float = 0.5
```

First backoff delay in seconds, doubled each attempt up to `backoff_max`; zero disables backoff.

<a id="typesafe_sdk.RetryPolicy.backoff_max"></a>

### `backoff_max`

`class-attribute` `instance-attribute`

```python
backoff_max: float = 5.0
```

Maximum backoff delay in seconds; zero disables backoff.

<a id="typesafe_sdk.RetryPolicy.backoff_jitter"></a>

### `backoff_jitter`

`class-attribute` `instance-attribute`

```python
backoff_jitter: float = 0.25
```

Fraction of each backoff delay randomly subtracted, between 0 and 1.

<a id="typesafe_sdk.RetryPolicy.http_statuses"></a>

### `http_statuses`

`class-attribute` `instance-attribute`

```python
http_statuses: set[int] = field(
    default_factory=lambda: {
        408,
        429,
        *range(500, 600),
    }
)
```

HTTP status codes that are retried.

<a id="typesafe_sdk.RetryPolicy.respect_retry_after"></a>

### `respect_retry_after`

`class-attribute` `instance-attribute`

```python
respect_retry_after: bool = True
```

Whether to honor `Retry-After` and `retry-after-ms` response headers.

<a id="typesafe_sdk.RetryPolicy.api_connection_error"></a>

### `api_connection_error`

`class-attribute` `instance-attribute`

```python
api_connection_error: bool = True
```

Whether to retry `TypeSafeAPIConnectionError`, raised when the request cannot reach or read from the server.

<a id="typesafe_sdk.RetryPolicy.api_timeout_error"></a>

### `api_timeout_error`

`class-attribute` `instance-attribute`

```python
api_timeout_error: bool = True
```

Whether to retry `TypeSafeAPITimeoutError`, raised when the request exceeds its timeout.

<a id="typesafe_sdk.RetryPolicy.exceptions"></a>

### `exceptions`

`class-attribute` `instance-attribute`

```python
exceptions: set[type[BaseException]] = field(
    default_factory=set
)
```

Additional exception types that trigger a retry, on top of the built-in rules.

<a id="typesafe_sdk.RetryPolicy.predicate"></a>

### `predicate`

`class-attribute` `instance-attribute`

```python
predicate: (
    Callable[[BaseException], bool] | None
) = None
```

An optional predicate called with the raised exception; returning `True` triggers a retry in addition to the other rules.

<a id="typesafe_sdk.RetryPolicy.timeout"></a>

### `timeout`

`class-attribute` `instance-attribute`

```python
timeout: float | None = 30.0
```

Total retry budget in seconds per SDK call, including the initial attempt and delays; `None` disables the limit.

Stops before a retry whose delay would reach or exceed the budget, re-raising the last error.
