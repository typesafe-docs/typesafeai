# JavaScript SDK reference: Classes

[← JavaScript reference](README.md) · [JS SDK guide](../../11-sdk-javascript.md) · Official: <https://docs.typesafe.ai/sdk/javascript/api>

- [APIConnectionError](#class-apiconnectionerror)
- [APIError](#class-apierror)
- [APIPromise](#class-apipromise)
- [APITimeoutError](#class-apitimeouterror)
- [APIUserAbortError](#class-apiuseraborterror)
- [AuthenticationError](#class-authenticationerror)
- [BadRequestError](#class-badrequesterror)
- [InternalServerError](#class-internalservererror)
- [NotFoundError](#class-notfounderror)
- [PermissionDeniedError](#class-permissiondeniederror)
- [RateLimitError](#class-ratelimiterror)
- [TypeSafeClient](#class-typesafeclient)
- [TypeSafeError](#class-typesafeerror)
- [UnprocessableEntityError](#class-unprocessableentityerror)


---

## Class: APIConnectionError

The request or response-body delivery failed (DNS, TLS, connection closed, etc.).

### Extends

* [`TypeSafeError`](#class-typesafeerror)

### Extended by

* [`APITimeoutError`](#class-apitimeouterror)

### Constructors

<a id="sdk-constructor"></a>

#### Constructor

```ts
new APIConnectionError(message?, options?): APIConnectionError;
```

##### Parameters

###### message?

`string` = `"Connection error."`

###### options?

`ErrorOptions`

##### Returns

`APIConnectionError`

##### Overrides

[`TypeSafeError`](#class-typesafeerror).[`constructor`](#class-typesafeerror)



---

## Class: APIError

An unsuccessful HTTP response from the API.

### Extends

* [`TypeSafeError`](#class-typesafeerror)

### Extended by

* [`AuthenticationError`](#class-authenticationerror)
* [`BadRequestError`](#class-badrequesterror)
* [`InternalServerError`](#class-internalservererror)
* [`NotFoundError`](#class-notfounderror)
* [`PermissionDeniedError`](#class-permissiondeniederror)
* [`RateLimitError`](#class-ratelimiterror)
* [`UnprocessableEntityError`](#class-unprocessableentityerror)

### Constructors

<a id="sdk-constructor"></a>

#### Constructor

```ts
new APIError(
   status, 
   body, 
   headers, 
   message?
): APIError;
```

##### Parameters

###### status

`number`

###### body

`unknown`

###### headers

`Headers`

###### message?

`string`

##### Returns

`APIError`

##### Overrides

[`TypeSafeError`](#class-typesafeerror).[`constructor`](#class-typesafeerror)

### Properties

<a id="sdk-body"></a>

#### body

```ts
readonly body: unknown;
```

Parsed JSON, response text, or `undefined` for an empty body.

***

<a id="sdk-headers"></a>

#### headers

```ts
readonly headers: Headers;
```

HTTP response headers.

***

<a id="sdk-requestid"></a>

#### requestId

```ts
readonly requestId: string | undefined;
```

Request ID from `x-typesafe-request-id`, or `undefined` when absent.

***

<a id="sdk-status"></a>

#### status

```ts
readonly status: number;
```

HTTP response status code.

### Methods

<a id="sdk-fromresponse"></a>

#### fromResponse()

```ts
static fromResponse(
   status, 
   body, 
   headers
): APIError;
```

Create the error subclass for an HTTP status code.

##### Parameters

###### status

`number`

###### body

`unknown`

###### headers

`Headers`

##### Returns

`APIError`



---

<a id="class-apipromiset"></a><a id="class-apipromise"></a>

## Class: `APIPromise<T>`
A promise for the parsed result with access to the HTTP response.

Non-2xx responses reject with an `APIError`, including through `asResponse()`.

### Extends

* `Promise`\<`T`>

### Type Parameters

#### T

`T`

### Constructors

<a id="sdk-constructor"></a>

#### Constructor

```ts
new APIPromise<T>(responsePromise, parseResponse): APIPromise<T>;
```

##### Parameters

###### responsePromise

`Promise`\<`Response`>

###### parseResponse

(`response`) => `Promise`\<`T`>

##### Returns

`APIPromise`\<`T`>

##### Overrides

```ts
Promise<T>.constructor
```

### Methods

<a id="sdk-asresponse"></a>

#### asResponse()

```ts
asResponse(): Promise<Response>;
```

Resolves to the raw `Response` without parsing the body. SDK requests buffer the full
body under the request timeout before handoff; reading it afterwards is caller-owned.
The caller owns the body; don't also `await` the parsed result on the same promise.

##### Returns

`Promise`\<`Response`>

***

<a id="sdk-catch"></a>

#### catch()

```ts
catch<TResult>(onrejected?): Promise<T | TResult>;
```

Attaches a callback for only the rejection of the Promise.

##### Type Parameters

###### TResult

`TResult` = `never`

##### Parameters

###### onrejected?

((`reason`) => `TResult` | `PromiseLike`\<`TResult`>) | `null`

The callback to execute when the Promise is rejected.

##### Returns

`Promise`\<`T` | `TResult`>

A Promise for the completion of the callback.

##### Overrides

```ts
Promise.catch
```

***

<a id="sdk-finally"></a>

#### finally()

```ts
finally(onfinally?): Promise<T>;
```

Attaches a callback that is invoked when the Promise is settled (fulfilled or rejected). The
resolved value cannot be modified from the callback.

##### Parameters

###### onfinally?

(() => `void`) | `null`

The callback to execute when the Promise is settled (fulfilled or rejected).

##### Returns

`Promise`\<`T`>

A Promise for the completion of the callback.

##### Overrides

```ts
Promise.finally
```

***

<a id="sdk-map"></a>

#### map()

```ts
map<U>(fn): APIPromise<U>;
```

Transform the parsed result, sharing the HTTP response and a single body parse.

##### Type Parameters

###### U

`U`

##### Parameters

###### fn

(`data`) => `U`

##### Returns

`APIPromise`\<`U`>

***

<a id="sdk-then"></a>

#### then()

```ts
then<TResult1, TResult2>(onfulfilled?, onrejected?): Promise<TResult1 | TResult2>;
```

Attaches callbacks for the resolution and/or rejection of the Promise.

##### Type Parameters

###### TResult1

`TResult1` = `T`

###### TResult2

`TResult2` = `never`

##### Parameters

###### onfulfilled?

((`value`) => `TResult1` | `PromiseLike`\<`TResult1`>) | `null`

The callback to execute when the Promise is resolved.

###### onrejected?

((`reason`) => `TResult2` | `PromiseLike`\<`TResult2`>) | `null`

The callback to execute when the Promise is rejected.

##### Returns

`Promise`\<`TResult1` | `TResult2`>

A Promise for the completion of which ever callback is executed.

##### Overrides

```ts
Promise.then
```

***

<a id="sdk-withresponse"></a>

#### withResponse()

```ts
withResponse(): Promise<WithResponse<T>>;
```

Return the parsed result, HTTP response, and request ID.

##### Returns

`Promise`\<[`WithResponse`](interfaces.md#interface-withresponset)\<`T`>>



---

## Class: APITimeoutError

The full response did not arrive within the timeout. A kind of `APIConnectionError`.

### Extends

* [`APIConnectionError`](#class-apiconnectionerror)

### Constructors

<a id="sdk-constructor"></a>

#### Constructor

```ts
new APITimeoutError(timeoutMs, options?): APITimeoutError;
```

##### Parameters

###### timeoutMs

`number`

###### options?

`ErrorOptions`

##### Returns

`APITimeoutError`

##### Overrides

[`APIConnectionError`](#class-apiconnectionerror).[`constructor`](#class-apiconnectionerror)

### Properties

<a id="sdk-timeoutms"></a>

#### timeoutMs

```ts
readonly timeoutMs: number;
```

Configured timeout in milliseconds.



---

## Class: APIUserAbortError

The caller cancelled the request through an `AbortSignal`.

### Extends

* [`TypeSafeError`](#class-typesafeerror)

### Constructors

<a id="sdk-constructor"></a>

#### Constructor

```ts
new APIUserAbortError(message?, options?): APIUserAbortError;
```

##### Parameters

###### message?

`string` = `"Request was aborted."`

###### options?

`ErrorOptions`

##### Returns

`APIUserAbortError`

##### Overrides

[`TypeSafeError`](#class-typesafeerror).[`constructor`](#class-typesafeerror)



---

## Class: AuthenticationError

HTTP 401: authentication failed.

### Extends

* [`APIError`](#class-apierror)

### Constructors

<a id="sdk-constructor"></a>

#### Constructor

```ts
new AuthenticationError(
   status, 
   body, 
   headers, 
   message?
): AuthenticationError;
```

##### Parameters

###### status

`number`

###### body

`unknown`

###### headers

`Headers`

###### message?

`string`

##### Returns

`AuthenticationError`

##### Inherited from

[`APIError`](#class-apierror).[`constructor`](#class-apierror)

### Properties

<a id="sdk-body"></a>

#### body

```ts
readonly body: unknown;
```

Parsed JSON, response text, or `undefined` for an empty body.

##### Inherited from

[`APIError`](#class-apierror).[`body`](#class-apierror)

***

<a id="sdk-headers"></a>

#### headers

```ts
readonly headers: Headers;
```

HTTP response headers.

##### Inherited from

[`APIError`](#class-apierror).[`headers`](#class-apierror)

***

<a id="sdk-requestid"></a>

#### requestId

```ts
readonly requestId: string | undefined;
```

Request ID from `x-typesafe-request-id`, or `undefined` when absent.

##### Inherited from

[`APIError`](#class-apierror).[`requestId`](#class-apierror)

***

<a id="sdk-status"></a>

#### status

```ts
readonly status: number;
```

HTTP response status code.

##### Inherited from

[`APIError`](#class-apierror).[`status`](#class-apierror)

### Methods

<a id="sdk-fromresponse"></a>

#### fromResponse()

```ts
static fromResponse(
   status, 
   body, 
   headers
): APIError;
```

Create the error subclass for an HTTP status code.

##### Parameters

###### status

`number`

###### body

`unknown`

###### headers

`Headers`

##### Returns

[`APIError`](#class-apierror)

##### Inherited from

[`APIError`](#class-apierror).[`fromResponse`](#class-apierror)



---

## Class: BadRequestError

HTTP 400: the request is invalid.

### Extends

* [`APIError`](#class-apierror)

### Constructors

<a id="sdk-constructor"></a>

#### Constructor

```ts
new BadRequestError(
   status, 
   body, 
   headers, 
   message?
): BadRequestError;
```

##### Parameters

###### status

`number`

###### body

`unknown`

###### headers

`Headers`

###### message?

`string`

##### Returns

`BadRequestError`

##### Inherited from

[`APIError`](#class-apierror).[`constructor`](#class-apierror)

### Properties

<a id="sdk-body"></a>

#### body

```ts
readonly body: unknown;
```

Parsed JSON, response text, or `undefined` for an empty body.

##### Inherited from

[`APIError`](#class-apierror).[`body`](#class-apierror)

***

<a id="sdk-headers"></a>

#### headers

```ts
readonly headers: Headers;
```

HTTP response headers.

##### Inherited from

[`APIError`](#class-apierror).[`headers`](#class-apierror)

***

<a id="sdk-requestid"></a>

#### requestId

```ts
readonly requestId: string | undefined;
```

Request ID from `x-typesafe-request-id`, or `undefined` when absent.

##### Inherited from

[`APIError`](#class-apierror).[`requestId`](#class-apierror)

***

<a id="sdk-status"></a>

#### status

```ts
readonly status: number;
```

HTTP response status code.

##### Inherited from

[`APIError`](#class-apierror).[`status`](#class-apierror)

### Methods

<a id="sdk-fromresponse"></a>

#### fromResponse()

```ts
static fromResponse(
   status, 
   body, 
   headers
): APIError;
```

Create the error subclass for an HTTP status code.

##### Parameters

###### status

`number`

###### body

`unknown`

###### headers

`Headers`

##### Returns

[`APIError`](#class-apierror)

##### Inherited from

[`APIError`](#class-apierror).[`fromResponse`](#class-apierror)



---

## Class: InternalServerError

HTTP 5xx: the server failed to handle the request.

### Extends

* [`APIError`](#class-apierror)

### Constructors

<a id="sdk-constructor"></a>

#### Constructor

```ts
new InternalServerError(
   status, 
   body, 
   headers, 
   message?
): InternalServerError;
```

##### Parameters

###### status

`number`

###### body

`unknown`

###### headers

`Headers`

###### message?

`string`

##### Returns

`InternalServerError`

##### Inherited from

[`APIError`](#class-apierror).[`constructor`](#class-apierror)

### Properties

<a id="sdk-body"></a>

#### body

```ts
readonly body: unknown;
```

Parsed JSON, response text, or `undefined` for an empty body.

##### Inherited from

[`APIError`](#class-apierror).[`body`](#class-apierror)

***

<a id="sdk-headers"></a>

#### headers

```ts
readonly headers: Headers;
```

HTTP response headers.

##### Inherited from

[`APIError`](#class-apierror).[`headers`](#class-apierror)

***

<a id="sdk-requestid"></a>

#### requestId

```ts
readonly requestId: string | undefined;
```

Request ID from `x-typesafe-request-id`, or `undefined` when absent.

##### Inherited from

[`APIError`](#class-apierror).[`requestId`](#class-apierror)

***

<a id="sdk-status"></a>

#### status

```ts
readonly status: number;
```

HTTP response status code.

##### Inherited from

[`APIError`](#class-apierror).[`status`](#class-apierror)

### Methods

<a id="sdk-fromresponse"></a>

#### fromResponse()

```ts
static fromResponse(
   status, 
   body, 
   headers
): APIError;
```

Create the error subclass for an HTTP status code.

##### Parameters

###### status

`number`

###### body

`unknown`

###### headers

`Headers`

##### Returns

[`APIError`](#class-apierror)

##### Inherited from

[`APIError`](#class-apierror).[`fromResponse`](#class-apierror)



---

## Class: NotFoundError

HTTP 404: the resource was not found.

### Extends

* [`APIError`](#class-apierror)

### Constructors

<a id="sdk-constructor"></a>

#### Constructor

```ts
new NotFoundError(
   status, 
   body, 
   headers, 
   message?
): NotFoundError;
```

##### Parameters

###### status

`number`

###### body

`unknown`

###### headers

`Headers`

###### message?

`string`

##### Returns

`NotFoundError`

##### Inherited from

[`APIError`](#class-apierror).[`constructor`](#class-apierror)

### Properties

<a id="sdk-body"></a>

#### body

```ts
readonly body: unknown;
```

Parsed JSON, response text, or `undefined` for an empty body.

##### Inherited from

[`APIError`](#class-apierror).[`body`](#class-apierror)

***

<a id="sdk-headers"></a>

#### headers

```ts
readonly headers: Headers;
```

HTTP response headers.

##### Inherited from

[`APIError`](#class-apierror).[`headers`](#class-apierror)

***

<a id="sdk-requestid"></a>

#### requestId

```ts
readonly requestId: string | undefined;
```

Request ID from `x-typesafe-request-id`, or `undefined` when absent.

##### Inherited from

[`APIError`](#class-apierror).[`requestId`](#class-apierror)

***

<a id="sdk-status"></a>

#### status

```ts
readonly status: number;
```

HTTP response status code.

##### Inherited from

[`APIError`](#class-apierror).[`status`](#class-apierror)

### Methods

<a id="sdk-fromresponse"></a>

#### fromResponse()

```ts
static fromResponse(
   status, 
   body, 
   headers
): APIError;
```

Create the error subclass for an HTTP status code.

##### Parameters

###### status

`number`

###### body

`unknown`

###### headers

`Headers`

##### Returns

[`APIError`](#class-apierror)

##### Inherited from

[`APIError`](#class-apierror).[`fromResponse`](#class-apierror)



---

## Class: PermissionDeniedError

HTTP 403: access is denied.

### Extends

* [`APIError`](#class-apierror)

### Constructors

<a id="sdk-constructor"></a>

#### Constructor

```ts
new PermissionDeniedError(
   status, 
   body, 
   headers, 
   message?
): PermissionDeniedError;
```

##### Parameters

###### status

`number`

###### body

`unknown`

###### headers

`Headers`

###### message?

`string`

##### Returns

`PermissionDeniedError`

##### Inherited from

[`APIError`](#class-apierror).[`constructor`](#class-apierror)

### Properties

<a id="sdk-body"></a>

#### body

```ts
readonly body: unknown;
```

Parsed JSON, response text, or `undefined` for an empty body.

##### Inherited from

[`APIError`](#class-apierror).[`body`](#class-apierror)

***

<a id="sdk-headers"></a>

#### headers

```ts
readonly headers: Headers;
```

HTTP response headers.

##### Inherited from

[`APIError`](#class-apierror).[`headers`](#class-apierror)

***

<a id="sdk-requestid"></a>

#### requestId

```ts
readonly requestId: string | undefined;
```

Request ID from `x-typesafe-request-id`, or `undefined` when absent.

##### Inherited from

[`APIError`](#class-apierror).[`requestId`](#class-apierror)

***

<a id="sdk-status"></a>

#### status

```ts
readonly status: number;
```

HTTP response status code.

##### Inherited from

[`APIError`](#class-apierror).[`status`](#class-apierror)

### Methods

<a id="sdk-fromresponse"></a>

#### fromResponse()

```ts
static fromResponse(
   status, 
   body, 
   headers
): APIError;
```

Create the error subclass for an HTTP status code.

##### Parameters

###### status

`number`

###### body

`unknown`

###### headers

`Headers`

##### Returns

[`APIError`](#class-apierror)

##### Inherited from

[`APIError`](#class-apierror).[`fromResponse`](#class-apierror)



---

## Class: RateLimitError

HTTP 429: the rate limit was exceeded.

### Extends

* [`APIError`](#class-apierror)

### Constructors

<a id="sdk-constructor"></a>

#### Constructor

```ts
new RateLimitError(
   status, 
   body, 
   headers, 
   message?
): RateLimitError;
```

##### Parameters

###### status

`number`

###### body

`unknown`

###### headers

`Headers`

###### message?

`string`

##### Returns

`RateLimitError`

##### Inherited from

[`APIError`](#class-apierror).[`constructor`](#class-apierror)

### Properties

<a id="sdk-body"></a>

#### body

```ts
readonly body: unknown;
```

Parsed JSON, response text, or `undefined` for an empty body.

##### Inherited from

[`APIError`](#class-apierror).[`body`](#class-apierror)

***

<a id="sdk-headers"></a>

#### headers

```ts
readonly headers: Headers;
```

HTTP response headers.

##### Inherited from

[`APIError`](#class-apierror).[`headers`](#class-apierror)

***

<a id="sdk-requestid"></a>

#### requestId

```ts
readonly requestId: string | undefined;
```

Request ID from `x-typesafe-request-id`, or `undefined` when absent.

##### Inherited from

[`APIError`](#class-apierror).[`requestId`](#class-apierror)

***

<a id="sdk-retryafterms"></a>

#### retryAfterMs

```ts
readonly retryAfterMs: number | undefined;
```

Server retry delay in milliseconds, or `undefined` when absent or invalid.

***

<a id="sdk-status"></a>

#### status

```ts
readonly status: number;
```

HTTP response status code.

##### Inherited from

[`APIError`](#class-apierror).[`status`](#class-apierror)

### Methods

<a id="sdk-fromresponse"></a>

#### fromResponse()

```ts
static fromResponse(
   status, 
   body, 
   headers
): APIError;
```

Create the error subclass for an HTTP status code.

##### Parameters

###### status

`number`

###### body

`unknown`

###### headers

`Headers`

##### Returns

[`APIError`](#class-apierror)

##### Inherited from

[`APIError`](#class-apierror).[`fromResponse`](#class-apierror)



---

## Class: TypeSafeClient

Client for the TypeSafe AI API.

### Constructors

<a id="sdk-constructor"></a>

#### Constructor

```ts
new TypeSafeClient(config?): TypeSafeClient;
```

Create a client for the TypeSafe AI API.

Explicit options take precedence over environment variables, then SDK defaults.
Empty or whitespace-only environment values are ignored.

##### Parameters

###### config?

[`TypeSafeClientConfig`](interfaces.md#interface-typesafeclientconfig) = `{}`

##### Returns

`TypeSafeClient`

##### Throws

The API key is missing, configuration is invalid, or the runtime is unsupported.

### Properties

<a id="sdk-baseurl"></a>

#### baseURL

```ts
readonly baseURL: string;
```

API root with trailing slashes removed.

***

<a id="sdk-defaultheaders"></a>

#### defaultHeaders

```ts
readonly defaultHeaders: Readonly<Record<string, string>>;
```

Additional headers sent with each request.

***

<a id="sdk-defaultmodel"></a>

#### defaultModel

```ts
readonly defaultModel: string;
```

Model used when a request omits `model`.

***

<a id="sdk-fetch"></a>

#### fetch

```ts
readonly fetch: Fetch;
```

HTTP fetch implementation.

***

<a id="sdk-logger"></a>

#### logger

```ts
readonly logger: Logger;
```

The configured logger, filtered to `logLevel`.

***

<a id="sdk-loglevel"></a>

#### logLevel

```ts
readonly logLevel: LogLevel;
```

Configured log verbosity.

***

<a id="sdk-models"></a>

#### models

```ts
readonly models: Models;
```

The models available to the account.

***

<a id="sdk-retry"></a>

#### retry

```ts
readonly retry: RetryPolicy;
```

Retry settings with constructor overrides applied.

***

<a id="sdk-timeout"></a>

#### timeout

```ts
readonly timeout: number;
```

Timeout per attempt in milliseconds.

### Methods

<a id="sdk-systemone"></a>

#### systemOne()

```ts
systemOne<Q>(request, options?): APIPromise<SystemOneResult<Q>>;
```

Answer named questions about text or structured state.

##### Type Parameters

###### Q

`Q` *extends* [`Questions`](interfaces.md#interface-questions)

##### Parameters

###### request

[`SystemOneRequest`](interfaces.md#interface-systemonerequestq)\<`Q`>

State, questions, and an optional model override.

###### options?

[`RequestOptions`](interfaces.md#interface-requestoptions) = `{}`

Per-call timeout, retry, headers, and cancellation settings.

##### Returns

[`APIPromise`](#class-apipromiset)\<[`SystemOneResult`](interfaces.md#interface-systemoneresultq)\<`Q`>>

Answers typed by question name and criteria, with model and token usage.

##### Throws

Questions are empty, or score criteria are not a list of at least two entries.

##### Throws

The server returns a non-2xx response after retries.

##### Throws

The request cannot connect or times out after retries.

##### Throws

The caller aborts the request.

##### Example

```ts
const { answers } = await client.systemOne({
  state: "I was charged twice. Please help.",
  questions: { billing: noul("Is this about billing?") },
});
console.log(answers.billing.noul);
```



---

## Class: TypeSafeError

Base class for SDK errors.

### Extends

* `Error`

### Extended by

* [`APIConnectionError`](#class-apiconnectionerror)
* [`APIError`](#class-apierror)
* [`APIUserAbortError`](#class-apiuseraborterror)

### Constructors

<a id="sdk-constructor"></a>

#### Constructor

```ts
new TypeSafeError(message, options?): TypeSafeError;
```

##### Parameters

###### message

`string`

###### options?

`ErrorOptions`

##### Returns

`TypeSafeError`

##### Overrides

```ts
Error.constructor
```



---

## Class: UnprocessableEntityError

HTTP 422: request validation failed.

### Extends

* [`APIError`](#class-apierror)

### Constructors

<a id="sdk-constructor"></a>

#### Constructor

```ts
new UnprocessableEntityError(
   status, 
   body, 
   headers, 
   message?
): UnprocessableEntityError;
```

##### Parameters

###### status

`number`

###### body

`unknown`

###### headers

`Headers`

###### message?

`string`

##### Returns

`UnprocessableEntityError`

##### Inherited from

[`APIError`](#class-apierror).[`constructor`](#class-apierror)

### Properties

<a id="sdk-body"></a>

#### body

```ts
readonly body: unknown;
```

Parsed JSON, response text, or `undefined` for an empty body.

##### Inherited from

[`APIError`](#class-apierror).[`body`](#class-apierror)

***

<a id="sdk-headers"></a>

#### headers

```ts
readonly headers: Headers;
```

HTTP response headers.

##### Inherited from

[`APIError`](#class-apierror).[`headers`](#class-apierror)

***

<a id="sdk-requestid"></a>

#### requestId

```ts
readonly requestId: string | undefined;
```

Request ID from `x-typesafe-request-id`, or `undefined` when absent.

##### Inherited from

[`APIError`](#class-apierror).[`requestId`](#class-apierror)

***

<a id="sdk-status"></a>

#### status

```ts
readonly status: number;
```

HTTP response status code.

##### Inherited from

[`APIError`](#class-apierror).[`status`](#class-apierror)

### Methods

<a id="sdk-fromresponse"></a>

#### fromResponse()

```ts
static fromResponse(
   status, 
   body, 
   headers
): APIError;
```

Create the error subclass for an HTTP status code.

##### Parameters

###### status

`number`

###### body

`unknown`

###### headers

`Headers`

##### Returns

[`APIError`](#class-apierror)

##### Inherited from

[`APIError`](#class-apierror).[`fromResponse`](#class-apierror)
