# JavaScript SDK reference: Interfaces

[← JavaScript reference](README.md) · [JS SDK guide](../../11-sdk-javascript.md) · Official: <https://docs.typesafe.ai/sdk/javascript/api>

- [BoxCoordinates](#interface-boxcoordinates)
- [BoxQuestion](#interface-boxquestion)
- [BoxResponse](#interface-boxresponse)
- [ChoiceQuestion](#interface-choicequestion)
- [ChoiceResponse](#interface-choiceresponse)
- [Logger](#interface-logger)
- [ModelCard](#interface-modelcard)
- [Models](#interface-models)
- [NoulQuestion](#interface-noulquestion)
- [NoulResponse](#interface-noulresponse)
- [Questions](#interface-questions)
- [RequestOptions](#interface-requestoptions)
- [RetryPolicy](#interface-retrypolicy)
- [ScoreQuestion](#interface-scorequestion)
- [ScoreResponse](#interface-scoreresponse)
- [SystemOneRequest](#interface-systemonerequest)
- [SystemOneResult](#interface-systemoneresult)
- [TextWithAssets](#interface-textwithassets)
- [TypeSafeClientConfig](#interface-typesafeclientconfig)
- [Usage](#interface-usage)
- [WithResponse](#interface-withresponse)


---

## Interface: BoxCoordinates

A box's edges as fractions of the image's height (`top`, `bottom`) and width (`left`, `right`).

### Properties

#### bottom

```ts
readonly bottom: number;
```

Bottom edge, as a fraction of image height from the top, from zero to one.

***

#### left

```ts
readonly left: number;
```

Left edge, as a fraction of image width from the left, from zero to one.

***

#### right

```ts
readonly right: number;
```

Right edge, as a fraction of image width from the left, from zero to one.

***

#### top

```ts
readonly top: number;
```

Top edge, as a fraction of image height from the top, from zero to one.



---

## Interface: BoxQuestion

A question that locates what its instructions describe in the request's image.

### Properties

#### instructions?

```ts
optional instructions?: EntryType;
```

What to locate, as text, an asset, a JSON object, or an array; optional or `null`.

***

#### type

```ts
type: "box";
```



---

## Interface: BoxResponse

The answer to a `box` question.

### Properties

#### box

```ts
readonly box: BoxCoordinates;
```

Where the instructions' subject is in the image.

***

#### confidence

```ts
readonly confidence: number | null;
```

Confidence in the box, from zero to one, or `null` when the API didn't report it.

***

#### type

```ts
readonly type: "box";
```



---

<a id="interface-choicequestiont"></a><a id="interface-choicequestion"></a>

## Interface: `ChoiceQuestion<T>`
A question that selects between named alternatives.

### Type Parameters

#### T

`T` *extends* [`ChoiceCriteria`](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/ChoiceCriteria) = [`ChoiceCriteria`](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/ChoiceCriteria)

### Properties

#### criteria

```ts
criteria: T;
```

Descriptions of the available outcomes; at least one label is required.

***

#### instructions?

```ts
optional instructions?: EntryType;
```

The question as text, a JSON object, or an array; optional or `null`.

***

#### type

```ts
type: "choice";
```



---

<a id="interface-choiceresponset"></a><a id="interface-choiceresponse"></a>

## Interface: `ChoiceResponse<T>`
A selected label and its probabilities.

### Type Parameters

#### T

`T` *extends* [`ChoiceCriteria`](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/ChoiceCriteria) = [`ChoiceCriteria`](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/ChoiceCriteria)

### Properties

#### choice

```ts
readonly choice: keyof T & string;
```

The selected label.

***

#### confidence

```ts
readonly confidence: number;
```

Reported confidence in the selected label.

***

#### probabilities

```ts
readonly probabilities: { readonly [label in string | number | symbol]: number };
```

Probabilities keyed by label.

***

#### type

```ts
readonly type: "choice";
```



---

## Interface: Logger

Log methods accepting a message and structured values; compatible with `console`.

### Methods

#### debug()

```ts
debug(message, ...args): void;
```

##### Parameters

###### message

`string`

###### args

...`unknown`\[]

##### Returns

`void`

***

#### error()

```ts
error(message, ...args): void;
```

##### Parameters

###### message

`string`

###### args

...`unknown`\[]

##### Returns

`void`

***

#### info()

```ts
info(message, ...args): void;
```

##### Parameters

###### message

`string`

###### args

...`unknown`\[]

##### Returns

`void`

***

#### warn()

```ts
warn(message, ...args): void;
```

##### Parameters

###### message

`string`

###### args

...`unknown`\[]

##### Returns

`void`



---

## Interface: ModelCard

Metadata for an available model.

### Properties

#### description

```ts
readonly description: string;
```

***

#### name

```ts
readonly name: string;
```

***

#### release\_date

```ts
readonly release_date: string;
```



---

## Interface: Models

Access to the Models API resource.

### Methods

#### list()

```ts
list(options?): APIPromise<ModelCard[]>;
```

List the models available to the account.

##### Parameters

###### options?

[`RequestOptions`](https://docs.typesafe.ai/sdk/javascript/api/interfaces/RequestOptions) = `{}`

##### Returns

[`APIPromise`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIPromise)\<[`ModelCard`](https://docs.typesafe.ai/sdk/javascript/api/interfaces/ModelCard)\[]>



---

## Interface: NoulQuestion

A yes/no question with optional descriptions for either outcome.

### Properties

#### criteria?

```ts
optional criteria?: 
  | {
  false?: EntryType;
  true?: EntryType;
}
  | null;
```

Descriptions of the yes and no outcomes; at least one is required when `instructions` is omitted or `null`.

##### Union Members

###### Type Literal

```ts
{
  false?: EntryType;
  true?: EntryType;
}
```

###### false?

```ts
optional false?: EntryType;
```

Description of the no outcome.

###### true?

```ts
optional true?: EntryType;
```

Description of the yes outcome.

***

`null`

***

#### instructions?

```ts
optional instructions?: EntryType;
```

The question as text, a JSON object, or an array; optional when `criteria` describes an outcome.

***

#### type

```ts
type: "noul";
```



---

## Interface: NoulResponse

A yes/no answer.

### Properties

#### noul

```ts
readonly noul: number;
```

Probability of a yes answer, from zero to one.

***

#### type

```ts
readonly type: "noul";
```



---

## Interface: Questions

Questions keyed by the names used to identify their answers.

### Indexable

```ts
[name: string]: Question
```



---

## Interface: RequestOptions

Per-call options that override client settings.

### Properties

#### headers?

```ts
optional headers?: Record<string, string>;
```

Additional headers, merged over `defaultHeaders`.

***

#### retry?

```ts
optional retry?: Partial<RetryPolicy>;
```

Retry overrides for this call; omitted fields inherit client settings.

***

#### signal?

```ts
optional signal?: AbortSignal;
```

Cancellation signal for the request and pending retries.

***

#### timeout?

```ts
optional timeout?: number;
```

Timeout per attempt in milliseconds; there is no total retry budget.



---

## Interface: RetryPolicy

Retry configuration. Partial overrides inherit unset fields from the client or SDK defaults.

### Properties

#### apiConnectionError

```ts
readonly apiConnectionError: boolean;
```

Retry connection failures, including interrupted response bodies (`APIConnectionError`). Default: true.

***

#### apiTimeoutError

```ts
readonly apiTimeoutError: boolean;
```

Whether to retry `APITimeoutError`. Default: true.

***

#### backoffInitialMs

```ts
readonly backoffInitialMs: number;
```

First backoff delay in milliseconds, doubled up to `backoffMaxMs`. Default: 500.

***

#### backoffJitter

```ts
readonly backoffJitter: number;
```

Fraction of each backoff delay randomly subtracted, from 0 to 1. Default: 0.25.

***

#### backoffMaxMs

```ts
readonly backoffMaxMs: number;
```

Maximum backoff delay in milliseconds. Default: 5000.

***

#### httpStatuses

```ts
readonly httpStatuses: ReadonlySet<number>;
```

HTTP status codes to retry. Default: 408, 429, and 500–599.

***

#### maxRetries

```ts
readonly maxRetries: number;
```

Maximum retries after the initial attempt; `0` disables retries. Default: 2.

***

#### maxRetryAfterMs

```ts
readonly maxRetryAfterMs: number;
```

Maximum server retry delay in milliseconds; longer delays use backoff. Default: 60000.

***

#### respectRetryAfter

```ts
readonly respectRetryAfter: boolean;
```

Honor `Retry-After` and `retry-after-ms` up to `maxRetryAfterMs`. Default: true.



---

<a id="interface-scorequestiont"></a><a id="interface-scorequestion"></a>

## Interface: `ScoreQuestion<T>`
A question that assigns a score using an ordered rubric.

### Type Parameters

#### T

`T` *extends* [`ScoreCriteria`](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/ScoreCriteria) = [`ScoreCriteria`](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/ScoreCriteria)

### Properties

#### criteria

```ts
criteria: T;
```

Descriptions of the available outcomes.

***

#### instructions?

```ts
optional instructions?: EntryType;
```

The question as text, a JSON object, or an array; optional or `null`.

***

#### type

```ts
type: "score";
```



---

<a id="interface-scoreresponset"></a><a id="interface-scoreresponse"></a>

## Interface: `ScoreResponse<T>`
An expected score with its rubric and probabilities.

### Type Parameters

#### T

`T` *extends* [`ScoreCriteria`](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/ScoreCriteria) = [`ScoreCriteria`](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/ScoreCriteria)

### Properties

#### confidence

```ts
readonly confidence: number;
```

Reported confidence in the score.

***

#### legend

```ts
readonly legend: ScoreLegend<T>;
```

Rubric descriptions keyed by score.

***

#### probabilities

```ts
readonly probabilities: { readonly [score in number | `${number}`]: number };
```

Probabilities keyed by score.

***

#### score

```ts
readonly score: number;
```

Expected score, which may fall between integer rubric levels.

***

#### type

```ts
readonly type: "score";
```



---

<a id="interface-systemonerequestq"></a><a id="interface-systemonerequest"></a>

## Interface: `SystemOneRequest<Q>`
State and named questions for `systemOne`.

Additional properties on a request variable are forwarded, including `null` values.

### Type Parameters

#### Q

`Q` *extends* [`Questions`](https://docs.typesafe.ai/sdk/javascript/api/interfaces/Questions) = [`Questions`](https://docs.typesafe.ai/sdk/javascript/api/interfaces/Questions)

### Properties

#### assets?

```ts
optional assets?: Record<string, Image>;
```

References mapped to assets, for referencing assets by name.

References are matched literally in string values within `state`, question instructions,
or criteria. Use distinct delimiters (such as `<photo>`) to avoid matching ordinary text.
Assets placed directly in `state` or question content, or in `withAssets` text, are sent
without being listed here. Every name must appear in the request; otherwise the call
rejects before sending.

***

#### model?

```ts
optional model?: string;
```

Model override; omitted values inherit `defaultModel`.

***

#### questions

```ts
questions: Q;
```

Nonempty questions keyed by the names used to identify their answers.

***

#### state

```ts
state: NonNullable<EntryType>;
```

Text, an asset, a JSON object, or an array to evaluate.



---

<a id="interface-systemoneresultq"></a><a id="interface-systemoneresult"></a>

## Interface: `SystemOneResult<Q>`
Answers keyed by question name, with model and usage metadata.

### Type Parameters

#### Q

`Q` *extends* [`Questions`](https://docs.typesafe.ai/sdk/javascript/api/interfaces/Questions)

### Properties

#### answers

```ts
readonly answers: { readonly [K in string | number | symbol]: ResultFor<Q[K]> };
```

Answers with types inferred from the supplied questions.

***

#### model

```ts
readonly model: string;
```

The model used to answer the request.

***

#### usage

```ts
readonly usage: Usage;
```

Token usage for the request.



---

## Interface: TextWithAssets

Text from a `withAssets` tagged template, with the assets interpolated into it.

### Properties

#### assets

```ts
readonly assets: readonly Image[];
```

The assets interpolated into the text, including those in nested `withAssets` text.

***

#### text

```ts
readonly text: string;
```

The text, with each asset replaced by its reference.

### Methods

#### toJSON()

```ts
toJSON(): string;
```

The text, written by `JSON.stringify` wherever this value appears in a request.

##### Returns

`string`

***

#### toString()

```ts
toString(): string;
```

##### Returns

`string`



---

## Interface: TypeSafeClientConfig

Client options. Explicit values take precedence over environment variables, then SDK defaults.

### Properties

#### apiKey?

```ts
optional apiKey?: string;
```

Required API key; falls back to `TYPESAFE_API_KEY`.

***

#### baseURL?

```ts
optional baseURL?: string;
```

API root; falls back to `TYPESAFE_BASE_URL`, then `https://api.typesafe.ai`.

***

#### compression?

```ts
optional compression?: Compression;
```

Request body compression, sent as `Content-Encoding`. Default: `"zstd"` on runtimes that
have it (Node.js 22.15 or newer), otherwise `false`. Bodies under 1 KiB are always sent
uncompressed. Pass `false` to send all bodies uncompressed, for example to an API that
doesn't accept compressed requests.

***

#### dangerouslyAllowBrowser?

```ts
optional dangerouslyAllowBrowser?: boolean;
```

Allow browser use, exposing the API key to page users. Default: false.

***

#### defaultHeaders?

```ts
optional defaultHeaders?: Record<string, string>;
```

Additional request headers; per-call headers take precedence.

***

#### defaultModel?

```ts
optional defaultModel?: string;
```

Default model; falls back to `TYPESAFE_DEFAULT_MODEL`, then `jev-latest`.

***

#### fetch?

```ts
optional fetch?: Fetch;
```

Custom HTTP fetch implementation for transport configuration or tests. Default: global `fetch`.

***

#### logger?

```ts
optional logger?: Logger;
```

Logger filtered to `logLevel` and above. Default: prefixed `console`.

***

#### logLevel?

```ts
optional logLevel?: LogLevel;
```

Log level; falls back to `TYPESAFE_LOG_LEVEL`, then `warn`.
`info` logs request summaries; `debug` adds headers and bodies.
Known credential headers are redacted; bodies are not.

***

#### retry?

```ts
optional retry?: Partial<RetryPolicy>;
```

Retry overrides; omitted fields use the defaults in `RetryPolicy`.

***

#### timeout?

```ts
optional timeout?: number;
```

Timeout per attempt in milliseconds, without a total retry budget. Default: 10000.



---

## Interface: Usage

Token usage for a request.

### Properties

#### input\_tokens

```ts
readonly input_tokens: number | null;
```

Number of input tokens used, or `null` when the API did not report it.

***

#### output\_tokens

```ts
readonly output_tokens: number | null;
```

Number of output tokens used, or `null` when the API did not report it.



---

<a id="interface-withresponset"></a><a id="interface-withresponse"></a>

## Interface: `WithResponse<T>`
Parsed data with its HTTP response and request ID.

### Type Parameters

#### T

`T`

### Properties

#### data

```ts
data: T;
```

The parsed response body.

***

#### requestId

```ts
requestId: string | undefined;
```

Request ID from `x-typesafe-request-id`, or `undefined` when absent.

***

#### response

```ts
response: Response;
```

The HTTP response, with its body consumed by parsing.
