# JavaScript SDK reference: Type Aliases

[← JavaScript reference](README.md) · [JS SDK guide](../../11-sdk-javascript.md) · Official: <https://docs.typesafe.ai/sdk/javascript/api>

- [ChoiceCriteria](#type-alias-choicecriteria)
- [Description](#type-alias-description)
- [EntryType](#type-alias-entrytype)
- [EnvVar](#type-alias-envvar)
- [Fetch](#type-alias-fetch)
- [JsonValue](#type-alias-jsonvalue)
- [LogLevel](#type-alias-loglevel)
- [Question](#type-alias-question)
- [ResultFor](#type-alias-resultfor)
- [ScoreCriteria](#type-alias-scorecriteria)
- [ScoreLegend](#type-alias-scorelegend)
- [ScoreOf](#type-alias-scoreof)


---

## Type Alias: ChoiceCriteria

```ts
type ChoiceCriteria = object;
```

Labels mapped to descriptions, or `null` for undescribed labels.

### Index Signature

```ts
[label: string]: EntryType
```



---

## Type Alias: Description

```ts
type Description = EntryType;
```

A criterion description; `null` leaves the label undescribed.



---

## Type Alias: EntryType

```ts
type EntryType = 
  | string
  | {
[key: string]: JsonValue;
}
  | JsonValue[]
  | null;
```

Text, a JSON object or array, or `null` for state, instructions, and criteria.



---

## Type Alias: EnvVar

```ts
type EnvVar = typeof ENV[keyof typeof ENV];
```



---

## Type Alias: Fetch

```ts
type Fetch = (input, init?) => Promise<Response>;
```

HTTP fetch implementation compatible with the global `fetch`.

### Parameters

#### input

`string`

#### init?

`RequestInit`

### Returns

`Promise`\<`Response`>



---

## Type Alias: JsonValue

```ts
type JsonValue = 
  | string
  | number
  | boolean
  | null
  | JsonValue[]
  | {
[key: string]: JsonValue;
};
```

A JSON-compatible value.



---

## Type Alias: LogLevel

```ts
type LogLevel = "debug" | "info" | "warn" | "error" | "off";
```

Log verbosity; `off` disables logging.



---

## Type Alias: Question

```ts
type Question = 
  | NoulQuestion
  | ScoreQuestion
  | ChoiceQuestion;
```

A question identified by its `type` field.



---

<a id="type-alias-resultfort"></a><a id="type-alias-resultfor"></a>

## Type Alias: `ResultFor<T>`
```ts
type ResultFor<T> = T extends NoulQuestion ? NoulResponse : T extends ScoreQuestion<infer S> ? ScoreResponse<S> : T extends ChoiceQuestion<infer E> ? ChoiceResponse<E> : never;
```

The answer type for a question, preserving its criteria keys.

### Type Parameters

#### T

`T` *extends* [`Question`](#type-alias-question)



---

## Type Alias: ScoreCriteria

```ts
type ScoreCriteria = readonly [EntryType, EntryType, ...EntryType[]];
```

At least two descriptions indexed by score from zero; `null` leaves a score undescribed.



---

<a id="type-alias-scorelegendt"></a><a id="type-alias-scorelegend"></a>

## Type Alias: `ScoreLegend<T>`
```ts
type ScoreLegend<T> = { readonly [score in ScoreOf<T>]: T[score] };
```

Rubric descriptions keyed by score.

### Type Parameters

#### T

`T` *extends* [`ScoreCriteria`](#type-alias-scorecriteria)



---

<a id="type-alias-scoreoft"></a><a id="type-alias-scoreof"></a>

## Type Alias: `ScoreOf<T>`
```ts
type ScoreOf<T> = number extends T["length"] ? number : Extract<keyof T, `${number}`>;
```

Score keys inferred from the rubric; a fixed-length tuple yields its indices, otherwise `number`.

### Type Parameters

#### T

`T` *extends* [`ScoreCriteria`](#type-alias-scorecriteria)
