# Changelog

[← Python reference](README.md) · [Python SDK guide](../../10-sdk-python.md) · Official: <https://docs.typesafe.ai/sdk/python/changelog>


> Python clients for the TypeSafe AI API

<a id="changelog"></a>

<a id="v072-2026-09-26"></a>

## v0.7.2 (2026-09-26)

<a id="miscellaneous"></a>

### `Miscellaneous`

* add `http2` extra to `typesafe-sdk` package

<a id="documentation"></a>

### `Documentation`

* document `typesafe-sdk` usage with HTTP/2 support

<a id="v071-2026-09-21"></a>

## v0.7.1 (2026-09-21)

<a id="bug-fixes"></a>

### Bug fixes

* validate the API key early and exclude the value from logged exceptions

<a id="documentation_1"></a>

### `Documentation`

* add examples for usage with AI gateways

<a id="v070-2026-09-18"></a>

## v0.7.0 (2026-09-18)

<a id="breaking-changes"></a>

### Breaking Changes

* ser/de library has been changed from `msgspec` to `pydantic`

<a id="bug-fixes_1"></a>

### Bug fixes

* `str` subclasses are now correctly serialized as strings instead of lists of characters

<a id="features"></a>

### `Features`

* the `system_one` method now accepts a new `response_model` argument that can be set to a desired `pydantic` model for additional *type-safety*

<a id="v060-2026-09-15"></a>

## v0.6.0 (2026-09-15)

<a id="breaking-changes_1"></a>

### Breaking Changes

* accept `Score.criteria` as an ordered sequence instead of a dictionary keyed by integers

<a id="features_1"></a>

### `Features`

* improve type annotations on SDK inputs to accept abstract types like `Mapping` and `Sequence`
* improve error messages to include http details and metadata

<a id="bug-fixes_2"></a>

### Bug fixes

* handle invalid values in `RetryPolicy`
* make exceptions and responses picklable

<a id="documentation_2"></a>

### `Documentation`

* link more concepts from main [docs](https://docs.typesafe.ai/)

<a id="v057-2026-09-14"></a>

## v0.5.7 (2026-09-14)

This is the initial public release of TypeSafe Python SDK. Learn more in the [documentation](https://docs.typesafe.ai/sdk/python).
