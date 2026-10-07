# JavaScript SDK reference: Functions

[← JavaScript reference](README.md) · [JS SDK guide](../../11-sdk-javascript.md) · Official: <https://docs.typesafe.ai/sdk/javascript/api>

- [choice](#function-choice)
- [noul](#function-noul)
- [score](#function-score)


---

## Function: choice()

```ts
function choice<T>(instructions, criteria): ChoiceQuestion<T>;
```

Create a question that selects between named alternatives.

### Type Parameters

#### T

`T` *extends* [`ChoiceCriteria`](type-aliases.md#type-alias-choicecriteria)

### Parameters

#### instructions

[`EntryType`](type-aliases.md#type-alias-entrytype)

The question as text, a JSON object or array, or `null`.

#### criteria

`T`

Labels mapped to descriptions, or `null` for undescribed labels.

### Returns

[`ChoiceQuestion`](interfaces.md#interface-choicequestiont)\<`T`>



---

## Function: noul()

```ts
function noul(instructions?, criteria?): NoulQuestion;
```

Create a yes/no question with optional descriptions for either outcome.

### Parameters

#### instructions?

[`EntryType`](type-aliases.md#type-alias-entrytype) = `null`

The question as text, a JSON object or array; defaults to `null`.

#### criteria?

\| \{
`false?`: [`EntryType`](type-aliases.md#type-alias-entrytype);
`true?`: [`EntryType`](type-aliases.md#type-alias-entrytype);
}
\| `null`

Optional descriptions of the yes and no outcomes.

##### Type Literal

\{
`false?`: [`EntryType`](type-aliases.md#type-alias-entrytype);
`true?`: [`EntryType`](type-aliases.md#type-alias-entrytype);
}

Optional descriptions of the yes and no outcomes.

###### false?

[`EntryType`](type-aliases.md#type-alias-entrytype)

Description of the no outcome.

###### true?

[`EntryType`](type-aliases.md#type-alias-entrytype)

Description of the yes outcome.

***

`null`

### Returns

[`NoulQuestion`](interfaces.md#interface-noulquestion)



---

## Function: score()

```ts
function score<T>(instructions, criteria): ScoreQuestion<T>;
```

Create a score question using an ordered rubric.

### Type Parameters

#### T

`T` *extends* [`ScoreCriteria`](type-aliases.md#type-alias-scorecriteria)

### Parameters

#### instructions

[`EntryType`](type-aliases.md#type-alias-entrytype)

The question as text, a JSON object or array, or `null`.

#### criteria

`T`

At least two descriptions indexed by score from zero; entries may be `null`.

### Returns

[`ScoreQuestion`](interfaces.md#interface-scorequestiont)\<`T`>
