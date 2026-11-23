# JavaScript SDK reference: Functions

[← JavaScript reference](README.md) · [JS SDK guide](../../11-sdk-javascript.md) · Official: <https://docs.typesafe.ai/sdk/javascript/api>

- [box](#function-box)
- [choice](#function-choice)
- [image](#function-image)


---

## Function: box()

```ts
function box(instructions?): BoxQuestion;
```

Create a question that locates what its instructions describe in the request's image.
Use the `jev-preview` model for `box` questions.

### Parameters

#### instructions?

[`EntryType`](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/EntryType) = `null`

What to locate, as text, an asset, a JSON object or array; defaults to `null`.

### Returns

[`BoxQuestion`](https://docs.typesafe.ai/sdk/javascript/api/interfaces/BoxQuestion)

### Example

```ts
const { answers } = await client.systemOne({
  state: image(await openAsBlob("photo.jpg")),
  questions: { dog: box("The dog") },
  model: "jev-preview",
});
const { top, bottom, left, right } = answers.dog.box;
```



---

## Function: choice()

```ts
function choice<T>(instructions, criteria): ChoiceQuestion<T>;
```

Create a question that selects between named alternatives.

### Type Parameters

#### T

`T` *extends* [`ChoiceCriteria`](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/ChoiceCriteria)

### Parameters

#### instructions

[`EntryType`](https://docs.typesafe.ai/sdk/javascript/api/type-aliases/EntryType)

The question as text, a JSON object or array, or `null`.

#### criteria

`T`

Labels mapped to descriptions, or `null` for undescribed labels.

### Returns

[`ChoiceQuestion`](https://docs.typesafe.ai/sdk/javascript/api/interfaces/ChoiceQuestion)\<`T`>



---

## Function: image()

```ts
function image(data): Image;
```

Create an image asset for `systemOne`.

Place the image in `state` or question content, or interpolate it into a `withAssets`
tagged template; either way it is sent under its own reference, `String(image)`. To
reference it by a name of your choice, pass it in `assets` instead.

The image must be PNG or JPEG. The API detects the format from the file bytes and rejects
other formats with a `BadRequestError`. `Blob` data is read when the request is sent, and its
`type` is ignored. For base64 text, use `Image.fromBase64`.

### Parameters

#### data

`ArrayBuffer` | `ArrayBufferView`\<`ArrayBufferLike`> | `Blob`

Image file bytes, or a `Blob` such as a `File`.

### Returns

[`Image`](https://docs.typesafe.ai/sdk/javascript/api/classes/Image)

### Throws

`data` is empty or isn't file bytes or a `Blob`.

### Example

```ts
// Node: `openAsBlob` reads a file as a Blob and is exported by "node:fs".
const { answers } = await client.systemOne({
  state: image(await openAsBlob("product.png")),
  questions: { damaged: noul("Is the product damaged?") },
});
```
