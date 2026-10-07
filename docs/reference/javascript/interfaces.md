# JavaScript SDK reference: Interfaces

[← JavaScript reference](README.md) · [JS SDK guide](../../11-sdk-javascript.md) · Official: <https://docs.typesafe.ai/sdk/javascript/api>

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
- [SystemOneRequestPayload](#interface-systemonerequestpayload)
- [SystemOneResult](#interface-systemoneresult)
- [TypeSafeClientConfig](#interface-typesafeclientconfig)
- [Usage](#interface-usage)
- [WithResponse](#interface-withresponse)


---

<a id="interface-choicequestiont"></a><a id="interface-choicequestion"></a>

## Interface: `ChoiceQuestion<T>`
A question that selects between named alternatives.

### Type Parameters

#### T

`T` *extends* [`ChoiceCriteria`](type-aliases.md#type-alias-choicecriteria) = [`ChoiceCriteria`](type-aliases.md#type-alias-choicecriteria)

### Properties

<a id="sdk-criteria"></a>

#### criteria

```ts
criteria: T;
```

Descriptions of the available outcomes.

***

<a id="sdk-instructions"></a>

#### instructions?

```ts
optional instructions?: EntryType;
```

The question as text, a JSON object, or an array; optional or `null`.

***

<a id="sdk-type"></a>

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

`T` *extends* [`ChoiceCriteria`](type-aliases.md#type-alias-choicecriteria) = [`ChoiceCriteria`](type-aliases.md#type-alias-choicecriteria)

### Properties

<a id="sdk-choice"></a>

#### choice

```ts
readonly choice: keyof T & string;
```

The selected label.

***

<a id="sdk-confidence"></a>

#### confidence

```ts
readonly confidence: number;
```

Reported confidence in the selected label.

***

<a id="sdk-probabilities"></a>

#### probabilities

```ts
readonly probabilities: { readonly [label in string | number | symbol]: number };
```

Probabilities keyed by label.

***

<a id="sdk-type"></a>

#### type

```ts
readonly type: "choice";
```



---

## Interface: Logger

Log methods accepting a message and structured values; compatible with `console`.

### Methods

<a id="sdk-debug"></a>

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

<a id="sdk-error"></a>

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

<a id="sdk-info"></a>

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

<a id="sdk-warn"></a>

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

<a id="sdk-description"></a>

#### description

```ts
readonly description: string;
```

***

<a id="sdk-name"></a>

#### name

```ts
readonly name: string;
```

***

<a id="sdk-release_date"></a>

#### release\_date

```ts
readonly release_date: string;
```



---

## Interface: Models

Access to the Models API resource.

### Methods

<a id="sdk-list"></a>

#### list()

```ts
list(options?): APIPromise<ModelCard[]>;
```

List the models available to the account.

##### Parameters

###### options?

[`RequestOptions`](#interface-requestoptions) = `{}`

##### Returns

[`APIPromise`](classes.md#class-apipromiset)\<[`ModelCard`](#interface-modelcard)\[]>



---

## Interface: NoulQuestion

A yes/no question with optional descriptions for either outcome.

### Properties

<a id="sdk-criteria"></a>

#### criteria?

```ts
optional criteria?: 
  | {
  false?: EntryType;
  true?: EntryType;
}
  | null;
```

Optional descriptions of the yes and no outcomes.

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

<a id="sdk-instructions"></a>

#### instructions?

```ts
optional instructions?: EntryType;
```

The question as text, a JSON object, or an array; optional or `null`.

***

<a id="sdk-type"></a>

#### type

```ts
type: "noul";
```



---

## Interface: NoulResponse

A yes/no answer.

### Properties

<a id="sdk-noul"></a>

#### noul

```ts
readonly noul: number;
```

Probability of a yes answer, from zero to one.

***

<a id="sdk-type"></a>

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

<a id="sdk-headers"></a>

#### headers?

```ts
optional headers?: Record<string, string>;
```

Additional headers, merged over `defaultHeaders`.

***

<a id="sdk-retry"></a>

#### retry?

```ts
optional retry?: Partial<RetryPolicy>;
```

Retry overrides for this call; omitted fields inherit client settings.

***

<a id="sdk-signal"></a>

#### signal?

```ts
optional signal?: AbortSignal;
```

Cancellation signal for the request and pending retries.

***

<a id="sdk-timeout"></a>

#### timeout?

```ts
optional timeout?: number;
```

Timeout per attempt in milliseconds; there is no total retry budget.



---

## Interface: RetryPolicy

Retry configuration. Partial overrides inherit unset fields from the client or SDK defaults.

### Properties

<a id="sdk-apiconnectionerror"></a>

#### apiConnectionError

```ts
readonly apiConnectionError: boolean;
```

Retry connection failures, including interrupted response bodies (`APIConnectionError`). Default: true.

***

<a id="sdk-apitimeouterror"></a>

#### apiTimeoutError

```ts
readonly apiTimeoutError: boolean;
```

Whether to retry `APITimeoutError`. Default: true.

***

<a id="sdk-backoffinitialms"></a>

#### backoffInitialMs

```ts
readonly backoffInitialMs: number;
```

First backoff delay in milliseconds, doubled up to `backoffMaxMs`. Default: 500.

***

<a id="sdk-backoffjitter"></a>

#### backoffJitter

```ts
readonly backoffJitter: number;
```

Fraction of each backoff delay randomly subtracted, from 0 to 1. Default: 0.25.

***

<a id="sdk-backoffmaxms"></a>

#### backoffMaxMs

```ts
readonly backoffMaxMs: number;
```

Maximum backoff delay in milliseconds. Default: 5000.

***

<a id="sdk-httpstatuses"></a>

#### httpStatuses

```ts
readonly httpStatuses: ReadonlySet<number>;
```

HTTP status codes to retry. Default: 408, 429, and 500–599.

***

<a id="sdk-maxretries"></a>

#### maxRetries

```ts
readonly maxRetries: number;
```

Maximum retries after the initial attempt; `0` disables retries. Default: 2.

***

<a id="sdk-maxretryafterms"></a>

#### maxRetryAfterMs

```ts
readonly maxRetryAfterMs: number;
```

Maximum server retry delay in milliseconds; longer delays use backoff. Default: 60000.

***

<a id="sdk-respectretryafter"></a>

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

`T` *extends* [`ScoreCriteria`](type-aliases.md#type-alias-scorecriteria) = [`ScoreCriteria`](type-aliases.md#type-alias-scorecriteria)

### Properties

<a id="sdk-criteria"></a>

#### criteria

```ts
criteria: T;
```

Descriptions of the available outcomes.

***

<a id="sdk-instructions"></a>

#### instructions?

```ts
optional instructions?: EntryType;
```

The question as text, a JSON object, or an array; optional or `null`.

***

<a id="sdk-type"></a>

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

`T` *extends* [`ScoreCriteria`](type-aliases.md#type-alias-scorecriteria) = [`ScoreCriteria`](type-aliases.md#type-alias-scorecriteria)

### Properties

<a id="sdk-confidence"></a>

#### confidence

```ts
readonly confidence: number;
```

Reported confidence in the score.

***

<a id="sdk-legend"></a>

#### legend

```ts
readonly legend: ScoreLegend<T>;
```

Rubric descriptions keyed by score.

***

<a id="sdk-probabilities"></a>

#### probabilities

```ts
readonly probabilities: { readonly [score in number | `${number}`]: number };
```

Probabilities keyed by score.

***

<a id="sdk-score"></a>

#### score

```ts
readonly score: number;
```

Expected score, which may fall between integer rubric levels.

***

<a id="sdk-type"></a>

#### type

```ts
readonly type: "score";
```



---

<a id="interface-systemonerequestq"></a><a id="interface-systemonerequest"></a>

## Interface: `SystemOneRequest<Q>`
State and named questions for `systemOne`.

Additional properties on a request variable are forwarded, including `null` values.

### Extended by

* [`SystemOneRequestPayload`](#interface-systemonerequestpayload)

### Type Parameters

#### Q

`Q` *extends* [`Questions`](#interface-questions) = [`Questions`](#interface-questions)

### Properties

<a id="sdk-model"></a>

#### model?

```ts
optional model?: string;
```

Model override; omitted values inherit `defaultModel`.

***

<a id="sdk-questions"></a>

#### questions

```ts
questions: Q;
```

Nonempty questions keyed by the names used to identify their answers.

***

<a id="sdk-state"></a>

#### state

```ts
state: EntryType;
```

Text, a JSON object or array, or `null` to evaluate.



---

## Interface: SystemOneRequestPayload

Request body for `POST /v1/systemone`, with the model resolved.

### Extends

* [`SystemOneRequest`](#interface-systemonerequestq)

### Properties

<a id="sdk-model"></a>

#### model

```ts
model: string;
```

Model override; omitted values inherit `defaultModel`.

##### Overrides

[`SystemOneRequest`](#interface-systemonerequestq).[`model`](#interface-systemonerequestq)

***

<a id="sdk-questions"></a>

#### questions

```ts
questions: Questions;
```

Nonempty questions keyed by the names used to identify their answers.

##### Inherited from

[`SystemOneRequest`](#interface-systemonerequestq).[`questions`](#interface-systemonerequestq)

***

<a id="sdk-state"></a>

#### state

```ts
state: EntryType;
```

Text, a JSON object or array, or `null` to evaluate.

##### Inherited from

[`SystemOneRequest`](#interface-systemonerequestq).[`state`](#interface-systemonerequestq)



---

<a id="interface-systemoneresultq"></a><a id="interface-systemoneresult"></a>

## Interface: `SystemOneResult<Q>`
Answers keyed by question name, with model and usage metadata.

### Type Parameters

#### Q

`Q` *extends* [`Questions`](#interface-questions)

### Properties

<a id="sdk-answers"></a>

#### answers

```ts
readonly answers: { readonly [K in string | number | symbol]: ResultFor<Q[K]> };
```

Answers with types inferred from the supplied questions.

***

<a id="sdk-model"></a>

#### model

```ts
readonly model: string;
```

The model used to answer the request.

***

<a id="sdk-usage"></a>

#### usage

```ts
readonly usage: Usage;
```

Token usage for the request.



---

## Interface: TypeSafeClientConfig

Client options. Explicit values take precedence over environment variables, then SDK defaults.

### Properties

<a id="sdk-apikey"></a>

#### apiKey?

```ts
optional apiKey?: string;
```

Required API key; falls back to `TYPESAFE_API_KEY`.

***

<a id="sdk-baseurl"></a>

#### baseURL?

```ts
optional baseURL?: string;
```

API root; falls back to `TYPESAFE_BASE_URL`, then `https://api.typesafe.ai`.

***

<a id="sdk-dangerouslyallowbrowser"></a>

#### dangerouslyAllowBrowser?

```ts
optional dangerouslyAllowBrowser?: boolean;
```

Allow browser use, exposing the API key to page users. Default: false.

***

<a id="sdk-defaultheaders"></a>

#### defaultHeaders?

```ts
optional defaultHeaders?: Record<string, string>;
```

Additional request headers; per-call headers take precedence.

***

<a id="sdk-defaultmodel"></a>

#### defaultModel?

```ts
optional defaultModel?: string;
```

Default model; falls back to `TYPESAFE_DEFAULT_MODEL`, then `jev-latest`.

***

<a id="sdk-fetch"></a>

#### fetch?

```ts
optional fetch?: Fetch;
```

Custom HTTP fetch implementation for transport configuration or tests. Default: global `fetch`.

***

<a id="sdk-logger"></a>

#### logger?

```ts
optional logger?: Logger;
```

Logger filtered to `logLevel` and above. Default: prefixed `console`.

***

<a id="sdk-loglevel"></a>

#### logLevel?

```ts
optional logLevel?: LogLevel;
```

Log level; falls back to `TYPESAFE_LOG_LEVEL`, then `warn`.
`info` logs request summaries; `debug` adds headers and bodies.
Known credential headers are redacted; bodies are not.

***

<a id="sdk-retry"></a>

#### retry?

```ts
optional retry?: Partial<RetryPolicy>;
```

Retry overrides; omitted fields use the defaults in `RetryPolicy`.

***

<a id="sdk-timeout"></a>

#### timeout?

```ts
optional timeout?: number;
```

Timeout per attempt in milliseconds, without a total retry budget. Default: 10000.



---

## Interface: Usage

Token usage for a request.

### Properties

<a id="sdk-input_tokens"></a>

#### input\_tokens

```ts
readonly input_tokens: number;
```

Number of input tokens used.

***

<a id="sdk-output_tokens"></a>

#### output\_tokens

```ts
readonly output_tokens: number;
```

Number of output tokens used.



---

<a id="interface-withresponset"></a><a id="interface-withresponse"></a>

## Interface: `WithResponse<T>`
Parsed data with its HTTP response and request ID.

### Type Parameters

#### T

`T`

### Properties

<a id="sdk-data"></a>

#### data

```ts
data: T;
```

The parsed response body.

***

<a id="sdk-requestid"></a>

#### requestId

```ts
requestId: string | undefined;
```

Request ID from `x-typesafe-request-id`, or `undefined` when absent.

***

<a id="sdk-response"></a>

#### response

```ts
response: Response;
```

The HTTP response, with its body consumed by parsing.
