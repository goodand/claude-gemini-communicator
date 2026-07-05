# Disambiguation Examples

## Complete Output Template: "아바타" (Avatar)

**User Query:** "아바타 명확하게 설명해줘"

**Expected Full Output:**

---

[1] Polysemy-Tree:

```
아바타 (root) - 5 distinct signifieds identified
├─ [Contextual: Religious/Mythological]
│   └─ 아바타₁: 힌두교에서 신(특히 비슈누)의 지상 강림/육화
├─ [Contextual: Digital Technology]
│   ├─ [Sub: 3D Virtual Environment]
│   │   └─ 아바타₂: 가상 3D 환경에서 사용자를 대표하는 조작 가능 캐릭터
│   └─ [Sub: 2D UI Element]
│       └─ 아바타₃: 사용자 계정을 나타내는 프로필 이미지/아이콘
├─ [Denotation: Proper Noun - Entertainment]
│   └─ 아바타₄: 특정 작품 제목 (예: James Cameron 영화, Nickelodeon 애니메이션)
└─ [Metaphorical: Pejorative]
    └─ 아바타₅: 타인에 의해 조종되는 수동적 존재 (비유적 표현)
```

[2] Recursive-Disambiguation:

**[Branch: Contextual > Religious]**
```
아바타₁ → "신의 화신"

Decompose "신의 화신" into components:

├─ Component "신" - Identify ALL meanings:
│   ├─ 신₁ [Religious]: 종교적 초월적 존재 (deity)
│   │   - Definition: Transcendent being worshipped
│   │   - Context markers: "비슈누", "예배", "기도"
│   │
│   ├─ 신₂ [Temporal]: 새로움 (新, newness)
│   │   - Definition: Recently made or introduced
│   │   - Context markers: "신제품", "신기술"
│   │
│   └─ 신₃ [Physical]: 신체 (身, body)
│       - Definition: Physical structure of person
│       - Context markers: "건강", "운동"
│   
│   Context check for "신의 화신": Religious discourse
│   → 신₁ is the meaning used in this context
│   → Guides replacement: "deity" (appropriate for religious context)
│   → 신₂, 신₃ are documented but not used here
│   
│   신₁ → RECURSE: disambiguate("신₁", depth=2)
│       └─ Replacement: "deity" / "초월적-존재"
│           └─ Check "deity" monosemic? → Yes ✓
│           └─ [RESOLVED at depth 2] ✓
│
└─ Component "화신" - Identify ALL meanings:
    ├─ 화신₁ [Religious]: 신이 육체로 현현함 (incarnation)
    │   - Definition: Divine being in physical form
    │   - Context markers: "강림", "현현", "육화"
    │
    └─ 화신₂ [Metaphorical]: 특성의 전형적 표현 (embodiment)
        - Definition: Perfect example of quality
        - Context markers: "정의의", "악의"
    
    Context check for "신의 화신": Religious discourse
    → 화신₁ is the meaning used in this context
    → Guides replacement: "incarnation" (appropriate for religious context)
    → 화신₂ is documented but not used here
    
    화신₁ → RECURSE: disambiguate("화신₁", depth=2)
        └─ Replacement: "incarnation" / "육화"
            └─ Check "incarnation" monosemic? → Yes ✓
            └─ [RESOLVED at depth 2] ✓

Final: "deity's-incarnation" / "초월적-존재의-육화" [depth 2] ✓
All meanings documented, contextually appropriate ones resolved
```

**[Branch: Contextual > Digital > 3D Virtual]**
```
아바타₂ → Replacement attempts:
  Attempt 1: "가상-캐릭터" → "캐릭터" is polysemous, continue
  Attempt 2: "3D-사용자-표현체" → "표현체" needs checking
  Attempt 3: Not needed, Attempt 2 succeeded ✓

Decomposition of "3D-사용자-표현체":
├─ Component "3D" polysemous?
│   └─ No, monosemic (three-dimensional) [RESOLVED at depth 2] ✓
├─ Component "사용자" polysemous?
│   ├─ 사용자₁: user (person who uses)
│   └─ 사용자₂: consumer (person who consumes)
│   └─ Attempt 1: "user" → Monosemic in this context [RESOLVED at depth 3] ✓
└─ Component "표현체" polysemous?
    └─ Attempt 1: "representation" → Monosemic [RESOLVED at depth 3] ✓

Final: "3D-user-representation" [depth 3] ✓
```

**[Branch: Contextual > Digital > 2D UI]**
```
아바타₃ → "프로필-이미지"
├─ Component "프로필" polysemous?
│   ├─ 프로필₁: 측면 (profile view)
│   └─ 프로필₂: 개인 정보 요약 (profile summary)
│   └─ Resolution in context: "계정-정보" / "account-representation" [RESOLVED at depth 2] ✓
│
└─ Component "이미지" polysemous?
    ├─ 이미지₁: 시각적 표상 (visual representation)
    ├─ 이미지₂: 인상/평판 (impression/image)
    └─ 이미지₃: 심상 (mental image)
    └─ Resolution: "시각적-표상" / "graphic-icon" [RESOLVED at depth 2] ✓

Final: "계정-시각적-표상" / "profile-graphic-icon" [depth 2] ✓
```

**[Branch: Denotation > Proper Noun]**
```
아바타₄ → Proper noun usage
└─ Context-dependent specification needed:
    ├─ "James Cameron의 영화 '아바타'" (2009 film)
    ├─ "Nickelodeon 애니메이션 '아바타: 아앙의 전설'"
    └─ Other works titled "Avatar"
    
→ [TERMINAL - Proper noun requires context specification]
Note: These are INSTANCES of proper noun usage, not separate signifieds
```

**[Branch: Metaphorical]**
```
아바타₅ → "꼭두각시"
├─ Component "꼭두각시" polysemous?
│   └─ Single meaning: puppet controlled by strings [RESOLVED at depth 1] ✓
│
Alternative: "수동적-피조종자" / "passive-controlled-agent"
└─ [RESOLVED at depth 1] ✓

Final: "꼭두각시" or "passive-controlled-agent" [depth 1] ✓
```

[3] Contextual-Semantic-Expansion:

**아바타₁** [초월적-존재의-육화]:
- **Definition**: 힌두교 신화에서 신성한 존재(특히 비슈누)가 특정 목적을 위해 지상에 물리적 형태로 현현한 것
- **Domain**: Religious/mythological discourse, Hindu philosophy
- **Context markers**: "비슈누의", "신의 강림", "크리슈나", "라마"
- **Examples**:
  1. "크리슈나는 비슈누의 여덟 번째 아바타₁(육화)이다"
  2. "힌두 신화에서 아바타₁(신적 현현)는 세상의 질서를 회복하기 위해 나타난다"
- **Metaphorical link**: Religious concept → Digital representation (borrowed authority/representation concept)

**아바타₂** [3D-가상-사용자-표현체]:
- **Definition**: 3차원 가상환경(게임, 메타버스, VR)에서 사용자가 실시간으로 조작하는 디지털 신체 또는 캐릭터
- **Domain**: Gaming, virtual reality, metaverse platforms
- **Context markers**: "가상세계", "메타버스", "VRChat", "Second Life", "게임 캐릭터"
- **Examples**:
  1. "내 아바타₂(가상-캐릭터)를 커스터마이징해서 친구들과 만났다"
  2. "VR 게임에서 아바타₂(3D-표현체)를 통해 가상 공간을 탐험한다"
- **Metaphorical link**: From 아바타₁ (divine embodiment) → digital embodiment of user

**아바타₃** [프로필-그래픽-아이콘]:
- **Definition**: 온라인 플랫폼, 포럼, 소셜미디어에서 사용자 계정을 시각적으로 식별하는 정적/동적 2D 이미지
- **Domain**: Social media, forums, messaging apps, web platforms
- **Context markers**: "프로필 사진", "계정 이미지", "포럼", "SNS", "profile picture"
- **Examples**:
  1. "아바타₃(프로필 이미지)를 고양이 사진으로 바꿨어요"
  2. "게시판에서 아바타₃(계정 아이콘)으로 사용자를 구분한다"
- **Metaphorical link**: Simplified 2D version of 아바타₂ concept

**아바타₄** [작품명 "아바타" + 맥락]:
- **Definition**: "Avatar"라는 제목을 가진 특정 엔터테인먼트 작품의 고유명사
- **Domain**: Film, television, pop culture
- **Context markers**: "James Cameron", "영화", "Nickelodeon", "애니메이션", "아앙"
- **Examples**:
  1. "James Cameron 감독의 영화 '아바타₄' 보셨나요?"
  2. "Nickelodeon 애니메이션 '아바타₄: 아앙의 전설'은 훌륭한 작품이다"
- **Metaphorical link**: Title borrows from 아바타₁ (humans using Na'vi bodies / elemental avatar)

**아바타₅** [꼭두각시/수동적-피조종자]:
- **Definition**: 자신의 의지 없이 타인에 의해 조종당하는 수동적 존재 (비하적 은유)
- **Domain**: Political discourse, criticism, pejorative usage
- **Context markers**: "조종당하다", "꼭두각시", "수동적", "주체성 없는"
- **Examples**:
  1. "그는 배후 세력의 아바타₅(꼭두각시)에 불과하다"
  2. "주체적 판단 없이 아바타₅(타인 조종 도구)처럼 행동한다"
- **Metaphorical link**: From 아바타₂ (user-controlled character) → pejoratively controlled person

[4] Cross-Reference-Mapping:

- 아바타₁ ←[etymological_origin]→ All others: Sanskrit "avatāra" (descent) is root concept
- 아바타₂ ←[metaphorical_extension]← 아바타₁: Divine embodiment → Digital embodiment of user
- 아바타₃ ←[simplified_derivative]← 아바타₂: 3D virtual body → 2D visual identifier
- 아바타₄ ←[proper_noun_derivation]← 아바타₁: Concept borrowed as title (Cameron's film uses Na'vi bodies; anime features "the Avatar")
- 아바타₅ ←[pejorative_metaphor]← 아바타₂: User-controlled character → Negatively controlled person
- 아바타₂ ←[semantic_field_overlap]→ 아바타₃: Both represent users digitally, differ in dimensionality and interactivity

---

## Recursive Depth Demonstration: "신의 화신"

This example shows WHY replacement terms must be recursively checked.

```
Input: 아바타₁
Initial replacement: "신의 화신"

Level 1 Analysis:
"신의 화신" (proposed replacement)
│
├─ Component 1: "신" 
│   │
│   ├─ Is "신" monosemic? NO - has 3+ meanings
│   │
│   ├─ 신₁ [Religious]: 초월적 존재 (deity)
│   ├─ 신₂ [Temporal]: 새로움 (新, newness)  
│   └─ 신₃ [Physical]: 신체 (身, body)
│   │
│   ├─ Context: Religious → Select 신₁
│   │
│   └─ Replacement attempt for 신₁:
│       ├─ "deity" - monosemic in English ✓
│       └─ "초월적-존재" - monosemic ✓
│       └─ [RESOLVED at depth 2]
│
└─ Component 2: "화신"
    │
    ├─ Is "화신" monosemic? NO - has 2 meanings
    │
    ├─ 화신₁ [Religious]: 육체로 현현 (incarnation)
    └─ 화신₂ [Metaphorical]: 특성의 전형 (embodiment)
    │
    ├─ Context: Religious → Select 화신₁
    │
    └─ Replacement attempt for 화신₁:
        ├─ "incarnation" - monosemic ✓
        └─ "육화(肉化)" - monosemic ✓
        └─ [RESOLVED at depth 2]

Depth tracking:
- Original term: 아바타₁ (depth 0)
- First replacement: "신의 화신" (depth 1) - STILL POLYSEMOUS
- Component resolution: "deity's incarnation" (depth 2) - FULLY MONOSEMIC ✓

Final monosemic expression: "초월적-존재의-육화" / "deity's-physical-manifestation"
Recursion depth: 2
```

---

## Example: "bank" (Multiple Recursion Paths)

[1] Polysemy-Tree:

```
bank (root) - 4 distinct signifieds
├─ [Contextual: Finance]
│   └─ bank₁: 금융 기관
├─ [Contextual: Geography]
│   └─ bank₂: 강둑/제방
├─ [Contextual: Aviation]
│   └─ bank₃: 항공기의 기울어짐
└─ [Contextual: Storage]
    └─ bank₄: 저장소 (blood bank, data bank)
```

[2] Recursive-Disambiguation:

**[Branch: Finance]**
```
bank₁ → "financial institution"
├─ "financial" polysemous?
│   ├─ financial₁: relating to money/finance
│   └─ financial₂: fiscal (government revenue)
│   └─ Context: money-related [RESOLVED at depth 2] ✓
│
└─ "institution" polysemous?
    ├─ institution₁: established organization
    ├─ institution₂: custom/practice
    └─ institution₃: psychiatric facility
    └─ Context: organization [RESOLVED at depth 2] ✓

Final: "money-management-organization" [depth 2] ✓
```

**[Branch: Geography]**
```
bank₂ → "river bank" / "제방"
└─ "제방" monosemic in this context [RESOLVED at depth 1] ✓

Final: "제방" / "river-embankment" [depth 1] ✓
```

**[Branch: Aviation]**
```
bank₃ → "aircraft tilt" / "기울어짐"
└─ Both monosemic in aviation context [RESOLVED at depth 1] ✓

Final: "aircraft-lateral-tilt" [depth 1] ✓
```

**[Branch: Storage]**
```
bank₄ → "storage repository"
├─ "storage" polysemous?
│   └─ Relatively monosemic in this context [RESOLVED at depth 2] ✓
└─ "repository" polysemous?
    └─ Monosemic [RESOLVED at depth 2] ✓

Final: "collection-repository" [depth 2] ✓
```

[3] Contextual-Semantic-Expansion:

**bank₁** [money-management-organization]:
- **Definition**: Institution that accepts deposits, makes loans, and handles financial transactions
- **Domain**: Finance, economics, business
- **Context markers**: "account", "deposit", "loan", "interest", "ATM"
- **Examples**:
  1. "I need to go to the bank₁ (financial institution) to deposit this check"
  2. "The bank₁ (money-management-organization) approved my mortgage application"

**bank₂** [river-embankment]:
- **Definition**: Land alongside a body of water, or artificial structure preventing flooding
- **Domain**: Geography, hydrology, civil engineering
- **Context markers**: "river", "stream", "shore", "flooding", "embankment"
- **Examples**:
  1. "We sat on the bank₂ (river-embankment) and watched the sunset"
  2. "The bank₂ (제방) collapsed during the heavy rain"

**bank₃** [aircraft-lateral-tilt]:
- **Definition**: Rotation of aircraft around longitudinal axis during turns
- **Domain**: Aviation, aeronautics
- **Context markers**: "aircraft", "plane", "turn", "angle", "roll"
- **Examples**:
  1. "The pilot initiated a steep bank₃ (lateral-tilt) to the left"
  2. "During the bank₃ (aircraft-roll), passengers felt the g-forces"

**bank₄** [collection-repository]:
- **Definition**: Place or system for storing and distributing resources
- **Domain**: Medicine, data management, resource management
- **Context markers**: "blood", "data", "gene", "sperm", "store", "collection"
- **Examples**:
  1. "The hospital maintains a blood bank₄ (storage-repository)"
  2. "Scientists use the gene bank₄ (genetic-collection-repository) for research"

[4] Cross-Reference-Mapping:

- bank₁ ←[no_relation]→ bank₂: Homonyms (different etymologies)
- bank₃ ←[metaphorical_extension]← bank₂: Tilting like a riverbank slope
- bank₄ ←[metaphorical_extension]← bank₁: Storing resources like money storage
