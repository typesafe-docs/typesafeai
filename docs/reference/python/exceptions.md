# Exceptions

[← Python reference](README.md) · [Python SDK guide](../../10-sdk-python.md) · Official: <https://docs.typesafe.ai/sdk/python/api/exceptions>


> Handle TypeSafe API errors, rate limits, connection failures, and timeouts.

<a id="exceptions"></a>

<a id="base-exception"></a>

## Base exception

<a id="typesafe_sdk.TypeSafeError"></a>

## `typesafe_sdk.TypeSafeError`

Bases: `Exception`

Base exception for SDK failures.

<a id="http-errors"></a>

## HTTP errors

<a id="typesafe_sdk.TypeSafeAPIError"></a>

## `typesafe_sdk.TypeSafeAPIError`

Bases: `TypeSafeError`

An unsuccessful HTTP response with its body and request metadata.

<a id="typesafe_sdk.TypeSafeAPIError.status"></a>

### `status`

`instance-attribute`

```python
status = status
```

HTTP response status code.

<a id="typesafe_sdk.TypeSafeAPIError.body"></a>

### `body`

`instance-attribute`

```python
body = body
```

The server's JSON error body, plain response text, or `None` for an empty body.

<a id="typesafe_sdk.TypeSafeAPIError.headers"></a>

### `headers`

`instance-attribute`

```python
headers = headers
```

HTTP response headers.

<a id="typesafe_sdk.TypeSafeAPIError.endpoint"></a>

### `endpoint`

`instance-attribute`

```python
endpoint = endpoint
```

The request method and URL, without credentials, query parameters, or fragment, when available.

<a id="typesafe_sdk.TypeSafeAPIError.request_id"></a>

### `request_id`

`property`

```python
request_id: str | None
```

The `x-typesafe-request-id` response header, or `None` if absent.

<a id="typesafe_sdk.TypeSafeBadRequestError"></a>

## `typesafe_sdk.TypeSafeBadRequestError`

Bases: `TypeSafeAPIError`

The request was invalid (400).

<a id="typesafe_sdk.TypeSafeAuthenticationError"></a>

## `typesafe_sdk.TypeSafeAuthenticationError`

Bases: `TypeSafeAPIError`

Authentication failed (401).

<a id="typesafe_sdk.TypeSafePermissionDeniedError"></a>

## `typesafe_sdk.TypeSafePermissionDeniedError`

Bases: `TypeSafeAPIError`

Access was denied (403).

<a id="typesafe_sdk.TypeSafeNotFoundError"></a>

## `typesafe_sdk.TypeSafeNotFoundError`

Bases: `TypeSafeAPIError`

The resource was not found (404).

<a id="typesafe_sdk.TypeSafeUnprocessableEntityError"></a>

## `typesafe_sdk.TypeSafeUnprocessableEntityError`

Bases: `TypeSafeAPIError`

The request failed server validation (422).

<a id="typesafe_sdk.TypeSafeRateLimitError"></a>

## `typesafe_sdk.TypeSafeRateLimitError`

Bases: `TypeSafeAPIError`

The rate limit was exceeded (429).

<a id="typesafe_sdk.TypeSafeRateLimitError.retry_after_ms"></a>

### `retry_after_ms`

`instance-attribute`

```python
retry_after_ms = parse_retry_after(headers)
```

The server's requested wait in milliseconds, or `None` if unavailable.

<a id="typesafe_sdk.TypeSafeInternalServerError"></a>

## `typesafe_sdk.TypeSafeInternalServerError`

Bases: `TypeSafeAPIError`

The server failed to process the request (5xx).

<a id="connection-errors"></a>

## Connection errors

<a id="typesafe_sdk.TypeSafeAPIConnectionError"></a>

## `typesafe_sdk.TypeSafeAPIConnectionError`

Bases: `TypeSafeError`, `ConnectionError`

A request failed without an HTTP response.

<a id="typesafe_sdk.TypeSafeAPITimeoutError"></a>

## `typesafe_sdk.TypeSafeAPITimeoutError`

Bases: `TypeSafeAPIConnectionError`, `TimeoutError`

A request exceeded its configured timeout.

<a id="typesafe_sdk.TypeSafeAPITimeoutError.timeout"></a>

### `timeout`

`instance-attribute`

```python
timeout = timeout
```

The timeout setting used for the request, in seconds or as an `httpx2.Timeout`.

<a id="response-validation"></a>

## Response validation

<a id="typesafe_sdk.TypeSafeAPIResponseValidationError"></a>

## `typesafe_sdk.TypeSafeAPIResponseValidationError`

Bases: `TypeSafeAPIError`

A successful HTTP response whose body was missing or structurally invalid required data.

<a id="typesafe_sdk.TypeSafeAPIResponseValidationError.field_path"></a>

### `field_path`

`instance-attribute`

```python
field_path = field_path
```

Dotted path to the offending field, such as `answers.tone.confidence`.

<a id="typesafe_sdk.TypeSafeAPIResponseValidationError.args"></a>

### `args`

`instance-attribute`

```python
args = (
    status,
    body,
    headers,
    field_path,
    endpoint,
)
```
