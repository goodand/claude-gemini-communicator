# Claude Code Task Prompt — Mermaid Skill

아래 프롬프트를 Claude Code에 그대로 공유하면 된다.

---

You are working in this repository:

`/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project`

Create a new **Mermaid-specific skill** intended for Claude Code usage.

## Mission

Build a reusable skill that helps Claude Code produce Mermaid diagrams that are much more likely to render successfully on Mermaid 11.13.0, especially when diagrams get slightly complex.

This skill should be **document-first**, **parser-safe**, and **incremental**.

## Goal

Create a new skill that teaches and enforces this workflow:

1. Start from adjacency-list style structure first.
2. Generate the most minimal Mermaid syntax first.
3. Confirm parser-safe rendering assumptions.
4. Only then add labels, grouping, and styling incrementally.
5. Treat Mermaid rendering failures as syntax-debugging tasks, not style tasks.

## Important Local Context

Use the local repository as primary context.

Read these files first:

- `skill-creation-process/SKILL.md`
- `skill-creation-process/references/progressive-context-injection.md`
- `skill-creation-process/references/markdown-artifact-writing-patterns-at2026-03-20-14-13.md`
- `skill-creation-process/references/script-and-linter-writing-patterns-at2026-03-20-14-15.md`
- `mermaid-kb-layer-edge-types-at2026-03-20-11-50.html`

Use the Mermaid HTML work we already did as local evidence for failure patterns and safe subset patterns.

## What The Skill Must Cover

The skill should teach:

- adjacency-list-first design
- minimal Mermaid first
- short node labels first
- edge types added incrementally
- avoid mixing too many Mermaid features at once
- parser-safe recovery flow when Mermaid says `Syntax error in text`
- difference between:
  - structural grouping
  - flow edges
  - constraint edges
  - escalation edges

It should also explicitly document that:

- `contains` is better expressed as **subgraph membership** when possible
- `feeds`, `constrains`, `escalates_to` remain edge relations
- `linkStyle`, `classDef`, long labels, slashes, and dense syntax should be added only after the minimal graph renders

## Deliverables

Create a new skill directory. Choose a good skill name, but prefer something close to:

- `claude-code-mermaid`
or
- `mermaid-safe-authoring`

Inside it, create at least:

1. `SKILL.md`
2. `references/troubleshooting.md`
3. one canonical KB in `knowledge_bases/`
4. one consistency checklist in `checklist-forconsistency-evaluation/`
5. one or more focused Mermaid references in `references/`

Recommended reference docs:

- Mermaid parser-safe subset
- Mermaid authoring workflow
- Mermaid troubleshooting / recovery
- Mermaid relation modeling guidance

Optional:

- a minimal HTML template or example artifact if it is clearly reusable

## Scope Boundaries

In scope:

- Mermaid authoring workflow
- Mermaid parser-safe syntax guidance
- Mermaid troubleshooting patterns
- Mermaid relation modeling guidance
- document-first skill scaffolding

Out of scope:

- large custom Mermaid rendering runtime
- browser automation
- image export pipeline
- external package installation
- graph database integration
- general diagramming beyond Mermaid

## Non-goals

- Do not turn this into a generic graph-RAG skill.
- Do not add apply/mutation workflow layers.
- Do not add speculative automation that depends on unstable tool output if a document rule is enough.
- Do not overbuild scripts unless there is a clearly reusable CLI shape.

## Style Requirements

- Keep the skill document-first unless a script is truly justified.
- Prefer stable rules over over-automation.
- Use Progressive Context Injection.
- Keep `SKILL.md` small enough to pass `quick_validate`.
- If line-count warning appears, split naturally into reference files instead of over-compressing.

## Mermaid-Specific Guidance To Encode

The skill should explicitly recommend this sequence:

1. write adjacency list
2. convert to minimal `graph TD`
3. use only simple nodes and `-->`
4. render mentally / parser-check assumptions
5. add edge labels one category at a time
6. move structural containment into `subgraph`
7. add style only last

It should also warn against:

- long labels too early
- slashes or punctuation-heavy labels too early
- mixing `classDef`, `linkStyle`, dashed edges, and labeled edges in the first draft
- trying to debug style before syntax is stable

## Verification

At minimum:

- `quick_validate <new-skill-dir>` must pass

If you add scripts:

- add TDD
- run the tests
- run `py_compile`

If you add an HTML example:

- keep it minimal and Mermaid 11.13.0-safe
- prefer a known-safe subset over a visually rich example

## Preservation Rules

- Do not touch unrelated skills.
- Do not modify legacy directories.
- Do not delete or rewrite unrelated active artifacts.
- If you replace an active file, preserve the previous content first.
- Prefer git commit over piling up ad-hoc legacy copies for tracked files.

## Suggested Output Back To Me

When done, report:

1. chosen skill name
2. files created
3. Mermaid-specific rules captured
4. whether scripts were intentionally omitted or added
5. verification result
6. any follow-up suggestions

## Strong Preference

I would rather have:

- a smaller, sharper Mermaid skill

than:

- an over-automated but unstable Mermaid skill

Optimize for successful reuse by Claude Code, not for maximum feature count.

---

짧은 버전으로 줄이면:

> Mermaid 11.13.0에서 잘 렌더되는 보수적 Mermaid authoring skill을 만들어라. adjacency-list-first, minimal syntax first, subgraph-for-contains, style-last 원칙을 중심으로 document-first skill을 만들고, `quick_validate`를 통과시켜라.
