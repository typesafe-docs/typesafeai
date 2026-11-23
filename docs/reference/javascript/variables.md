# JavaScript SDK reference: Variables

[← JavaScript reference](README.md) · [JS SDK guide](../../11-sdk-javascript.md) · Official: <https://docs.typesafe.ai/sdk/javascript/api>

- [ENV](#variable-env)
- [LOG_LEVELS](#variable-log_levels)
- [VERSION](#variable-version)
- [noul](#variable-noul)
- [score](#variable-score)
- [withAssets](#variable-withassets)


---

## Variable: ENV

```ts
const ENV: object;
```

Environment variable names for client configuration. Explicit options take precedence.

### Type Declaration

#### apiKey

```ts
readonly apiKey: "TYPESAFE_API_KEY" = "TYPESAFE_API_KEY";
```

Required API key; used when `apiKey` is omitted.

#### baseURL

```ts
readonly baseURL: "TYPESAFE_BASE_URL" = "TYPESAFE_BASE_URL";
```

API root; defaults to `https://api.typesafe.ai`.

#### defaultModel

```ts
readonly defaultModel: "TYPESAFE_DEFAULT_MODEL" = "TYPESAFE_DEFAULT_MODEL";
```

Default model name; defaults to `jev-latest`.

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
const VERSION: "0.7.0" = "0.7.0";
```



---

## Variable: noul

```ts
const noul: {
  (instructions, criteria?): NoulQuestion;
  (instructions, criteria): NoulQuestion;
};
```

Create a yes/no question with optional descriptions for either outcome.

### Call Signature

```ts
(instructions, criteria?): NoulQuestion;
```

#### Parameters

##### instructions

`NonNullable`\<[`EntryType`](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/EntryType)>

##### criteria?

\| \{
`false?`: [`EntryType`](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/EntryType);
`true?`: [`EntryType`](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/EntryType);
}
\| `null`

###### Type Literal

\{
`false?`: [`EntryType`](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/EntryType);
`true?`: [`EntryType`](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/EntryType);
}

###### false?

[`EntryType`](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/EntryType)

Description of the no outcome.

###### true?

[`EntryType`](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/EntryType)

Description of the yes outcome.

***

`null`

#### Returns

[`NoulQuestion`](https://docs.typesafe.ai/sdk/javascript/api/interfaces/NoulQuestion)

### Call Signature

```ts
(instructions, criteria): NoulQuestion;
```

#### Parameters

##### instructions

[`EntryType`](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/EntryType) | `undefined`

##### criteria

\| \{
`false?`: [`EntryType`](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/EntryType);
`true`: `NonNullable`\<[`EntryType`](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/EntryType)>;
}
\| \{
`false`: `NonNullable`\<[`EntryType`](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/EntryType)>;
`true?`: [`EntryType`](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/EntryType);
}

#### Returns

[`NoulQuestion`](https://docs.typesafe.ai/sdk/javascript/api/interfaces/NoulQuestion)

### Param

**instructions**

The question as text, a JSON object or array; `null` or omitted
requires `criteria` to describe at least one outcome.

### Param

**criteria**

Descriptions of the yes and no outcomes.



---

## Variable: score

```ts
const score: {
<T>  (instructions, criteria): ScoreQuestion<T>;
<T>  (instructions, criteria): ScoreQuestion<readonly [T[number], T[number], T[number]]>;
};
```

Create a score question using an ordered rubric.

### Call Signature

```ts
<T>(instructions, criteria): ScoreQuestion<T>;
```

#### Type Parameters

##### T

`T` *extends* [`ScoreCriteria`](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/ScoreCriteria)

#### Parameters

##### instructions

[`EntryType`](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/EntryType)

##### criteria

`T`

#### Returns

[`ScoreQuestion`](https://docs.typesafe.ai/sdk/javascript/api/interfaces/ScoreQuestion)\<`T`>

### Call Signature

```ts
<T>(instructions, criteria): ScoreQuestion<readonly [T[number], T[number], T[number]]>;
```

#### Type Parameters

##### T

`T` *extends* readonly [`EntryType`](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/EntryType)\[]

#### Parameters

##### instructions

[`EntryType`](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/EntryType)

##### criteria

`T` & `number` *extends* `T`\[`"length"`] ? `unknown` : `never`

#### Returns

[`ScoreQuestion`](https://docs.typesafe.ai/sdk/javascript/api/interfaces/ScoreQuestion)\<readonly \[`T`\[`number`], `T`\[`number`], `T`\[`number`]]>

### Param

**instructions**

The question as text, a JSON object or array, or `null`.

### Param

**criteria**

At least two descriptions indexed by score from zero; entries may be `null`.
A list built at runtime, such as a `string[]`, is accepted, and `systemOne` rejects it when
it has fewer than two entries.



---

## Variable: withAssets

```ts
const withAssets: {
(strings, ...values): TextWithAssets;
  join: TextWithAssets;
};
```

Tag a template literal so the assets interpolated into it are sent with the text.

Each asset is replaced by its reference; other values are converted to strings, as in an
untagged template literal. To write a list of assets with a separator, use
`withAssets.join`.

### Type Declaration

### Parameters

#### strings

`TemplateStringsArray`

#### values

...readonly `unknown`\[]

### Returns

[`TextWithAssets`](https://docs.typesafe.ai/sdk/javascript/api/interfaces/TextWithAssets)

#### join()

```ts
join(values, separator?): TextWithAssets;
```

Join `values` with `separator`, as `Array.prototype.join` does, and send the assets among
them with the text. The result can be passed as content or interpolated into `withAssets`.

##### Parameters

###### values

readonly `unknown`\[]

###### separator?

`string`

Written between values. Default: `","`.

##### Returns

[`TextWithAssets`](https://docs.typesafe.ai/sdk/javascript/api/interfaces/TextWithAssets)

##### Example

```ts
const { answers } = await client.systemOne({
  state: withAssets`The seller uploaded ${withAssets.join(uploads, ", ")}.`,
  questions: { same: noul("Do the uploads show the same product?") },
});
```

### Example

```ts
const { answers } = await client.systemOne({
  state: withAssets`Compare ${photo} with the listing.`,
  questions: { same: noul(withAssets`Is ${photo} the product in ${listing}?`) },
});
```
