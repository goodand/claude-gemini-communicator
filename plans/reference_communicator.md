 핵심은 **7가지 블록이 서로 어떻게 얽히는지**와, 그중 **memory/storage를 어떻게 설계하느냐**야. [systemdesignhandbook](https://www.systemdesignhandbook.com/guides/design-a-chat-system/)

***

## 1. 7개 컴포넌트의 역할 관계

각 블록을 “딱 한 줄”로 정리하면:

- **Message 구조**: 시스템을 오가는 모든 발화를 담는 공통 포맷.  
- **Agent / Model Registry**: 어떤 LLM/에이전트가 있는지, 어떤 역할/모델을 쓰는지의 목록.  
- **Scheduler**: “지금 이 턴에 어떤 에이전트들이 참여해야 하는지”를 결정하는 **두뇌**.  
- **Router**: Scheduler가 고른 대상에게 실제로 메시지를 전달하고, 결과를 다시 수집하는 **배선**.  
- **terminal**: 사용자 I/O (입력 루프 + 컬러 출력).  
- **memory / Storage**: 모든 Message·세션·요약 등 상태를 보존하고, 일부를 LLM 컨텍스트로 재활용. [mastra](https://mastra.ai/docs/memory/message-history)
- **Config**: 모드, 라우팅 규칙, 각 에이전트의 역할/우선순위 등 실행 전략을 정의하는 설정.

실제 구현에서는 `Scheduler`가 **어떤 에이전트에게 보낼지 + 어떤 컨텍스트를 넘길지**를 정하고, `Router`가 **각 API(Gemini, Claude 등)를 호출하고 응답을 Message로 되돌리는 역할**을 맡는 구조가 깔끔해. [arxiv](https://arxiv.org/abs/2507.06520)

***

## 2. Memory / Storage를 더 구체화

멀티 LLM Team Mode에서 메모리는 크게 세 층으로 나눌 수 있어:

1. **Message History (단순 로그)** – 각 세션의 모든 메시지. [systemdesignhandbook](https://www.systemdesignhandbook.com/guides/design-a-chat-system/)
2. **Conversation Summary / Condensed Context (요약 메모리)** – 긴 대화를 압축한 문자열 또는 구조체. [js.langchaincn](https://js.langchaincn.com/docs/modules/memory/examples/conversation_summary)
3. **Procedural Memory (LEGOMem 스타일 재사용 지식)** – 과거 성공적인 세션에서 추출한 “계획·토론 패턴”을 재사용. [arxiv](https://arxiv.org/html/2510.04851v1)

### 2‑1. 기본 Message Store

가장 기본은 “채팅 시스템”과 똑같이, 세션별로 메시지 배열을 저장하는 것. [trueconf](https://trueconf.com/blog/reviews-comparisons/chat-app-system-design)

```ts
interface Session {
  id: string;
  title: string;
  createdAt: number;
  mode: 'broadcast' | 'debate' | 'relay' | 'report';
  participants: string[]; // ['user','gemini','claude']
}

interface Message {
  id: string;
  sessionId: string;
  senderId: string;
  recipientId: string;
  role: 'user' | 'agent' | 'system';
  modelName?: string;
  content: string;
  turnIndex: number;
  createdAt: number;
  parentMessageId?: string;
}

type MessageStore = {
  [sessionId: string]: Message[];
};
```

- “채팅 시스템 설계”에서 말하는 것처럼, **핫 스토리지(최근 메시지)**는 메모리/빠른 DB, **콜드 스토리지(오래된 기록)**는 파일·객체 스토리지로 나눌 수 있음. [trueconf](https://trueconf.com/blog/reviews-comparisons/chat-app-system-design)
- Team Mode 초기 버전이라면, in‑memory + JSON 파일 dump 정도로 시작해도 충분해.

### 2‑2. Conversation Summary Memory

토큰 한계를 고려하면, LLM에 매번 “전체 히스토리”를 넣을 수는 없어서, LangChain의 `ConversationSummaryMemory`처럼 “요약 문자열”을 별도로 관리하는 패턴이 유용해. [js.langchaincn](https://js.langchaincn.com/docs/modules/memory/examples/conversation_summary)

```ts
interface SessionMemory {
  sessionId: string;
  summary: string;         // 지금까지 대화 요약
  lastSummarizedTurn: number;
}
```

핵심 아이디어:

- 매 N턴마다(예: 10턴마다) `MessageStore[sessionId]`의 새 메시지들을 LLM에 넘겨 **요약 업데이트**를 생성. [js.langchaincn](https://js.langchaincn.com/docs/modules/memory/examples/conversation_summary)
- LLM 호출할 때는:
  - `summary` (전역 맥락)  
  - 마지막 k개의 실제 메시지 (로컬 디테일)  
  를 함께 넣어서 프롬프트를 구성. [mastra](https://mastra.ai/docs/memory/message-history)

이렇게 하면, memory는 “**전체 이력 → 요약 + 최근 로그**”로 분해되고, 각 LLM이 동일한 압축 맥락을 공유하게 됨.

### 2‑3. Procedural Memory (선택 사항, 고급)

LEGOMem처럼 과거 세션을 “재사용 가능한 패턴”으로 쪼개 저장하는 레벨까지 가면, Team Mode가 **자기 학습되는 오케스트레이션 시스템**으로 확장된다. [arxiv](https://arxiv.org/html/2510.04851v1)

```ts
interface ProceduralMemory {
  id: string;
  type: 'plan' | 'debate-pattern' | 'relay-chain';
  tags: string[];          // ['bugfix', 'design', 'planning']
  summary: string;         // 사람 읽기용 설명
  trace: Message[];        // 해당 태스크에서의 핵심 메시지 시퀀스
}
```

- LEGOMem은 이런 메모리 단위를 **semantic index**에 넣고, 새 태스크가 들어오면 유사한 패턴을 꺼내서 오케스트레이터에게 주입. [arxiv](https://arxiv.org/html/2510.04851v1)
- 예: “코드 리뷰 + 버그 수정” 태스크가 들어오면, 과거의 성공적인 팀 토론 패턴을 가져와 “이번에도 이런 라운드를 돌려봐라”라는 힌트를 줄 수 있음. [arxiv](https://arxiv.org/html/2510.04851v1)

***

## 3. Scheduler vs Router: 핵심 로직

### 3‑1. Scheduler 핵심 아이디어

Scheduler의 핵심은 **“지금, 어떤 에이전트들이 어떤 순서로 말해야 하는가?”**만 책임지게 하는 것. [arxiv](https://arxiv.org/html/2509.11656v2)

책임:

1. 새 Message를 입력받음 (user or agent).  
2. 현재 Session의 `mode`와 `Config`를 읽음.  
3. “다음 화자(들)”로 쓸 `AgentConfig[]`를 결정.  
4. 각 에이전트에 넘길 **context view**를 구성 (summary + 최근 history). [mastra](https://mastra.ai/docs/memory/message-history)
5. “이 에이전트들에게 메시지를 보내라”는 요청을 Router에 넘김.

의사코드:

```ts
class Scheduler {
  constructor(
    private agents: AgentConfig[],
    private store: MessageStore,
    private memories: Map<string, SessionMemory>,
    private config: GlobalConfig
  ) {}

  handleIncomingMessage(msg: Message) {
    appendToStore(msg);

    const session = getSession(msg.sessionId);
    const memory = this.memories.get(msg.sessionId);

    const targets = this.route(session, msg); // 어떤 에이전트가 말할지 결정

    for (const agent of targets) {
      const context = buildContext(session.id, memory, this.store);
      router.dispatch(agent, context, msg);
    }
  }

  private route(session: Session, msg: Message): AgentConfig[] {
    // mode + turnIndex 기반 룰: broadcast, debate, relay...
  }
}
```

핵심 아이디어:

- Scheduler는 **LLM API 세부사항을 몰라도 된다** → Router에 맡김.  
- Scheduler는 **Config + Memory + Store**만 보고 “전략적 의사결정”만 수행. [arxiv](https://arxiv.org/abs/2507.06520)

### 3‑2. Router 핵심 아이디어

Router는 “실제 호출 + 응답을 Message로 되돌리는 역할”만 담당.

책임:

1. `dispatch(agent, context, triggerMessage)`를 받아 실제 LLM API 호출.  
2. 응답을 `Message` 구조로 변환.  
3. Scheduler에게 `handleIncomingMessage(responseMessage)`로 다시 전달.

의사코드:

```ts
class Router {
  async dispatch(
    agent: AgentConfig,
    context: LLMContext,
    trigger: Message
  ): Promise<void> {
    const prompt = buildPrompt(context, trigger, agent);
    const text = await callModelAPI(agent, prompt); // Gemini/Claude 등
    const reply: Message = {
      id: uuid(),
      sessionId: trigger.sessionId,
      senderId: agent.id,
      recipientId: 'broadcast',
      role: 'agent',
      modelName: agent.modelName,
      content: text,
      turnIndex: trigger.turnIndex + 1,
      createdAt: Date.now(),
      parentMessageId: trigger.id
    };
    scheduler.handleIncomingMessage(reply);
  }
}
```

핵심 아이디어:

- Router는 stateless에 가깝고, “에이전트별 API 차이”만 캡슐화.  
- 모델 교체(Gemini ↔ Claude)는 Router의 `callModelAPI` 구현만 바꿔도 됨.

***

## 4. Config: 시스템의 “전략 레벨”

Config는 사실상 **Team Mode의 룰북**이다. [arxiv](https://arxiv.org/html/2509.11656v2)

```ts
interface GlobalConfig {
  defaultMode: 'broadcast' | 'debate' | 'relay';
  maxTurns: number;
  summaryEveryNTurns: number;
  contextWindow: {
    maxMessages: number;
    maxTokens: number;
  };
  debate: {
    agents: string[];    // ['gemini','claude']
    judge: string;       // 'codex'
    rounds: number;
  };
  relay: {
    chain: string[];     // ['planner','coder','reviewer']
  };
}
```

핵심 아이디어:

- **새 모드 추가**(예: “critic 모드”)는 Config + Scheduler의 `route`만 건드리면 된다.  
- 팀 구성(어떤 역할에 어떤 모델 배치)은 `AgentConfig`와 Config에서만 제어 → 코드 수정 없이 YAML/JSON으로 조정 가능.

***

## 5. Terminal는 “뷰”로 최소화

terminal는 전체 구조에서 가장 단순해야 한다:

- stdin → `Scheduler.handleIncomingMessage(userMessage)`만 호출.  
- `MessageStore`에 새 메시지가 추가될 때마다, `senderId`로 색상/이름 결정해서 출력. [github](https://github.com/dperique/termi-chat)

핵심 아이디어:

- Terminal는 “state를 갖지 않고”, 모든 상태는 Memory/Storage에 두는 것. [systemdesignhandbook](https://www.systemdesignhandbook.com/guides/design-a-chat-system/)
- 나중에 웹 UI나 다른 클라이언트로 확장할 때, 같은 Scheduler/Router/Memory를 그대로 재사용 가능.

***

## 6. 진짜 핵심 아이디어만 눌러서 요약

질문한 7가지 중에서 **memory/storage 쪽과 전체 연결에서 중요한 포인트**만 다시 한 번 손에 잡히게 정리하면:

1. **Message 구조**는 “LLM·유저·에이전트”를 모두 동일 포맷으로 취급하는 **단일 진실 소스**가 된다. [innovationlab.fetch](https://innovationlab.fetch.ai/resources/docs/agent-communication/agent-chat-protocol)
2. **Memory/Storage**는 단순 로그를 넘어서:
   - 세션별 전체 기록(MessageStore),  
   - 압축된 요약(SessionMemory),  
   - 재사용 가능한 패턴(ProceduralMemory)로 층을 나누는 게 좋다. [systemdesignhandbook](https://www.systemdesignhandbook.com/guides/design-a-chat-system/)
3. **Scheduler**는 “전략 + 메모리”를 이용해 **다음 화자와 모드를 결정**하는 브레인이다. [arxiv](https://arxiv.org/abs/2507.06520)
4. **Router**는 “어떤 모델이든 연결할 수 있게 하는 어댑터”로, API 세부사항을 캡슐화한다.  
5. **Config**는 “어떤 팀 구성을 어떤 패턴으로 돌릴지”를 코드 바깥에서 조절하게 해준다. [arxiv](https://arxiv.org/html/2509.11656v2)

이 구조를 기준으로 TypeScript/Python 스켈레톤을 한 번 짜두면, 이후에는  
- 새로운 LLM 추가 → AgentRegistry/Router만 수정,  
- 새로운 협업 패턴 추가 → Config + Scheduler만 확장  
이런 식으로 Team Mode를 점진적으로 키워갈 수 있어.

코드베이스의 **재사용성, 이식성, 유연성**이라는 목적에 집중하여, 설계안에서 핵심적인 뼈대와 **Memory/Storage**의 구체적 전략만 남겨 정리해 드립니다.

복잡한 부가 설명은 걷어내고, 시스템 확장에 있어 '결정적'인 요소들입니다.

---

## 1. 핵심 5대 컴포넌트 구조 (유연성 확보)

7가지 중 굳이 분리하지 않아도 될 요소를 통합하고, **전략(Scheduler)**과 **실행(Router)**을 분리하는 것이 핵심입니다.

* **Message (공통 규격)**: 모든 에이전트와 유저가 소통하는 단일 진실 소스(Single Source of Truth).
* **Memory/Storage (상태 관리)**: 대화 이력, 요약, 추출된 지식을 보관하는 저장소.
* **Scheduler (의사결정)**: `Config`와 `Memory`를 참조하여 "다음 화자"와 "전달할 컨텍스트"를 결정하는 두뇌.
* **Router (실행 어댑터)**: 결정된 화자(Gemini, Claude 등)의 API를 실제로 호출하고 응답을 Message 규격으로 변환.
* **Config (전략 설정)**: 코드 수정 없이 팀 구성(에이전트 역할)과 협업 모드(토론, 릴레이 등)를 정의하는 룰북.

---

## 2. Memory/Storage 설계: 재사용성의 핵심

이식성과 유연성을 높이려면 메모리를 단순 로그가 아닌 **계층형 구조**로 설계해야 합니다.

### Layer 1: Message Store (단기/상세 메모리)

* **역할**: 현재 세션의 모든 로우(Raw) 데이터 저장.
* **구조**: `turnIndex`와 `parentMessageId`를 포함하여 대화의 흐름(Tree 구조)을 추적 가능하게 함.
* **이점**: 특정 시점으로의 롤백이나 브랜치 대화(다른 시도)가 가능해짐.

### Layer 2: Summary Memory (중기/압축 메모리)

* **역할**: 토큰 제한을 극복하기 위해 이전 대화를 LLM을 통해 요약.
* **전략**: "전체 요약 + 최근 N개 메시지" 조합으로 컨텍스트 주입.
* **이점**: 대화가 길어져도 핵심 맥락을 잃지 않고 비용을 절감함.

### Layer 3: Procedural Memory (장기/지식 메모리)

* **역할**: 성공적인 문제 해결 패턴(예: 특정 버그 수정 루틴)을 별도 지식화.
* **이점**: 새로운 프로젝트나 세션에서도 "과거에 이런 식으로 협업했을 때 효율적이었다"는 가이드를 에이전트에게 주입하여 **시스템의 자기 학습** 구현.

---

## 3. 핵심 로직: Scheduler와 Router의 분리

이 분리가 되어야만 새로운 LLM이 나와도 시스템 전체를 뜯어고치지 않습니다.

* **Scheduler (Why & Who)**:
* "지금 상황(Memory)을 보니 다음은 Claude가 코드 리뷰(Role)를 할 차례군."
* **유연성**: `Config` 파일만 바꾸면 토론 순서나 참여 모델을 즉시 변경 가능.


* **Router (How)**:
* "Claude API 형식에 맞춰 메시지를 보내고 결과를 받아올게."
* **이식성**: 새로운 모델(예: GPT-5) 추가 시 Router에 어댑터 하나만 추가하면 끝.



---

## 4. 최종 요약: 도움이 될 설계 원칙

1. **모델 독립성**: Scheduler는 어떤 모델이 쓰이는지 몰라야 합니다. 오직 '역할'만 지정합니다.
2. **컨텍스트 격리**: 각 에이전트에게 전체 이력을 다 줄지, 요약본만 줄지 Scheduler가 Memory를 필터링해서 전달합니다.
3. **설정 기반 확장**: 새로운 협업 패턴(모드) 추가는 소스 코드가 아닌 `Config`와 `Scheduler`의 라우팅 규칙 추가로 해결합니다.

---

\