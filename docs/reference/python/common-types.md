# Common types

[← Python reference](README.md) · [Python SDK guide](../../10-sdk-python.md) · Official: <https://docs.typesafe.ai/sdk/python/api/types/common>


> Common types for TypeSafe API SDK.

<a id="common-types"></a>

<a id="typesafe_sdk.JSONValue"></a>

## `typesafe_sdk.JSONValue`

`module-attribute`

```python
JSONValue = TypeAliasType(
    "JSONValue",
    "str | int | float | bool | Sequence[JSONValue | None] | Mapping[str, JSONValue | None]",
)
```

A JSON-like value. May be nested and contain `None`.

<a id="typesafe_sdk.JSONContent"></a>

## `typesafe_sdk.JSONContent`

`module-attribute`

```python
JSONContent = TypeAliasType(
    "JSONContent",
    "str | Mapping[str, JSONValue | None] | Sequence[JSONValue | None]",
)
```

Either a plain string or a mapping/sequence of [`JSONValue`](#typesafe_sdk.JSONValue) entries.
