# JavaScript SDK reference: Classes

[← JavaScript reference](README.md) · [JS SDK guide](../../11-sdk-javascript.md) · Official: <https://docs.typesafe.ai/sdk/javascript/api>

- [APIConnectionError](#class-apiconnectionerror)
- [APIError](#class-apierror)
- [APIPromise](#class-apipromise)
- [APITimeoutError](#class-apitimeouterror)
- [APIUserAbortError](#class-apiuseraborterror)
- [AuthenticationError](#class-authenticationerror)
- [BadRequestError](#class-badrequesterror)
- [Image](#class-image)
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

* [`TypeSafeError`](https://docs.typesafe.ai/sdk/javascript/api/classes/TypeSafeError)

### Extended by

* [`APITimeoutError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APITimeoutError)

### Constructors

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

[`TypeSafeError`](https://docs.typesafe.ai/sdk/javascript/api/classes/TypeSafeError).[`constructor`](https://docs.typesafe.ai/sdk/javascript/api/classes/TypeSafeError#sdk-constructor)



---

## Class: APIError

An unsuccessful HTTP response from the API.

### Extends

* [`TypeSafeError`](https://docs.typesafe.ai/sdk/javascript/api/classes/TypeSafeError)

### Extended by

* [`AuthenticationError`](https://docs.typesafe.ai/sdk/javascript/api/classes/AuthenticationError)
* [`BadRequestError`](https://docs.typesafe.ai/sdk/javascript/api/classes/BadRequestError)
* [`InternalServerError`](https://docs.typesafe.ai/sdk/javascript/api/classes/InternalServerError)
* [`NotFoundError`](https://docs.typesafe.ai/sdk/javascript/api/classes/NotFoundError)
* [`PermissionDeniedError`](https://docs.typesafe.ai/sdk/javascript/api/classes/PermissionDeniedError)
* [`RateLimitError`](https://docs.typesafe.ai/sdk/javascript/api/classes/RateLimitError)
* [`UnprocessableEntityError`](https://docs.typesafe.ai/sdk/javascript/api/classes/UnprocessableEntityError)

### Constructors

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

[`TypeSafeError`](https://docs.typesafe.ai/sdk/javascript/api/classes/TypeSafeError).[`constructor`](https://docs.typesafe.ai/sdk/javascript/api/classes/TypeSafeError#sdk-constructor)

### Properties

#### body

```ts
readonly body: unknown;
```

Parsed JSON, response text, or `undefined` for an empty body.

***

#### headers

```ts
readonly headers: Headers;
```

HTTP response headers.

***

#### requestId

```ts
readonly requestId: string | undefined;
```

Request ID from `x-typesafe-request-id`, or `undefined` when absent.

***

#### status

```ts
readonly status: number;
```

HTTP response status code.

### Methods

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

#### withResponse()

```ts
withResponse(): Promise<WithResponse<T>>;
```

Return the parsed result, HTTP response, and request ID.

##### Returns

`Promise`\<[`WithResponse`](https://docs.typesafe.ai/sdk/javascript/api/interfaces/WithResponse)\<`T`>>



---

## Class: APITimeoutError

The full response did not arrive within the timeout. A kind of `APIConnectionError`.

### Extends

* [`APIConnectionError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIConnectionError)

### Constructors

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

[`APIConnectionError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIConnectionError).[`constructor`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIConnectionError#sdk-constructor)

### Properties

#### timeoutMs

```ts
readonly timeoutMs: number;
```

Configured timeout in milliseconds.



---

## Class: APIUserAbortError

The caller cancelled the request through an `AbortSignal`.

### Extends

* [`TypeSafeError`](https://docs.typesafe.ai/sdk/javascript/api/classes/TypeSafeError)

### Constructors

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

[`TypeSafeError`](https://docs.typesafe.ai/sdk/javascript/api/classes/TypeSafeError).[`constructor`](https://docs.typesafe.ai/sdk/javascript/api/classes/TypeSafeError#sdk-constructor)



---

## Class: AuthenticationError

HTTP 401: authentication failed.

### Extends

* [`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError)

### Constructors

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

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`constructor`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-constructor)

### Properties

#### body

```ts
readonly body: unknown;
```

Parsed JSON, response text, or `undefined` for an empty body.

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`body`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-body)

***

#### headers

```ts
readonly headers: Headers;
```

HTTP response headers.

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`headers`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-headers)

***

#### requestId

```ts
readonly requestId: string | undefined;
```

Request ID from `x-typesafe-request-id`, or `undefined` when absent.

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`requestId`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-requestid)

***

#### status

```ts
readonly status: number;
```

HTTP response status code.

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`status`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-status)

### Methods

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

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError)

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`fromResponse`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-fromresponse)



---

## Class: BadRequestError

HTTP 400: the request is invalid.

### Extends

* [`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError)

### Constructors

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

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`constructor`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-constructor)

### Properties

#### body

```ts
readonly body: unknown;
```

Parsed JSON, response text, or `undefined` for an empty body.

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`body`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-body)

***

#### headers

```ts
readonly headers: Headers;
```

HTTP response headers.

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`headers`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-headers)

***

#### requestId

```ts
readonly requestId: string | undefined;
```

Request ID from `x-typesafe-request-id`, or `undefined` when absent.

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`requestId`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-requestid)

***

#### status

```ts
readonly status: number;
```

HTTP response status code.

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`status`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-status)

### Methods

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

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError)

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`fromResponse`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-fromresponse)



---

## Class: Image

A PNG or JPEG image asset, created by `image` or `Image.fromBase64`.

### Constructors

#### Constructor

```ts
new Image(data): Image;
```

##### Parameters

###### data

`ArrayBuffer` | `ArrayBufferView`\<`ArrayBufferLike`> | `Blob`

##### Returns

`Image`

##### Throws

`data` is empty or isn't file bytes or a `Blob`.

### Properties

#### data

```ts
readonly data: Uint8Array<ArrayBufferLike> | Blob;
```

The image file bytes, or a `Blob` read when the request is sent.

***

#### type

```ts
readonly type: "image" = "image";
```

### Methods

#### toJSON()

```ts
toJSON(): string;
```

The reference, written by `JSON.stringify` wherever the image appears in a request.

##### Returns

`string`

***

#### toString()

```ts
toString(): string;
```

The unique reference this image is sent under, for referencing it inside text.

##### Returns

`string`

***

#### fromBase64()

```ts
static fromBase64(text): Image;
```

Create an image from base64-encoded file bytes, decoding them now.

##### Parameters

###### text

`string`

The image file bytes, base64-encoded, without a `data:` URL prefix.

##### Returns

`Image`

##### Throws

`text` isn't valid base64 or decodes to no bytes.

##### Example

```ts
const photo = Image.fromBase64(upload.photoBase64);
```



---

## Class: InternalServerError

HTTP 5xx: the server failed to handle the request.

### Extends

* [`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError)

### Constructors

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

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`constructor`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-constructor)

### Properties

#### body

```ts
readonly body: unknown;
```

Parsed JSON, response text, or `undefined` for an empty body.

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`body`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-body)

***

#### headers

```ts
readonly headers: Headers;
```

HTTP response headers.

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`headers`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-headers)

***

#### requestId

```ts
readonly requestId: string | undefined;
```

Request ID from `x-typesafe-request-id`, or `undefined` when absent.

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`requestId`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-requestid)

***

#### status

```ts
readonly status: number;
```

HTTP response status code.

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`status`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-status)

### Methods

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

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError)

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`fromResponse`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-fromresponse)



---

## Class: NotFoundError

HTTP 404: the resource was not found.

### Extends

* [`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError)

### Constructors

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

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`constructor`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-constructor)

### Properties

#### body

```ts
readonly body: unknown;
```

Parsed JSON, response text, or `undefined` for an empty body.

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`body`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-body)

***

#### headers

```ts
readonly headers: Headers;
```

HTTP response headers.

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`headers`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-headers)

***

#### requestId

```ts
readonly requestId: string | undefined;
```

Request ID from `x-typesafe-request-id`, or `undefined` when absent.

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`requestId`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-requestid)

***

#### status

```ts
readonly status: number;
```

HTTP response status code.

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`status`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-status)

### Methods

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

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError)

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`fromResponse`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-fromresponse)



---

## Class: PermissionDeniedError

HTTP 403: access is denied.

### Extends

* [`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError)

### Constructors

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

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`constructor`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-constructor)

### Properties

#### body

```ts
readonly body: unknown;
```

Parsed JSON, response text, or `undefined` for an empty body.

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`body`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-body)

***

#### headers

```ts
readonly headers: Headers;
```

HTTP response headers.

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`headers`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-headers)

***

#### requestId

```ts
readonly requestId: string | undefined;
```

Request ID from `x-typesafe-request-id`, or `undefined` when absent.

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`requestId`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-requestid)

***

#### status

```ts
readonly status: number;
```

HTTP response status code.

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`status`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-status)

### Methods

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

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError)

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`fromResponse`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-fromresponse)



---

## Class: RateLimitError

HTTP 429: the rate limit was exceeded.

### Extends

* [`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError)

### Constructors

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

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`constructor`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-constructor)

### Properties

#### body

```ts
readonly body: unknown;
```

Parsed JSON, response text, or `undefined` for an empty body.

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`body`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-body)

***

#### headers

```ts
readonly headers: Headers;
```

HTTP response headers.

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`headers`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-headers)

***

#### requestId

```ts
readonly requestId: string | undefined;
```

Request ID from `x-typesafe-request-id`, or `undefined` when absent.

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`requestId`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-requestid)

***

#### retryAfterMs

```ts
readonly retryAfterMs: number | undefined;
```

Server retry delay in milliseconds, or `undefined` when absent or invalid.

***

#### status

```ts
readonly status: number;
```

HTTP response status code.

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`status`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-status)

### Methods

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

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError)

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`fromResponse`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-fromresponse)



---

## Class: TypeSafeClient

Client for the TypeSafe AI API.

### Constructors

#### Constructor

```ts
new TypeSafeClient(config?): TypeSafeClient;
```

Create a client for the TypeSafe AI API.

Explicit options take precedence over environment variables, then SDK defaults.
Empty or whitespace-only environment values are ignored.

##### Parameters

###### config?

[`TypeSafeClientConfig`](https://docs.typesafe.ai/sdk/javascript/api/interfaces/TypeSafeClientConfig) = `{}`

##### Returns

`TypeSafeClient`

##### Throws

The API key is missing, configuration is invalid, the runtime is
unsupported, or the runtime lacks the requested compression.

### Properties

#### baseURL

```ts
readonly baseURL: string;
```

API root with trailing slashes removed.

***

#### compression

```ts
readonly compression: Compression;
```

Request body compression, or `false` when bodies are sent uncompressed.

***

#### defaultHeaders

```ts
readonly defaultHeaders: Readonly<Record<string, string>>;
```

Additional headers sent with each request.

***

#### defaultModel

```ts
readonly defaultModel: string;
```

Model used when a request omits `model`.

***

#### fetch

```ts
readonly fetch: Fetch;
```

HTTP fetch implementation.

***

#### logger

```ts
readonly logger: Logger;
```

The configured logger, filtered to `logLevel`.

***

#### logLevel

```ts
readonly logLevel: LogLevel;
```

Configured log verbosity.

***

#### models

```ts
readonly models: Models;
```

The models available to the account.

***

#### retry

```ts
readonly retry: RetryPolicy;
```

Retry settings with constructor overrides applied.

***

#### timeout

```ts
readonly timeout: number;
```

Timeout per attempt in milliseconds.

### Methods

#### systemOne()

```ts
systemOne<Q>(request, options?): APIPromise<SystemOneResult<Q>>;
```

Answer named questions about text, structured state, or assets.

##### Type Parameters

###### Q

`Q` *extends* [`Questions`](https://docs.typesafe.ai/sdk/javascript/api/interfaces/Questions)

##### Parameters

###### request

[`SystemOneRequest`](https://docs.typesafe.ai/sdk/javascript/api/interfaces/SystemOneRequest)\<`Q`>

State, questions, an optional model override, and optional assets.
Assets in `state`, question content, or `withAssets` text are sent under their references.

###### options?

[`RequestOptions`](https://docs.typesafe.ai/sdk/javascript/api/interfaces/RequestOptions) = `{}`

Per-call timeout, retry, headers, and cancellation settings.

##### Returns

[`APIPromise`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIPromise)\<[`SystemOneResult`](https://docs.typesafe.ai/sdk/javascript/api/interfaces/SystemOneResult)\<`Q`>>

Answers typed by question name and criteria, with model and token usage. Every
failure below rejects the returned promise; the call itself doesn't throw.

##### Throws

State is `null` or omitted, questions are empty, score criteria are not
a list of at least two entries, choice criteria are not a nonempty map, a noul question has
neither instructions nor a described outcome, a string holds the reference of an asset not
attached to the request, a name in `assets` doesn't appear in the request, or a `Blob`
asset can't be read.

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

* [`APIConnectionError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIConnectionError)
* [`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError)
* [`APIUserAbortError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIUserAbortError)

### Constructors

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

* [`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError)

### Constructors

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

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`constructor`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-constructor)

### Properties

#### body

```ts
readonly body: unknown;
```

Parsed JSON, response text, or `undefined` for an empty body.

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`body`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-body)

***

#### headers

```ts
readonly headers: Headers;
```

HTTP response headers.

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`headers`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-headers)

***

#### requestId

```ts
readonly requestId: string | undefined;
```

Request ID from `x-typesafe-request-id`, or `undefined` when absent.

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`requestId`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-requestid)

***

#### status

```ts
readonly status: number;
```

HTTP response status code.

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`status`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-status)

### Methods

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

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError)

##### Inherited from

[`APIError`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError).[`fromResponse`](https://docs.typesafe.ai/sdk/javascript/api/classes/APIError#sdk-fromresponse)
