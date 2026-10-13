# Questions

[← Python reference](README.md) · [Python SDK guide](../../10-sdk-python.md) · Official: <https://docs.typesafe.ai/sdk/python/api/types/questions>


> Provide state and ask yes/no, choice, and score questions using objects or dictionaries.

<a id="questions"></a>

<a id="state"></a>

## `State`

`state` is the text or JSON object you want to ask questions about. It cannot be `None`, but values inside an object may be `None`.

<a id="question-objects"></a>

## Question objects

Use `Noul`, `Choice`, and `Score` to define questions with named arguments.

<a id="typesafe_sdk.NoulCriteria"></a>

## `typesafe_sdk.NoulCriteria`

Bases: `TypedDict`

Optional descriptions of the yes and no outcomes.

See the [noul primitive](https://docs.typesafe.ai/primitives/noul) for details.

<a id="typesafe_sdk.NoulCriteria.true"></a>

### `true`

`instance-attribute`

```python
true: JSONContent | None
```

Description of the yes outcome as text, a JSON object, or an array; `None` leaves it undescribed.

<a id="typesafe_sdk.NoulCriteria.false"></a>

### `false`

`instance-attribute`

```python
false: JSONContent | None
```

Description of the no outcome as text, a JSON object, or an array; `None` leaves it undescribed.

<a id="typesafe_sdk.Noul"></a>

## `typesafe_sdk.Noul`

`pydantic-model`

**Implementation**

```python
Noul(**data: Any)
```

**Overload 1**

```python
Noul(
    *,
    type: Literal["noul"] = ...,
    instructions: JSONContent,
    criteria: NoulCriteria | None = ...,
)
```

**Overload 2**

```python
Noul(
    *,
    type: Literal["noul"] = ...,
    instructions: None = ...,
    criteria: _DescribedTrue | _DescribedFalse,
)
```

Bases: `_Question`, `wire.NoulQuestion`

A yes/no question with optional descriptions for either outcome.

See the [noul primitive](https://docs.typesafe.ai/primitives/noul) for details.

> 📝 **Note**
>
> **Show JSON schema:**
>
> <Accordion title="Details" id="sdk-disclosure-1">
> ```json theme={null}
> {
> "$defs": {
> "JSONContent": {
> "anyOf": [
> {
> "type": "string"
> },
> {
> "additionalProperties": {
> "anyOf": [
> {
> "$ref": "#/$defs/JSONValue"
> },
> {
> "type": "null"
> }
> ]
> },
> "type": "object"
> },
> {
> "items": {
> "anyOf": [
> {
> "$ref": "#/$defs/JSONValue"
> },
> {
> "type": "null"
> }
> ]
> },
> "type": "array"
> }
> ]
> },
> "JSONValue": {
> "anyOf": [
> {
> "type": "string"
> },
> {
> "type": "integer"
> },
> {
> "type": "number"
> },
> {
> "type": "boolean"
> },
> {
> "items": {
> "anyOf": [
> {
> "$ref": "#/$defs/JSONValue"
> },
> {
> "type": "null"
> }
> ]
> },
> "type": "array"
> },
> {
> "additionalProperties": {
> "anyOf": [
> {
> "$ref": "#/$defs/JSONValue"
> },
> {
> "type": "null"
> }
> ]
> },
> "type": "object"
> }
> ]
> },
> "NoulCriteria": {
> "additionalProperties": false,
> "description": "Optional descriptions of the yes and no outcomes.\n\nSee the [noul primitive](https://docs.typesafe.ai/primitives/noul) for details.",
> "properties": {
> "true": {
> "anyOf": [
> {
> "$ref": "#/$defs/JSONContent"
> },
> {
> "type": "null"
> }
> ]
> },
> "false": {
> "anyOf": [
> {
> "$ref": "#/$defs/JSONContent"
> },
> {
> "type": "null"
> }
> ]
> }
> },
> "title": "NoulCriteria",
> "type": "object"
> }
> },
> "additionalProperties": false,
> "description": "A yes/no question with optional descriptions for either outcome.\n\nSee the [noul primitive](https://docs.typesafe.ai/primitives/noul) for details.",
> "properties": {
> "type": {
> "const": "noul",
> "default": "noul",
> "title": "Type",
> "type": "string"
> },
> "instructions": {
> "anyOf": [
> {
> "$ref": "#/$defs/JSONContent"
> },
> {
> "type": "null"
> }
> ],
> "default": null
> },
> "criteria": {
> "anyOf": [
> {
> "$ref": "#/$defs/NoulCriteria"
> },
> {
> "type": "null"
> }
> ],
> "default": null
> }
> },
> "title": "Noul",
> "type": "object"
> }
> ```
> </Accordion>

Fields:

* `type` (`Literal['noul']`)
* `instructions` (`JSONContent | None`)
* `criteria` (`NoulCriteria | None`)

<a id="typesafe_sdk.Noul.instructions"></a>

### `instructions`

`pydantic-field`

```python
instructions: JSONContent | None = None
```

The question to ask, expressed as text, a JSON object, or an array; optional when `criteria` describes an outcome.

<a id="typesafe_sdk.Noul.criteria"></a>

### `criteria`

`pydantic-field`

```python
criteria: NoulCriteria | None = None
```

Optional descriptions of the yes and no outcomes; required when `instructions` is `None`.

<a id="typesafe_sdk.Choice"></a>

## `typesafe_sdk.Choice`

`pydantic-model`

Bases: `_Question`, `wire.ChoiceQuestion`

A question that selects between named alternatives.

See the [choice primitive](https://docs.typesafe.ai/primitives/choice) for details.

> 📝 **Note**
>
> **Show JSON schema:**
>
> <Accordion title="Details" id="sdk-disclosure-2">
> ```json theme={null}
> {
> "$defs": {
> "JSONContent": {
> "anyOf": [
> {
> "type": "string"
> },
> {
> "additionalProperties": {
> "anyOf": [
> {
> "$ref": "#/$defs/JSONValue"
> },
> {
> "type": "null"
> }
> ]
> },
> "type": "object"
> },
> {
> "items": {
> "anyOf": [
> {
> "$ref": "#/$defs/JSONValue"
> },
> {
> "type": "null"
> }
> ]
> },
> "type": "array"
> }
> ]
> },
> "JSONValue": {
> "anyOf": [
> {
> "type": "string"
> },
> {
> "type": "integer"
> },
> {
> "type": "number"
> },
> {
> "type": "boolean"
> },
> {
> "items": {
> "anyOf": [
> {
> "$ref": "#/$defs/JSONValue"
> },
> {
> "type": "null"
> }
> ]
> },
> "type": "array"
> },
> {
> "additionalProperties": {
> "anyOf": [
> {
> "$ref": "#/$defs/JSONValue"
> },
> {
> "type": "null"
> }
> ]
> },
> "type": "object"
> }
> ]
> }
> },
> "additionalProperties": false,
> "description": "A question that selects between named alternatives.\n\nSee the [choice primitive](https://docs.typesafe.ai/primitives/choice) for details.",
> "properties": {
> "type": {
> "const": "choice",
> "default": "choice",
> "title": "Type",
> "type": "string"
> },
> "instructions": {
> "anyOf": [
> {
> "$ref": "#/$defs/JSONContent"
> },
> {
> "type": "null"
> }
> ],
> "default": null
> },
> "criteria": {
> "additionalProperties": {
> "anyOf": [
> {
> "$ref": "#/$defs/JSONContent"
> },
> {
> "type": "null"
> }
> ]
> },
> "title": "Criteria",
> "type": "object"
> }
> },
> "required": [
> "criteria"
> ],
> "title": "Choice",
> "type": "object"
> }
> ```
> </Accordion>

Fields:

* `type` (`Literal['choice']`)
* `criteria` (`Mapping[str, JSONContent | None]`)
* `instructions` (`JSONContent | None`)

<a id="typesafe_sdk.Choice.criteria"></a>

### `criteria`

`pydantic-field`

```python
criteria: Mapping[str, JSONContent | None]
```

A nonempty mapping of labels to text, object, or array descriptions, or `None` for undescribed labels.

<a id="typesafe_sdk.Choice.instructions"></a>

### `instructions`

`pydantic-field`

```python
instructions: JSONContent | None = None
```

The question to ask, expressed as text, a JSON object, or an array; optional.

<a id="typesafe_sdk.Score"></a>

## `typesafe_sdk.Score`

`pydantic-model`

Bases: `_Question`, `wire.ScoreQuestion`

A question that assigns a score using an ordered rubric.

See the [score primitive](https://docs.typesafe.ai/primitives/score) for details.

> 📝 **Note**
>
> **Show JSON schema:**
>
> <Accordion title="Details" id="sdk-disclosure-3">
> ```json theme={null}
> {
> "$defs": {
> "JSONContent": {
> "anyOf": [
> {
> "type": "string"
> },
> {
> "additionalProperties": {
> "anyOf": [
> {
> "$ref": "#/$defs/JSONValue"
> },
> {
> "type": "null"
> }
> ]
> },
> "type": "object"
> },
> {
> "items": {
> "anyOf": [
> {
> "$ref": "#/$defs/JSONValue"
> },
> {
> "type": "null"
> }
> ]
> },
> "type": "array"
> }
> ]
> },
> "JSONValue": {
> "anyOf": [
> {
> "type": "string"
> },
> {
> "type": "integer"
> },
> {
> "type": "number"
> },
> {
> "type": "boolean"
> },
> {
> "items": {
> "anyOf": [
> {
> "$ref": "#/$defs/JSONValue"
> },
> {
> "type": "null"
> }
> ]
> },
> "type": "array"
> },
> {
> "additionalProperties": {
> "anyOf": [
> {
> "$ref": "#/$defs/JSONValue"
> },
> {
> "type": "null"
> }
> ]
> },
> "type": "object"
> }
> ]
> }
> },
> "additionalProperties": false,
> "description": "A question that assigns a score using an ordered rubric.\n\nSee the [score primitive](https://docs.typesafe.ai/primitives/score) for details.",
> "properties": {
> "type": {
> "const": "score",
> "default": "score",
> "title": "Type",
> "type": "string"
> },
> "instructions": {
> "anyOf": [
> {
> "$ref": "#/$defs/JSONContent"
> },
> {
> "type": "null"
> }
> ],
> "default": null
> },
> "criteria": {
> "items": {
> "$ref": "#/$defs/JSONContent"
> },
> "minItems": 1,
> "title": "Criteria",
> "type": "array"
> }
> },
> "required": [
> "criteria"
> ],
> "title": "Score",
> "type": "object"
> }
> ```
> </Accordion>

Fields:

* `type` (`Literal['score']`)
* `criteria` (`Sequence[JSONContent]`)
* `instructions` (`JSONContent | None`)

<a id="typesafe_sdk.Score.criteria"></a>

### `criteria`

`pydantic-field`

```python
criteria: Sequence[JSONContent]
```

A nonempty, ordered list of text, object, or array descriptions, one per score from zero.

<a id="typesafe_sdk.Score.instructions"></a>

### `instructions`

`pydantic-field`

```python
instructions: JSONContent | None = None
```

The question to ask, expressed as text, a JSON object, or an array; optional.

<a id="typesafe_sdk.Question"></a>

## `typesafe_sdk.Question`

`module-attribute`

```python
Question: TypeAlias = (
    Noul | Choice | Score | QuestionModel
)
```

A question object or question dictionary.

<a id="typesafe_sdk.Questions"></a>

## `typesafe_sdk.Questions`

`module-attribute`

```python
Questions: TypeAlias = Mapping[str, Question]
```

Question inputs keyed by the names used to identify their answers.

<a id="question-dictionaries"></a>

## Question dictionaries

Question dictionaries include a `type` key: `"noul"`, `"choice"`, or `"score"`. You can mix dictionaries and question objects in the same request.

<a id="typesafe_sdk.NoulModel"></a>

## `typesafe_sdk.NoulModel`

Bases: `TypedDict`

A yes/no question dictionary with `type="noul"`.

See the [noul primitive](https://docs.typesafe.ai/primitives/noul) for details.

<a id="typesafe_sdk.NoulModel.type"></a>

### `type`

`instance-attribute`

```python
type: Literal['noul']
```

<a id="typesafe_sdk.NoulModel.instructions"></a>

### `instructions`

`instance-attribute`

```python
instructions: NotRequired[JSONContent | None]
```

The question to ask, expressed as text, a JSON object, or an array; optional when `criteria` describes an outcome.

<a id="typesafe_sdk.NoulModel.criteria"></a>

### `criteria`

`instance-attribute`

```python
criteria: NotRequired[NoulCriteria | None]
```

Optional descriptions of the yes and no outcomes; required when `instructions` is `None`.

<a id="typesafe_sdk.ChoiceModel"></a>

## `typesafe_sdk.ChoiceModel`

Bases: `TypedDict`

A choice question dictionary with `type="choice"`.

See the [choice primitive](https://docs.typesafe.ai/primitives/choice) for details.

<a id="typesafe_sdk.ChoiceModel.type"></a>

### `type`

`instance-attribute`

```python
type: Literal['choice']
```

<a id="typesafe_sdk.ChoiceModel.instructions"></a>

### `instructions`

`instance-attribute`

```python
instructions: NotRequired[JSONContent | None]
```

The question to ask, expressed as text, a JSON object, or an array; optional.

<a id="typesafe_sdk.ChoiceModel.criteria"></a>

### `criteria`

`instance-attribute`

```python
criteria: Mapping[str, JSONContent | None]
```

A nonempty mapping of labels to text, object, or array descriptions, or `None` for undescribed labels.

<a id="typesafe_sdk.ScoreModel"></a>

## `typesafe_sdk.ScoreModel`

Bases: `TypedDict`

A score question dictionary with `type="score"`.

See the [score primitive](https://docs.typesafe.ai/primitives/score) for details.

<a id="typesafe_sdk.ScoreModel.type"></a>

### `type`

`instance-attribute`

```python
type: Literal['score']
```

<a id="typesafe_sdk.ScoreModel.instructions"></a>

### `instructions`

`instance-attribute`

```python
instructions: NotRequired[JSONContent | None]
```

The question to ask, expressed as text, a JSON object, or an array; optional.

<a id="typesafe_sdk.ScoreModel.criteria"></a>

### `criteria`

`instance-attribute`

```python
criteria: Sequence[JSONContent]
```

A nonempty, ordered list of text, object, or array descriptions, one per score from zero.

<a id="typesafe_sdk.QuestionModel"></a>

## `typesafe_sdk.QuestionModel`

`module-attribute`

```python
QuestionModel: TypeAlias = (
    NoulModel | ChoiceModel | ScoreModel
)
```

A question dictionary identified by its `type` key.
