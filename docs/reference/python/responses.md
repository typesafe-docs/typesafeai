# Answers and responses

[← Python reference](README.md) · [Python SDK guide](../../10-sdk-python.md) · Official: <https://docs.typesafe.ai/sdk/python/api/types/responses>


> Read answers, confidence scores, token usage, and available models returned by the TypeSafe API.

<a id="answers-and-responses"></a>

<a id="response"></a>

## `Response`

<a id="typesafe_sdk.SystemOneResponse"></a>

## `typesafe_sdk.SystemOneResponse`

`pydantic-model`

Bases: `Response`

Answers grouped by question type with model and usage metadata.

See [System One](https://docs.typesafe.ai/concepts/system-one) for details.

> 📝 **Note**
>
> **Show JSON schema:**
>
> <Accordion title="Details" id="sdk-disclosure-1">
> ```json theme={null}
> {
> "$defs": {
> "ChoiceAnswer": {
> "description": "A selected label and its probabilities.\n\nSee the [choice primitive](https://docs.typesafe.ai/primitives/choice) for details.",
> "properties": {
> "type": {
> "const": "choice",
> "default": "choice",
> "title": "Type",
> "type": "string"
> },
> "choice": {
> "description": "The name of the choice with the highest probability among the question's criteria.",
> "examples": [
> "angry"
> ],
> "title": "Choice",
> "type": "string"
> },
> "confidence": {
> "description": "Confidence in the selected choice, from 0 to 1. Higher values indicate greater certainty; use lower values to flag uncertain selections for review.",
> "examples": [
> 0.9
> ],
> "title": "Confidence",
> "type": "number"
> },
> "probabilities": {
> "additionalProperties": {
> "type": "number"
> },
> "description": "Probability of each choice in criteria, keyed by choice name, from 0 to 1. Shows how likely the alternatives are; values sum to approximately 1.",
> "examples": [
> {
> "angry": 0.8,
> "calm": 0.1,
> "excited": 0.1
> }
> ],
> "title": "Probabilities",
> "type": "object"
> }
> },
> "required": [
> "choice",
> "confidence",
> "probabilities"
> ],
> "title": "ChoiceAnswer",
> "type": "object"
> },
> "NoulAnswer": {
> "description": "A yes/no answer.\n\nSee the [noul primitive](https://docs.typesafe.ai/primitives/noul) for details.",
> "properties": {
> "type": {
> "const": "noul",
> "default": "noul",
> "title": "Type",
> "type": "string"
> },
> "noul": {
> "description": "Probability of a yes answer or a true statement, from 0 to 1. Values near 1 favor yes or true, values near 0 favor no or false, and values near 0.5 indicate uncertainty.",
> "examples": [
> 0.98
> ],
> "title": "Noul",
> "type": "number"
> }
> },
> "required": [
> "noul"
> ],
> "title": "NoulAnswer",
> "type": "object"
> },
> "ScoreAnswer": {
> "description": "An expected score with its rubric and probabilities.\n\nSee the [score primitive](https://docs.typesafe.ai/primitives/score) for details.",
> "properties": {
> "type": {
> "const": "score",
> "default": "score",
> "title": "Type",
> "type": "string"
> },
> "score": {
> "description": "Expected score: the probability-weighted average of the rubric levels. May fall between integer levels.",
> "examples": [
> 1.7
> ],
> "title": "Score",
> "type": "number"
> },
> "confidence": {
> "description": "Confidence in the score, from 0 to 1. Higher values indicate greater certainty; use lower values to flag uncertain ratings for review.",
> "examples": [
> 0.9
> ],
> "title": "Confidence",
> "type": "number"
> },
> "legend": {
> "additionalProperties": {
> "anyOf": [
> {
> "type": "string"
> },
> {
> "additionalProperties": true,
> "type": "object"
> },
> {
> "items": {},
> "type": "array"
> }
> ]
> },
> "title": "Legend",
> "type": "object"
> },
> "probabilities": {
> "additionalProperties": {
> "type": "number"
> },
> "title": "Probabilities",
> "type": "object"
> }
> },
> "required": [
> "score",
> "confidence",
> "legend",
> "probabilities"
> ],
> "title": "ScoreAnswer",
> "type": "object"
> },
> "Usage": {
> "description": "Token counts for a request, when reported by the API.",
> "properties": {
> "input_tokens": {
> "anyOf": [
> {
> "type": "integer"
> },
> {
> "type": "null"
> }
> ],
> "default": null,
> "title": "Input Tokens"
> },
> "output_tokens": {
> "anyOf": [
> {
> "type": "integer"
> },
> {
> "type": "null"
> }
> ],
> "default": null,
> "title": "Output Tokens"
> }
> },
> "title": "Usage",
> "type": "object"
> }
> },
> "description": "Answers grouped by question type with model and usage metadata.\n\nSee [System One](https://docs.typesafe.ai/concepts/system-one) for details.",
> "properties": {
> "model": {
> "title": "Model",
> "type": "string"
> },
> "usage": {
> "$ref": "#/$defs/Usage"
> },
> "answers": {
> "additionalProperties": {
> "discriminator": {
> "mapping": {
> "choice": "#/$defs/ChoiceAnswer",
> "noul": "#/$defs/NoulAnswer",
> "score": "#/$defs/ScoreAnswer"
> },
> "propertyName": "type"
> },
> "oneOf": [
> {
> "$ref": "#/$defs/NoulAnswer"
> },
> {
> "$ref": "#/$defs/ChoiceAnswer"
> },
> {
> "$ref": "#/$defs/ScoreAnswer"
> }
> ]
> },
> "title": "Answers",
> "type": "object"
> }
> },
> "required": [
> "model",
> "usage"
> ],
> "title": "SystemOneResponse",
> "type": "object"
> }
> ```
> </Accordion>

Config:

* `extra`: `ignore`
* `frozen`: `True`
* `strict`: `True`

Fields:

* `model` (`str`)
* `usage` (`Usage`)
* `answers` (`dict[str, Answer]`)

<a id="typesafe_sdk.SystemOneResponse.request_id"></a>

### `request_id`

`cached` `property`

```python
request_id: str
```

The `x-typesafe-request-id` response header.

<a id="typesafe_sdk.SystemOneResponse.raw_http_response"></a>

### `raw_http_response`

`property`

```python
raw_http_response: httpx2.Response
```

The underlying `httpx2.Response`, exposing status, headers, and body.

<a id="typesafe_sdk.SystemOneResponse.model_config"></a>

### `model_config`

`class-attribute` `instance-attribute`

```python
model_config = ConfigDict(
    extra="ignore", frozen=True, strict=True
)
```

<a id="typesafe_sdk.SystemOneResponse.model"></a>

### `model`

`pydantic-field`

```python
model: str
```

The model used to answer the request.

<a id="typesafe_sdk.SystemOneResponse.usage"></a>

### `usage`

`pydantic-field`

```python
usage: Usage
```

Token usage for the request.

<a id="typesafe_sdk.SystemOneResponse.answers"></a>

### `answers`

`pydantic-field`

```python
answers: dict[str, Answer]
```

All answer objects keyed by question name.

<a id="typesafe_sdk.SystemOneResponse.nouls"></a>

### `nouls`

`cached` `property`

```python
nouls: dict[str, NoulAnswer]
```

Yes/no answers keyed by question name.

<a id="typesafe_sdk.SystemOneResponse.choices"></a>

### `choices`

`cached` `property`

```python
choices: dict[str, ChoiceAnswer]
```

Choice answers keyed by question name.

<a id="typesafe_sdk.SystemOneResponse.scores"></a>

### `scores`

`cached` `property`

```python
scores: dict[str, ScoreAnswer]
```

Score answers keyed by question name.

<a id="typesafe_sdk.Usage"></a>

## `typesafe_sdk.Usage`

`pydantic-model`

Bases: `wire.Usage`

Token counts for a request, when reported by the API.

> 📝 **Note**
>
> **Show JSON schema:**
>
> <Accordion title="Details" id="sdk-disclosure-2">
> ```json theme={null}
> {
> "description": "Token counts for a request, when reported by the API.",
> "properties": {
> "input_tokens": {
> "anyOf": [
> {
> "type": "integer"
> },
> {
> "type": "null"
> }
> ],
> "default": null,
> "title": "Input Tokens"
> },
> "output_tokens": {
> "anyOf": [
> {
> "type": "integer"
> },
> {
> "type": "null"
> }
> ],
> "default": null,
> "title": "Output Tokens"
> }
> },
> "title": "Usage",
> "type": "object"
> }
> ```
> </Accordion>

Config:

* `extra`: `ignore`
* `frozen`: `True`
* `strict`: `True`

Fields:

* `input_tokens` (`int | None`)
* `output_tokens` (`int | None`)

<a id="typesafe_sdk.Usage.model_config"></a>

### `model_config`

`class-attribute` `instance-attribute`

```python
model_config = ConfigDict(
    extra="ignore", frozen=True, strict=True
)
```

<a id="typesafe_sdk.Usage.input_tokens"></a>

### `input_tokens`

`pydantic-field`

```python
input_tokens: int | None = None
```

Number of input tokens used, or `None` when the API did not report it.

<a id="typesafe_sdk.Usage.output_tokens"></a>

### `output_tokens`

`pydantic-field`

```python
output_tokens: int | None = None
```

Number of output tokens used, or `None` when the API did not report it.

<a id="answers"></a>

## `Answers`

<a id="typesafe_sdk.NoulAnswer"></a>

## `typesafe_sdk.NoulAnswer`

`pydantic-model`

Bases: `wire.NoulAnswer`

A yes/no answer.

See the [noul primitive](https://docs.typesafe.ai/primitives/noul) for details.

> 📝 **Note**
>
> **Show JSON schema:**
>
> <Accordion title="Details" id="sdk-disclosure-3">
> ```json theme={null}
> {
> "description": "A yes/no answer.\n\nSee the [noul primitive](https://docs.typesafe.ai/primitives/noul) for details.",
> "properties": {
> "type": {
> "const": "noul",
> "default": "noul",
> "title": "Type",
> "type": "string"
> },
> "noul": {
> "description": "Probability of a yes answer or a true statement, from 0 to 1. Values near 1 favor yes or true, values near 0 favor no or false, and values near 0.5 indicate uncertainty.",
> "examples": [
> 0.98
> ],
> "title": "Noul",
> "type": "number"
> }
> },
> "required": [
> "noul"
> ],
> "title": "NoulAnswer",
> "type": "object"
> }
> ```
> </Accordion>

Config:

* `extra`: `ignore`
* `frozen`: `True`
* `strict`: `True`

Fields:

* `noul` (`float`)
* `type` (`Literal['noul']`)

<a id="typesafe_sdk.NoulAnswer.noul"></a>

### `noul`

`pydantic-field`

```python
noul: float
```

Probability of a yes answer or a true statement, from 0 to 1. Values near 1 favor yes or true, values near 0 favor no or false, and values near 0.5 indicate uncertainty.

<a id="typesafe_sdk.NoulAnswer.model_config"></a>

### `model_config`

`class-attribute` `instance-attribute`

```python
model_config = ConfigDict(
    extra="ignore", frozen=True, strict=True
)
```

<a id="typesafe_sdk.ChoiceAnswer"></a>

## `typesafe_sdk.ChoiceAnswer`

`pydantic-model`

Bases: `wire.ChoiceAnswer`

A selected label and its probabilities.

See the [choice primitive](https://docs.typesafe.ai/primitives/choice) for details.

> 📝 **Note**
>
> **Show JSON schema:**
>
> <Accordion title="Details" id="sdk-disclosure-4">
> ```json theme={null}
> {
> "description": "A selected label and its probabilities.\n\nSee the [choice primitive](https://docs.typesafe.ai/primitives/choice) for details.",
> "properties": {
> "type": {
> "const": "choice",
> "default": "choice",
> "title": "Type",
> "type": "string"
> },
> "choice": {
> "description": "The name of the choice with the highest probability among the question's criteria.",
> "examples": [
> "angry"
> ],
> "title": "Choice",
> "type": "string"
> },
> "confidence": {
> "description": "Confidence in the selected choice, from 0 to 1. Higher values indicate greater certainty; use lower values to flag uncertain selections for review.",
> "examples": [
> 0.9
> ],
> "title": "Confidence",
> "type": "number"
> },
> "probabilities": {
> "additionalProperties": {
> "type": "number"
> },
> "description": "Probability of each choice in criteria, keyed by choice name, from 0 to 1. Shows how likely the alternatives are; values sum to approximately 1.",
> "examples": [
> {
> "angry": 0.8,
> "calm": 0.1,
> "excited": 0.1
> }
> ],
> "title": "Probabilities",
> "type": "object"
> }
> },
> "required": [
> "choice",
> "confidence",
> "probabilities"
> ],
> "title": "ChoiceAnswer",
> "type": "object"
> }
> ```
> </Accordion>

Config:

* `extra`: `ignore`
* `frozen`: `True`
* `strict`: `True`

Fields:

* `choice` (`str`)
* `confidence` (`float`)
* `probabilities` (`dict[str, float]`)
* `type` (`Literal['choice']`)

<a id="typesafe_sdk.ChoiceAnswer.choice"></a>

### `choice`

`pydantic-field`

```python
choice: str
```

The name of the choice with the highest probability among the question's criteria.

<a id="typesafe_sdk.ChoiceAnswer.confidence"></a>

### `confidence`

`pydantic-field`

```python
confidence: float
```

Confidence in the selected choice, from 0 to 1. Higher values indicate greater certainty; use lower values to flag uncertain selections for review.

<a id="typesafe_sdk.ChoiceAnswer.probabilities"></a>

### `probabilities`

`pydantic-field`

```python
probabilities: dict[str, float]
```

Probability of each choice in criteria, keyed by choice name, from 0 to 1. Shows how likely the alternatives are; values sum to approximately 1.

<a id="typesafe_sdk.ChoiceAnswer.model_config"></a>

### `model_config`

`class-attribute` `instance-attribute`

```python
model_config = ConfigDict(
    extra="ignore", frozen=True, strict=True
)
```

<a id="typesafe_sdk.ScoreAnswer"></a>

## `typesafe_sdk.ScoreAnswer`

`pydantic-model`

Bases: `wire.ScoreAnswer`

An expected score with its rubric and probabilities.

See the [score primitive](https://docs.typesafe.ai/primitives/score) for details.

> 📝 **Note**
>
> **Show JSON schema:**
>
> <Accordion title="Details" id="sdk-disclosure-5">
> ```json theme={null}
> {
> "description": "An expected score with its rubric and probabilities.\n\nSee the [score primitive](https://docs.typesafe.ai/primitives/score) for details.",
> "properties": {
> "type": {
> "const": "score",
> "default": "score",
> "title": "Type",
> "type": "string"
> },
> "score": {
> "description": "Expected score: the probability-weighted average of the rubric levels. May fall between integer levels.",
> "examples": [
> 1.7
> ],
> "title": "Score",
> "type": "number"
> },
> "confidence": {
> "description": "Confidence in the score, from 0 to 1. Higher values indicate greater certainty; use lower values to flag uncertain ratings for review.",
> "examples": [
> 0.9
> ],
> "title": "Confidence",
> "type": "number"
> },
> "legend": {
> "additionalProperties": {
> "anyOf": [
> {
> "type": "string"
> },
> {
> "additionalProperties": true,
> "type": "object"
> },
> {
> "items": {},
> "type": "array"
> }
> ]
> },
> "title": "Legend",
> "type": "object"
> },
> "probabilities": {
> "additionalProperties": {
> "type": "number"
> },
> "title": "Probabilities",
> "type": "object"
> }
> },
> "required": [
> "score",
> "confidence",
> "legend",
> "probabilities"
> ],
> "title": "ScoreAnswer",
> "type": "object"
> }
> ```
> </Accordion>

Config:

* `extra`: `ignore`
* `frozen`: `True`
* `strict`: `True`

Fields:

* `score` (`float`)
* `confidence` (`float`)
* `type` (`Literal['score']`)
* `legend` (`dict[int, str | dict[str, Any] | list[Any]]`)
* `probabilities` (`dict[int, float]`)

<a id="typesafe_sdk.ScoreAnswer.score"></a>

### `score`

`pydantic-field`

```python
score: float
```

Expected score: the probability-weighted average of the rubric levels. May fall between integer levels.

<a id="typesafe_sdk.ScoreAnswer.confidence"></a>

### `confidence`

`pydantic-field`

```python
confidence: float
```

Confidence in the score, from 0 to 1. Higher values indicate greater certainty; use lower values to flag uncertain ratings for review.

<a id="typesafe_sdk.ScoreAnswer.model_config"></a>

### `model_config`

`class-attribute` `instance-attribute`

```python
model_config = ConfigDict(
    extra="ignore", frozen=True, strict=True
)
```

<a id="typesafe_sdk.ScoreAnswer.legend"></a>

### `legend`

`pydantic-field`

```python
legend: dict[
    int, str | dict[str, Any] | list[Any]
]
```

Rubric descriptions keyed by integer score.

<a id="typesafe_sdk.ScoreAnswer.probabilities"></a>

### `probabilities`

`pydantic-field`

```python
probabilities: dict[int, float]
```

Probabilities keyed by integer score.

<a id="typesafe_sdk.Answer"></a>

## `typesafe_sdk.Answer`

`module-attribute`

```python
Answer: TypeAlias = Annotated[
    NoulAnswer | ChoiceAnswer | ScoreAnswer,
    Field(discriminator="type"),
]
```

An answer to a single question, identified by its `type`.

<a id="available-models"></a>

## Available models

<a id="typesafe_sdk.ListModelsResponse"></a>

## `typesafe_sdk.ListModelsResponse`

`pydantic-model`

Bases: `Response`

The models available to the account.

> 📝 **Note**
>
> **Show JSON schema:**
>
> <Accordion title="Details" id="sdk-disclosure-6">
> ```json theme={null}
> {
> "$defs": {
> "ModelMetadata": {
> "description": "Metadata describing a single available model.",
> "properties": {
> "name": {
> "title": "Name",
> "type": "string"
> },
> "description": {
> "title": "Description",
> "type": "string"
> },
> "release_date": {
> "title": "Release Date",
> "type": "string"
> }
> },
> "required": [
> "name",
> "description",
> "release_date"
> ],
> "title": "ModelMetadata",
> "type": "object"
> }
> },
> "description": "The models available to the account.",
> "properties": {
> "models": {
> "items": {
> "$ref": "#/$defs/ModelMetadata"
> },
> "title": "Models",
> "type": "array"
> }
> },
> "required": [
> "models"
> ],
> "title": "ListModelsResponse",
> "type": "object"
> }
> ```
> </Accordion>

Fields:

* `models` (`tuple[ModelMetadata, ...]`)

<a id="typesafe_sdk.ListModelsResponse.request_id"></a>

### `request_id`

`cached` `property`

```python
request_id: str
```

The `x-typesafe-request-id` response header.

<a id="typesafe_sdk.ListModelsResponse.raw_http_response"></a>

### `raw_http_response`

`property`

```python
raw_http_response: httpx2.Response
```

The underlying `httpx2.Response`, exposing status, headers, and body.

<a id="typesafe_sdk.ListModelsResponse.model_config"></a>

### `model_config`

`class-attribute` `instance-attribute`

```python
model_config = ConfigDict(
    extra="ignore", frozen=True, strict=True
)
```

<a id="typesafe_sdk.ListModelsResponse.models"></a>

### `models`

`pydantic-field`

```python
models: tuple[ModelMetadata, ...]
```

The available models.

<a id="typesafe_sdk.ModelMetadata"></a>

## `typesafe_sdk.ModelMetadata`

`pydantic-model`

Bases: `Schema`

Metadata describing a single available model.

> 📝 **Note**
>
> **Show JSON schema:**
>
> <Accordion title="Details" id="sdk-disclosure-7">
> ```json theme={null}
> {
> "description": "Metadata describing a single available model.",
> "properties": {
> "name": {
> "title": "Name",
> "type": "string"
> },
> "description": {
> "title": "Description",
> "type": "string"
> },
> "release_date": {
> "title": "Release Date",
> "type": "string"
> }
> },
> "required": [
> "name",
> "description",
> "release_date"
> ],
> "title": "ModelMetadata",
> "type": "object"
> }
> ```
> </Accordion>

Fields:

* `name` (`str`)
* `description` (`str`)
* `release_date` (`str`)

<a id="typesafe_sdk.ModelMetadata.name"></a>

### `name`

`pydantic-field`

```python
name: str
```

Model name or alias accepted by a request's model field.

<a id="typesafe_sdk.ModelMetadata.description"></a>

### `description`

`pydantic-field`

```python
description: str
```

Human-readable description of the model and its capabilities.

<a id="typesafe_sdk.ModelMetadata.release_date"></a>

### `release_date`

`pydantic-field`

```python
release_date: str
```

Model release date, formatted as YYYY-MM-DD.
