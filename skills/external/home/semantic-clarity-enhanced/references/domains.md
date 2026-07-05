# Domain-Specific Disambiguation Patterns

## Table of Contents
1. Formal Logic & Mathematical Philosophy
2. Analytic Philosophy & Semantics
3. Patent Claims & Legal Language
4. Object-Oriented Programming
5. General Disambiguation Strategies

---

## 1. Formal Logic & Mathematical Philosophy

### Common Polysemous Terms

| Term | Signifieds | Monosemic Alternatives |
|------|-----------|------------------------|
| proposition | proposition₁ (logical statement with truth value)<br>proposition₂ (business proposal/suggestion) | statement₁, proposal₂ |
| valid | valid₁ (logical: conclusion follows from premises)<br>valid₂ (legal: legally acceptable)<br>valid₃ (general: reasonable) | logically-sound₁, lawful₂, reasonable₃ |
| sound | sound₁ (logic: valid + true premises)<br>sound₂ (physics: auditory waves)<br>sound₃ (health: healthy/intact) | deductively-valid-with-true-premises₁, auditory₂, healthy₃ |
| implication | implication₁ (logical connective →)<br>implication₂ (suggestion/hint) | conditional-connective₁, suggestion₂ |
| or | or₁ (inclusive disjunction ∨)<br>or₂ (exclusive disjunction ⊕) | inclusive-disjunction₁, exclusive-disjunction₂ |
| function | function₁ (mathematical mapping f: X → Y)<br>function₂ (purpose/role)<br>function₃ (programming subroutine) | mapping₁, purpose₂, subroutine₃ |

### Formalization Workflow with Disambiguation

```
Natural Language Statement
    ↓
[Step 1] Identify polysemous terms
    ↓
[Step 2] Disambiguate each term using subscripts
    ↓
[Step 3] Extract atomic propositions₁ (logical-statements)
    ↓
[Step 4] Assign symbols (P, Q, R...)
    ↓
[Step 5] Connect with logical operators₁ (connectives)
    ↓
[Step 6] Verify semantic₁ (meaning) preservation
```

**Example:**
- Ambiguous: "If it rains or snows, the game is cancelled"
- Disambiguated: "If it rains or₁ (inclusive-disjunction) snows, the game is cancelled"
- Formalized: (R ∨ S) → C

---

## 2. Analytic Philosophy & Semantics

### Common Polysemous Terms

| Term | Signifieds | Philosophical Context |
|------|-----------|---------------------|
| meaning | meaning₁ (Fregean Sinn: sense/mode of presentation)<br>meaning₂ (Fregean Bedeutung: reference/denotation)<br>meaning₃ (significance/importance) | Frege's distinction crucial |
| object | object₁ (physical concrete entity)<br>object₂ (abstract logical entity)<br>object₃ (intentional object of thought)<br>object₄ (goal/purpose) | Ontological categories |
| property | property₁ (attribute/characteristic)<br>property₂ (owned possession) | Universal vs particular |
| identity | identity₁ (numerical identity: x=x)<br>identity₂ (qualitative similarity)<br>identity₃ (personal self-continuity) | Leibniz's Law contexts |
| truth | truth₁ (correspondence theory)<br>truth₂ (coherence theory)<br>truth₃ (pragmatic utility) | Competing theories |
| possible | possible₁ (logically possible)<br>possible₂ (physically possible)<br>possible₃ (epistemically possible) | Modal distinctions |

### Clarification Strategy for Philosophical Analysis

**Use-Mention Distinction:**
```
Use₁: Employing a word to refer to something
  - "Snow is white" uses 'snow' to refer to frozen precipitation

Mention₁: Referring to the word itself
  - "'Snow' has four letters" mentions the word 'snow'
```

**Intensional vs Extensional Contexts:**
```
Extensional₁ (reference-based):
  - "The morning star is the evening star" (both refer to Venus)
  
Intensional₁ (meaning-based):
  - "John believes the morning star appears in the morning"
    (cannot substitute 'evening star' without changing truth value)
```

---

## 3. Patent Claims & Legal Language

### Common Polysemous Terms in Patent Law

| Term | Signifieds | Legal Implications |
|------|-----------|-------------------|
| comprising | comprising₁ (open-ended: includes but not limited to)<br>comprising₂ (general: containing) | Claim scope critical |
| consisting of | consisting₁ (closed: exactly these elements, nothing more) | Narrow interpretation |
| means | means₁ (mechanism/device/apparatus)<br>means₂ (method/process/way) | Means-plus-function |
| coupled | coupled₁ (directly physically connected)<br>coupled₂ (indirectly connected)<br>coupled₃ (operatively associated) | Connection specificity |
| substantially | substantially₁ (approximately within engineering tolerance)<br>substantially₂ (mostly/largely) | Claim breadth |
| adapted to | adapted₁ (configured/structured to)<br>adapted₂ (suitable for) | Structural vs functional |

### Claim Drafting Principles

1. **Define terms explicitly** in specification
2. **Maintain consistent terminology** throughout claims
3. **Use monosemic alternatives** where possible:
   - Replace "substantially" with specific tolerance (e.g., "within ±5%")
   - Replace "coupled" with "mechanically connected" or "electrically coupled"
4. **Antecedent basis protocol:**
   - First mention: "a processor"
   - Subsequent: "the processor" or "said processor"

**Example Disambiguation:**
```
Ambiguous claim:
"A device comprising a processor coupled to a memory"

Disambiguated options:
1. "A device comprising₁ (at least) a processor electrically coupled₁ (directly connected) to a memory"
2. "A device consisting₁ (exclusively) of a processor operatively coupled₃ (functionally associated) with a memory"
```

---

## 4. Object-Oriented Programming

### Common Polysemous Terms in OOP

| Term | Signifieds | Context |
|------|-----------|---------|
| object | object₁ (instance of class)<br>object₂ (base Object class)<br>object₃ (general thing) | Capitalize for class |
| class | class₁ (type definition/blueprint)<br>class₂ (CSS style class)<br>class₃ (general category) | Programming context |
| method | method₁ (instance method bound to object)<br>method₂ (class/static method)<br>method₃ (general approach) | Binding context |
| property | property₁ (instance variable/field)<br>property₂ (getter/setter accessor)<br>property₃ (characteristic) | Language-specific |
| type | type₁ (compile-time static type)<br>type₂ (runtime dynamic type)<br>type₃ (category) | Static vs dynamic |
| interface | interface₁ (contract/abstract type definition)<br>interface₂ (UI/user interface)<br>interface₃ (API boundary) | OOP vs general usage |
| inheritance | inheritance₁ (class extension: is-a)<br>inheritance₂ (property/estate transfer) | OOP relationship |
| polymorphism | polymorphism₁ (subtype: inheritance-based)<br>polymorphism₂ (parametric: generics)<br>polymorphism₃ (ad-hoc: overloading) | Type of polymorphism |

### Disambiguation Pattern for Technical Documentation

**Example 1: "object" disambiguation**
```
Ambiguous: "Create an object and call its method"

Disambiguated:
"Create an object₁ (instance of class User) and call its method₁ (instance method)"

Code context:
```python
user_instance = User()  # object₁ (instance)
user_instance.save()    # method₁ (instance method)
```

**Example 2: "property" disambiguation**
```
JavaScript context - property₂ (accessor):
```javascript
class Person {
  get name() { return this._name; }  // property₂ (getter accessor)
  set name(value) { this._name = value; }  // property₂ (setter accessor)
}
```

Python context - property₁ (attribute):
```python
class Person:
    def __init__(self):
        self.name = "John"  # property₁ (instance variable)
```

**Example 3: Type disambiguation**
```
TypeScript:
const value: string = getSomeValue();
// type₁ (compile-time static type): string
// type₂ (runtime dynamic type): might still be string

Python:
def process(data: list) -> None:
    # type₁ (declared type): list
    # type₂ (runtime type): could be any subtype of list
```

---

## 5. General Disambiguation Strategies

### Strategy 1: Context-Dependent Selection

When a term is polysemous but context clearly indicates meaning:

```
Procedure:
1. Identify all signifieds
2. Eliminate signifieds incompatible with context
3. If one signified remains → Use it with subscript
4. If multiple remain → Request clarification or provide all interpretations
```

**Example:**
- Statement: "The bank collapsed"
- Context markers: "river", "flooding"
- Selection: bank₂ (river-embankment) - not bank₁ (financial-institution)

### Strategy 2: Domain-Specific Defaults

Within specialized domains, establish default interpretations:

| Domain | Term | Default Signified |
|--------|------|------------------|
| Mathematics | "function" | function₁ (mapping) |
| Programming | "object" | object₁ (instance) |
| Law | "party" | party₁ (legal entity in case) |
| Medicine | "culture" | culture₁ (bacterial growth) |

### Strategy 3: Explicit Subscripting in Ambiguous Contexts

When context is insufficient, use subscript notation explicitly:

```
Ambiguous: "The property is important"

Options with subscripts:
1. "The property₁ (instance-variable) is important for state management"
2. "The property₂ (accessor-method) is important for encapsulation"
3. "The property₃ (characteristic) is important for understanding"
```

### Strategy 4: Recursive Component Analysis

For compound terms:

```
Term: "object-oriented programming"

Level 1:
- "object-oriented" (compound modifier)
- "programming" (noun)

Level 2 - Decompose "object-oriented":
- "object" → object₁ (instance-based)
- "oriented" → monosemic (directed toward)

Level 2 - Check "programming":
- programming₁ (writing code)
- programming₂ (TV scheduling)
→ Context: programming₁

Final: "instance-based code-writing paradigm"
```

### Strategy 5: Metaphor vs Literal Distinction

Identify when polysemy arises from metaphorical extension:

```
Original term: "mouse"
├─ mouse₁ [Literal]: small rodent mammal
└─ mouse₂ [Metaphorical]: computer input device
    └─ Mapping: rodent shape → device shape

Treatment:
- In zoology context: use mouse₁ (no disambiguation needed)
- In computing context: use mouse₂ or "pointing-device"
- In ambiguous context: specify with subscript
```

---

## Cross-Domain Disambiguation Decision Tree

```
Encounter polysemous term
    ↓
Is domain clearly established?
    ├─ Yes → Apply domain-specific default
    │         ↓
    │      Is default unambiguous in current sentence?
    │         ├─ Yes → Use term with subscript notation
    │         └─ No → Explicit monosemic replacement
    │
    └─ No → Check contextual markers
              ↓
           Markers present?
              ├─ Yes → Select appropriate signified + subscript
              └─ No → Provide all interpretations OR
                      Request user clarification OR
                      Use monosemic replacement
```

---

## Special Considerations

### Dead Metaphors
Terms whose metaphorical origin is no longer active in consciousness:
- "Comprehend" (Latin: "grasp together") - treat as monosemic in modern usage
- "Calculate" (Latin: "pebble") - treat as monosemic

### Technical Jargon Stabilization
Within specialized discourse, some polysemous terms achieve quasi-monosemic status:
- "Bandwidth" in networking contexts defaults to data-transfer-rate
- "Resolution" in digital imaging defaults to pixel-dimensions

### Cultural/Language-Specific Polysemy
Some polysemy exists only in specific languages:
- Korean "신" (god/new/body) - requires disambiguation in Korean, not in English
- English "bank" (financial/river) - requires disambiguation in English, less so in other languages
