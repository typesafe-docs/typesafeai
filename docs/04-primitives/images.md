# 4.6 Images

[← Primitives](README.md) · Source: <https://docs.typesafe.ai/images>

Jev reads PNG and JPEG images anywhere in a request: in `state`, in a question's `instructions`, or in `criteria`. Every question type accepts them, and [Box](box.md) questions need one.

> **Experimental.** TypeSafe labels images and Box "Dreamer-ready": fine for prototypes, not yet production-ready. The request format, the answers, and the limits can change between releases.

| | |
|---|---|
| **Turn on** | Send `TypeSafe-Danger-Zone-Images: true` on every request that has an image or a Box question. Without it, the request fails with `400`. |
| **Models** | Jev 1.14 and Jev 1.13 accept images. Box questions need Jev 1.14 (`jev-latest` or `jev-preview` today). |
| **Formats** | PNG or JPEG stills. Animated PNG, GIF, WebP, and HEIC are rejected; convert them first. |
| **Cost** | Images are billed as input tokens at the normal price, with no separate charge. `usage.input_tokens` includes them, and they count toward the context limits. TypeSafe hasn't published a formula for image token counts yet. |
| **Rate limits** | No separate limits for images. |

## Send an image with an SDK

Pass an image object where the image goes. The SDK uploads the file and writes a reference in its place.

**Python**

```python
from pathlib import Path

from typesafe_sdk import Choice, Image, Noul, TypeSafeClient

IMAGES = {"TypeSafe-Danger-Zone-Images": "true"}

with TypeSafeClient(headers=IMAGES) as client:  # or extra_headers=IMAGES per call
    result = client.system_one(
        state={"door": Image(Path("door-camera.jpg"))},
        questions={
            "person_present": Noul(instructions="Is there a person in `door`?"),
            "carrying": Choice(
                instructions="What is the person in `door` carrying?",
                criteria={
                    "package": "A box or parcel.",
                    "bag": "A bag of groceries or shopping.",
                    "nothing": "Empty hands.",
                },
            ),
        },
    )
    print(result.nouls["person_present"].noul, result.choices["carrying"].choice)
```

`Image` takes a path or raw bytes. `Image.from_base64(text)` takes base64, and `Image.from_pil(img, format="jpeg")` takes a Pillow image (install the `pil` extra). Reusing one `Image` object reuses the loaded file.

**TypeScript**

<!-- ts-check -->
```ts
import { openAsBlob } from "node:fs";
import { choice, image, noul, TypeSafeClient } from "@typesafe-ai/sdk";

const client = new TypeSafeClient({ defaultHeaders: { "TypeSafe-Danger-Zone-Images": "true" } });
const door = image(await openAsBlob("door-camera.jpg"));

const { answers } = await client.systemOne({
  state: { door },
  questions: {
    person_present: noul("Is there a person in `door`?"),
    carrying: choice("What is the person in `door` carrying?", {
      package: "A box or parcel.",
      bag: "A bag of groceries or shopping.",
      nothing: "Empty hands.",
    }),
  },
});
console.log(answers.person_present.noul, answers.carrying.choice);
```

`image()` takes a `Blob`, an `ArrayBuffer`, or a typed array such as a Node `Buffer`. `Image.fromBase64(text)` takes base64.

### Images inside text

To mention an image in the middle of a sentence, interpolate it. The SDK finds the reference and sends the image with the request.

**Python**

```python
from pathlib import Path

from typesafe_sdk import Image, Noul, TypeSafeClient

with TypeSafeClient(headers={"TypeSafe-Danger-Zone-Images": "true"}) as client:
    photo = Image(Path("product.png"))
    with client.attach_assets(photo):  # calls inside the block send `photo` wherever it's referenced
        damaged = client.system_one(
            f"Customer's return photo: {photo}",
            {"damaged": Noul(instructions="Is the product in the photo damaged?")},
        ).nouls["damaged"].noul
```

**TypeScript**

<!-- ts-check -->
```ts
import { openAsBlob } from "node:fs";
import { image, noul, TypeSafeClient, withAssets } from "@typesafe-ai/sdk";

const client = new TypeSafeClient({ defaultHeaders: { "TypeSafe-Danger-Zone-Images": "true" } });
const photo = image(await openAsBlob("product.png"));

const { answers } = await client.systemOne({
  state: withAssets`Customer's return photo: ${photo}`,
  questions: { damaged: noul("Is the product in the photo damaged?") },
});
```

## Where an image can go

| Place | Use it for | Note |
|---|---|---|
| `state` | The thing every question looks at: a photo, a scan, a sequence of frames | Sent once, seen by every question |
| `instructions` | A picture one question compares against ("the same dog as in this picture") | Sent with that question only, and **again for each question that uses it**. If several questions need it, put it in `state` and point at it by path. |
| `criteria` | Options or levels defined by example pictures | Choice option values, Score levels, and Noul `true`/`false` can all hold images. A Choice option **name** can't be an image; put it in the description. |

Point questions at images by path, like any other field: `` `photo` ``, `` `lineup[2]` ``, `` `frames[0].frame` ``. Answers that echo your criteria, such as a Score's `legend`, show the reference string, not the image.

Options defined by example pictures (references written as placeholders here):

```json
"gesture": {
  "type": "choice",
  "instructions": "Which gesture is the hand in `camera` making?",
  "criteria": {
    "thumbs_up": "0b6c51aa-thumb",
    "open_palm": {
      "description": "A hand held up with the palm facing the camera.",
      "examples": ["4fd2e7b9-palm1", "c83a0e15-palm2"]
    },
    "fist": "a7e94d02-fist",
    "none": "No hand, or a hand that matches none of the examples."
  }
}
```

Patterns from the official page: compare against a known picture, define options by example, ask what changed across a frame history, look closer only when needed, search a large image by tiling it into Choice options, and find where something is with a [Box](box.md).

## Over HTTP, without an SDK

Images go in a top-level `assets` map. Each key is a **reference** string. Write that string anywhere in `state`, `instructions`, or `criteria`, and the model sees the image in its place.

```json
{
  "model": "jev-latest",
  "state": { "photo": "a3f1c2e8-found" },
  "assets": {
    "a3f1c2e8-found": { "type": "image", "format": "jpg", "data_base64": "/9j/4AAQSkZJRg..." },
    "77b0d4a1-poster": { "type": "image", "format": "jpg", "data_base64": "/9j/4AAQSkZJRg..." }
  },
  "questions": {
    "same_dog": { "type": "noul", "instructions": "Is the dog in `photo` the same dog as in this picture: 77b0d4a1-poster?" },
    "has_collar": { "type": "noul", "instructions": "Is the dog in `photo` wearing a collar?" }
  }
}
```

| Asset field | Value |
|---|---|
| `type` | Optional; `"image"` if sent |
| `data_base64` | Standard base64 with `=` padding, no whitespace, no `data:` prefix. Required unless `part` is set. |
| `format` | `"png"`, `"jpg"`, or `"jpeg"` (lowercase). Required with `data_base64`. |
| `part` | Name of a multipart file part holding the image. Wins over `data_base64` if both are set. |

**Reference rules:**
- References match as plain text anywhere in the request's strings, so use something unique such as a UUID. A reference like `cat` would also match inside `category`.
- Every asset must be referenced, or the request fails with `400`.
- **Each use adds the image again** and counts toward the size limits.
- Object keys are never replaced.
- A reference is at most 1,024 bytes; all references together are at most 65,536 bytes.

**Multipart** is the better choice for large images, because base64 adds about 33% to the 32 MiB body limit:
- Put the JSON in a part named `request` with type `application/json`.
- Put each image in its own part, named by the asset's `part` field.
- Image parts may be `image/png`, `image/jpeg`, `application/octet-stream`, or untyped.

```bash
curl https://api.typesafe.ai/v1/systemone \
  -H "Authorization: Bearer $TYPESAFE_API_KEY" \
  -H "TypeSafe-Danger-Zone-Images: true" \
  -F 'request={
    "model": "jev-latest",
    "state": {"door": "a3f1c2e8-door"},
    "assets": {"a3f1c2e8-door": {"type": "image", "part": "door-photo"}},
    "questions": {
      "person_present": {"type": "noul", "instructions": "Is there a person in `door`?"}
    }
  };type=application/json' \
  -F 'door-photo=@door-camera.jpg;type=image/jpeg'
```

Base64 in JSON, from Python without the SDK:

```python
import base64
import os
import uuid

import requests


def image_asset(path: str) -> tuple[str, dict]:
    """A new reference and the asset entry for one image file."""
    fmt = "png" if path.lower().endswith(".png") else "jpg"
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    return str(uuid.uuid4()), {"type": "image", "format": fmt, "data_base64": data}


photo_key, photo = image_asset("door-camera.jpg")
response = requests.post(
    "https://api.typesafe.ai/v1/systemone",
    headers={"Authorization": f"Bearer {os.environ['TYPESAFE_API_KEY']}", "TypeSafe-Danger-Zone-Images": "true"},
    json={
        "model": "jev-latest",
        "state": {"door": photo_key},
        "assets": {photo_key: photo},
        "questions": {"person_present": {"type": "noul", "instructions": "Is there a person in `door`?"}},
    },
    timeout=30,
)
print(response.json()["answers"])
```

## Limits

Images outside these limits are rejected, never resized, and one rejected image fails the whole request.

| Limit | Value |
|---|---|
| Width and height | 280 to 1568 px each |
| Total pixels | 78,400 to 2,458,624 |
| File size | 16 MiB per image (after base64 decoding) |
| Request body | 32 MiB, including JSON, base64, and multipart framing. Compression doesn't raise it. |
| All images in a request | 32 MiB after processing (re-encoding can grow a file) |
| Expanded request | 32 MiB after every reference is replaced by its image. A 10 MiB image referenced 4 times is over. |

How many images fit also depends on the [context limits](../12-models.md#context-length).

## Preparing images

- **Resize** so the longest side is at most 1568 px. Upscale or pad anything under 280 px.
- **Rotate the pixels.** The API strips EXIF and doesn't apply EXIF orientation, so a sideways phone photo stays sideways.
- **Stills only.** Convert GIF, WebP, and HEIC to PNG or JPEG.
- **Prefer 8-bit baseline JPEG.** Re-save progressive JPEGs as baseline. If the API rejects a file that opens fine locally, re-export it.

```python
from PIL import Image as PILImage, ImageOps

with PILImage.open("photo.jpg") as original:
    img = ImageOps.exif_transpose(original)  # rotate the pixels upright
    img.thumbnail((1568, 1568))  # longest side at most 1568, same aspect ratio; only shrinks
    img.convert("RGB").save("photo-ready.jpg", "JPEG", quality=90)  # baseline JPEG
```

## Errors

| Status | Cause |
|---|---|
| `400` | Images not turned on: an image or Box question without the `TypeSafe-Danger-Zone-Images: true` header |
| `400` | An image or asset was rejected: not PNG/JPEG, damaged, animated, under the minimum size, never referenced, bad base64 or `format`, an empty reference, or a broken multipart rule |
| `400` `max_tokens_exceeded` | Images plus text exceed the context length |
| `413` | Over a size limit (file, dimensions, pixels, body, all images, expanded request, or reference length) |

When a request has several problems, only one is reported.

---

[← Box](box.md) · Next: [5. Confidence →](../05-confidence.md)
