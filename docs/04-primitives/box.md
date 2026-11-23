# 4.5 Box

[← Primitives](README.md) · Source: <https://docs.typesafe.ai/primitives/box>

A **Box** finds where something is in an image and answers with a bounding box: the smallest rectangle that contains it. Examples: where is the damage on this car, where is the signature on this form, where is the coffee mug in this photo?

> **Needs Jev 1.14 and images.** Use `jev-latest` (which points to `jev-1.14.0`) or pin `jev-1.14.0`. Every request with a Box question needs the `TypeSafe-Danger-Zone-Images: true` header and an [image](images.md). Like images, Box is experimental ("Dreamer-ready"): the format and accuracy can change between releases.

## Request

A Box has `type: "box"` and `instructions`, which can be a short noun phrase. It takes **no `criteria`**. You can mix Box questions with Noul, Choice, and Score questions in the same request.

```bash
curl https://api.typesafe.ai/v1/systemone \
  -H "Authorization: Bearer $TYPESAFE_API_KEY" \
  -H "TypeSafe-Danger-Zone-Images: true" \
  -F 'request={
    "model": "jev-latest",
    "state": {"photo": "6e1d0b7c-kitchen"},
    "assets": {"6e1d0b7c-kitchen": {"type": "image", "part": "kitchen-photo"}},
    "questions": {
      "mug": {"type": "box", "instructions": "the coffee mug in `photo`"}
    }
  };type=application/json' \
  -F 'kitchen-photo=@kitchen.jpg;type=image/jpeg'
```

## Response

```json
{
  "model": "jev-1.14.0",
  "answers": {
    "mug": {
      "type": "box",
      "box": { "top": 0.25, "bottom": 0.82, "left": 0.44, "right": 0.84 },
      "confidence": 0.92
    }
  },
  "usage": { "input_tokens": 290, "output_tokens": 21 }
}
```

| Field | Meaning |
|---|---|
| `box.left`, `box.right` | Fractions of the image **width**, measured from the left edge, 0 to 1 |
| `box.top`, `box.bottom` | Fractions of the image **height**, measured from the top edge, 0 to 1 |
| `confidence` | 0 to 1, or `null` when the model doesn't provide it (both SDKs type it nullable). There are no `probabilities`, and no recommended threshold: tune one on your own images. |

`(0, 0)` is the top-left corner and `(1, 1)` the bottom-right, with `left < right` and `top < bottom`.

## A Box always answers, so ask whether the thing is there

There's no "not found" answer: a Box returns four edges even when the target isn't in the image. Put a Noul in the same request that asks whether it's there, and use the box only when the Noul says yes.

**Python**

```python
from pathlib import Path

from typesafe_sdk import Box, Image, Noul, TypeSafeClient

PRESENT_AT = 0.7  # starting point: tune on your own images

with TypeSafeClient(model="jev-1.14.0", headers={"TypeSafe-Danger-Zone-Images": "true"}) as client:
    result = client.system_one(
        state={"photo": Image(Path("kitchen.jpg"))},
        questions={
            "mug_visible": Noul(instructions="Is there a coffee mug in `photo`?"),
            "mug": Box(instructions="the coffee mug in `photo`"),
        },
    )

if result.nouls["mug_visible"].noul >= PRESENT_AT:
    mug = result.boxes["mug"]
    print(mug.box.left, mug.box.top, mug.box.right, mug.box.bottom, mug.confidence)
else:
    print("no mug in the photo")
```

**TypeScript**

<!-- ts-check -->
```ts
import { openAsBlob } from "node:fs";
import { box, image, noul, TypeSafeClient } from "@typesafe-ai/sdk";

const PRESENT_AT = 0.7; // starting point: tune on your own images

const client = new TypeSafeClient({ defaultModel: "jev-1.14.0", defaultHeaders: { "TypeSafe-Danger-Zone-Images": "true" } });
const photo = image(await openAsBlob("kitchen.jpg"));

const { answers } = await client.systemOne({
  state: { photo },
  questions: {
    mug_visible: noul("Is there a coffee mug in `photo`?"),
    mug: box("the coffee mug in `photo`"),
  },
});

if (answers.mug_visible.noul >= PRESENT_AT) {
  const { top, bottom, left, right } = answers.mug.box;
  console.log({ top, bottom, left, right, confidence: answers.mug.confidence });
} else {
  console.log("no mug in the photo");
}
```

## Reading a Box: from fractions to pixels

Multiply by the image size you sent. When confidence is low, pad the box before you crop, or ask again on a larger image or a closer crop.

**Python**

```python
from PIL import Image as PILImage

PAD = 0.05  # fraction of the image added on each side; tune for your images
MIN_CONFIDENCE = 0.6  # example threshold; tune it on your own images


def crop_box(path: str, edges: dict[str, float], confidence: float | None, out: str) -> None:
    if confidence is None or confidence < MIN_CONFIDENCE:
        edges = {
            "left": max(0.0, edges["left"] - PAD),
            "top": max(0.0, edges["top"] - PAD),
            "right": min(1.0, edges["right"] + PAD),
            "bottom": min(1.0, edges["bottom"] + PAD),
        }
    with PILImage.open(path) as image:
        width, height = image.size
        pixels = (
            round(edges["left"] * width),
            round(edges["top"] * height),
            round(edges["right"] * width),
            round(edges["bottom"] * height),
        )
        image.crop(pixels).save(out)


# crop_box("kitchen.jpg", mug.box.model_dump(), mug.confidence, "mug.jpg")
```

**TypeScript**

<!-- ts-check -->
```ts
import type { BoxCoordinates } from "@typesafe-ai/sdk";

const PAD = 0.05; // fraction of the image added on each side; tune for your images
const MIN_CONFIDENCE = 0.6; // example threshold; tune it on your own images

/** Pixel rectangle for an image of `width` × `height`, padded when confidence is low. */
function toPixels(b: BoxCoordinates, confidence: number | null, width: number, height: number) {
  const pad = (confidence ?? 0) < MIN_CONFIDENCE ? PAD : 0;
  const left = Math.max(0, b.left - pad), right = Math.min(1, b.right + pad);
  const top = Math.max(0, b.top - pad), bottom = Math.min(1, b.bottom + pad);
  return {
    x: Math.round(left * width),
    y: Math.round(top * height),
    width: Math.round((right - left) * width),
    height: Math.round((bottom - top) * height),
  };
}
```

## Writing Box questions

- **One box per question.** For several different things, ask one Box each. For several of the same thing, describe the one you want ("the leftmost mug"), or add a Choice for `none` / `one` / `several` and split the image.
- **Small targets in large images can be missed.** Find the right tile first (for example a Choice over image tiles), run the Box on that tile, then map its coordinates back to the full image.
- **The target can be a picture.** Put an image reference in `instructions`: `"the person in `photo` who matches this badge photo: 9a21c7d3-badge"`.

---

[← 4.4 Advanced: structure](advanced-structure.md) · Next: [4.6 Images →](images.md)
