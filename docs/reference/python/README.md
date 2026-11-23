# Python SDK API reference

[← Python SDK guide](../../10-sdk-python.md) · [README](../../../README.md) · Official: <https://docs.typesafe.ai/sdk/python/api> · Source: <https://github.com/typesafe-ai/typesafe-sdk-python>

This is the complete, generated API reference for `typesafe-sdk`, converted from the official docs: every class, method signature, parameter, return type, and exception.

| Page | What's inside |
|---|---|
| [Usage: basic](usage-basic.md) | Sync and async calls, models, images (`Image`, `attach_assets`, named `assets`), typed responses, retries, errors, env vars, base URL |
| [Usage: advanced](usage-advanced.md) | Performance (zstd, aiohttp, client per thread, HTTP/2, connection limits), logging, forward compatibility |
| [Synchronous client](sync-client.md) | `TypeSafeClient`: constructor, `system_one` (plus overloads), `models.list()`, `close` and context manager |
| [Asynchronous client](async-client.md) | `AsyncTypeSafeClient`: the same surface, `async` |
| [Questions](questions.md) | `Noul`, `NoulCriteria`, `Choice`, `Score`, `Box`, `Question` |
| [Answers and responses](responses.md) | `SystemOneResponse`, `NoulAnswer`, `ChoiceAnswer`, `ScoreAnswer`, `BoxAnswer`, `BoxCoordinates`, `Usage`, `ModelCard` |
| [Assets](assets.md) | `Image` (from a path, bytes, base64, or Pillow) and `Asset` |
| [Common types](common-types.md) | `JSONValue`, `JSONContent` |
| [Retries](retries.md) | `RetryPolicy` and every field's default |
| [Exceptions](exceptions.md) | `TypeSafeError` hierarchy, from HTTP and connection errors to response validation |
| [Constants](constants.md) | Environment variable names and defaults |
| [Changelog](changelog.md) | Release notes |
