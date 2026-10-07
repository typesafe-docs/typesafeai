# JavaScript SDK reference: Variables

[← JavaScript reference](README.md) · [JS SDK guide](../../11-sdk-javascript.md) · Official: <https://docs.typesafe.ai/sdk/javascript/api>

- [ENV](#variable-env)
- [LOG_LEVELS](#variable-log_levels)
- [VERSION](#variable-version)


---

## Variable: ENV

```ts
const ENV: object;
```

Environment variable names for client configuration. Explicit options take precedence.

### Type Declaration

<a id="sdk-apikey"></a>

#### apiKey

```ts
readonly apiKey: "TYPESAFE_API_KEY" = "TYPESAFE_API_KEY";
```

Required API key; used when `apiKey` is omitted.

<a id="sdk-baseurl"></a>

#### baseURL

```ts
readonly baseURL: "TYPESAFE_BASE_URL" = "TYPESAFE_BASE_URL";
```

API root; defaults to `https://api.typesafe.ai`.

<a id="sdk-defaultmodel"></a>

#### defaultModel

```ts
readonly defaultModel: "TYPESAFE_DEFAULT_MODEL" = "TYPESAFE_DEFAULT_MODEL";
```

Default model name; defaults to `jev-latest`.

<a id="sdk-loglevel"></a>

#### logLevel

```ts
readonly logLevel: "TYPESAFE_LOG_LEVEL" = "TYPESAFE_LOG_LEVEL";
```

Log level; defaults to `warn`.



---

## Variable: LOG_LEVELS

```ts
const LOG_LEVELS: readonly LogLevel[];
```

Supported log levels, from most to least verbose.



---

## Variable: VERSION

```ts
const VERSION: "0.6.0" = "0.6.0";
```
