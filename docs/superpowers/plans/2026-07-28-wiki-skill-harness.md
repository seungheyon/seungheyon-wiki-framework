# 위키 스킬 하네스 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** seungheyon-wiki를 지속 관리할 수 있는 스킬 하네스(범용 생성기 + 운영 3종 + 커리어 2종 + 세 글로벌 규칙)를 이 레포 안에 정석 구조로 구축한다.

**Architecture:** `.claude/skills/`에 Claude Code 정석 스킬 구조(SKILL.md + references/ + templates/)로 스킬을 두고, 위키 규약은 `_shared/wiki-conventions.md` 단일 출처로 분리(DRY)한다. 자동 동작은 훅 대신 CLAUDE.md 규칙 + 레포 커밋 파일(`.claude/LESSONS.md`)로 구현해 `git clone` 이식성을 확보한다.

**Tech Stack:** Markdown, YAML frontmatter, Obsidian 위키링크, git, Claude Code Skill 규약.

**참고 문서:** 설계 스펙 `docs/superpowers/specs/2026-07-28-wiki-skill-harness-design.md`, 스키마 `CLAUDE.md`, 패턴 원본 `reference/llm-wiki.md`.

**검증 규약(전 태스크 공통):** "테스트"는 (a) 구조 검증 — `SKILL.md` frontmatter에 `name`(디렉터리와 동일, ascii-kebab)·`description` 존재, (b) 대표 트리거 리허설 — 해당 자연어로 스킬이 로딩·수행되는지 1건 확인. 코드 실행 테스트는 없음.

---

## File Structure

| 파일 | 책임 |
|---|---|
| `.claude/LESSONS.md` | 셀프임프루빙 append-only 로그. 세션 시작 시 필독 |
| `.claude/skills/_shared/wiki-conventions.md` | 위키 규약 요약(단일 출처). 위키 스킬들이 참조 |
| `.claude/skills/skill-creator/SKILL.md` | 범용 스킬 생성기 진입점 |
| `.claude/skills/skill-creator/references/skill-authoring-best-practices.md` | 생성기의 자가검증 체크리스트/원칙 |
| `.claude/skills/skill-creator/templates/SKILL.template.md` | 새 스킬 house 템플릿 |
| `.claude/skills/wiki-ingest/SKILL.md` | ingest 워크플로우 |
| `.claude/skills/wiki-query/SKILL.md` | query 워크플로우 |
| `.claude/skills/wiki-lint/SKILL.md` | lint 워크플로우 |
| `.claude/skills/interview-prep/SKILL.md` | 면접 대비(특수 query) |
| `.claude/skills/decision-journal/SKILL.md` | 의사결정 저널(특수 ingest) |
| `CLAUDE.md` | §7 글로벌 규칙 + 스킬 카탈로그/트리거 표 추가 (수정) |
| `log.md` | 하네스 구축 ingest 항목 추가 (수정) |

---

## Task 1: Phase 0 — 뼈대 (디렉터리 + LESSONS + 공통 규약)

**Files:**
- Create: `.claude/skills/_shared/wiki-conventions.md`
- Create: `.claude/LESSONS.md`

- [ ] **Step 1: 디렉터리 생성**

Run:
```bash
mkdir -p .claude/skills/_shared \
  .claude/skills/skill-creator/references \
  .claude/skills/skill-creator/templates \
  .claude/skills/wiki-ingest .claude/skills/wiki-query .claude/skills/wiki-lint \
  .claude/skills/interview-prep .claude/skills/decision-journal
```
Expected: 무출력(성공).

- [ ] **Step 2: `.claude/LESSONS.md` 작성 (시드 교훈 포함)**

Create `.claude/LESSONS.md`:
```markdown
# LESSONS — 셀프 임프루빙 로그

seungheyon-wiki 하네스의 자기교정 기록. 레포에 커밋되어 클론에 따라온다.

**규칙(강제):**
- 사용자가 피드백을 주거나, 회고 중 내 실수를 발견하면 **즉시** 아래에 append 하고 두 번 다시 반복하지 않는다.
- **매 세션 시작 시 이 파일을 반드시 읽고** 그 교훈을 준수한다.

형식: `- [YYYY-MM-DD] 교훈 / 왜: … / 적용: …`

## 교훈
- [2026-07-28] 새 원격/레포에서는 첫 커밋 전에 push 권한을 확인한다 / 왜: 첫 push가 권한 없는 origin으로 403 실패 / 적용: 작업 시작 시 `git remote -v` + 쓰기 권한 점검.
- [2026-07-28] 범위·방식·대상이 조금이라도 모호하면 추측하지 말고 AskUserQuestion 먼저 / 왜: 사용자 명시 글로벌 규칙 #3 / 적용: 모든 세션에서 상시 적용.
```

- [ ] **Step 3: `_shared/wiki-conventions.md` 작성**

Create `.claude/skills/_shared/wiki-conventions.md`:
```markdown
# 위키 규약 (단일 출처)

위키 스킬(wiki-ingest/query/lint, interview-prep, decision-journal)이 공통으로 지키는 규약 요약.
**정본은 `CLAUDE.md`** — 충돌 시 CLAUDE.md가 우선한다. 여기서는 스킬 실행에 필요한 핵심만 압축한다.

## 3계층
- `raw/` : 불변 원본. **절대 수정하지 않는다.** 갱신은 새 파일 추가로만.
- wiki(`people/`·`concepts/`·`companies/`) : LLM이 소유·유지하는 합성 페이지.
- schema(`CLAUDE.md`) : 규칙.

## frontmatter (모든 wiki 페이지 공통)
```yaml
---
type: person | concept | company | index
domain: 취업-IT
tags: [태그]
updated: YYYY-MM-DD
sources:
  - "[[raw/경로/파일명]]"
status: null | 진행중 | 종료 | 대기
---
```

## 위키링크
- 내부 참조는 항상 `[[페이지명]]` (확장자 없이).
- raw도 `[[취업-IT/raw/…]]`로 링크.
- 고아 페이지 금지 — 모든 새 페이지는 최소 1개 이상 나가는 링크 + 가능하면 들어오는 링크.

## 중복 처리
- 같은 사실이 여러 raw에 흩어지면 wiki에 **캐논 페이지 1개**로 통합하고 raw들은 `sources:`로만 링크. raw는 지우지 않는다.

## 페이지 유형별 뼈대
- person: 기본정보 → 목표 → 강점 → 약점/자기인식 → 핵심 프로젝트(링크) → 성과지표(링크) → 관련 회사(링크)
- concept: 정의/요약 → 세부 → 등장 맥락 → 출처
- company: 개요 → 지원 직무 → 파이프라인 상태(단계·날짜) → 산출물(링크) → 회고

## 마무리 공통
- 변경마다 도메인 `index.md`와 루트 `log.md` 갱신.
- `log.md` 항목 형식: `## [YYYY-MM-DD] ingest|query|lint | 제목`.
```

- [ ] **Step 4: 구조 검증**

Run:
```bash
ls -R .claude && test -f .claude/LESSONS.md && test -f .claude/skills/_shared/wiki-conventions.md && echo OK
```
Expected: 디렉터리 트리 출력 후 `OK`.

- [ ] **Step 5: Commit**

```bash
git add .claude/LESSONS.md .claude/skills/_shared/wiki-conventions.md
git commit -m "feat(harness): .claude 뼈대 + LESSONS + 위키 공통 규약 추가"
```

---

## Task 2: Phase 1 — skill-creator (범용 생성기)

**Files:**
- Create: `.claude/skills/skill-creator/SKILL.md`
- Create: `.claude/skills/skill-creator/references/skill-authoring-best-practices.md`
- Create: `.claude/skills/skill-creator/templates/SKILL.template.md`

- [ ] **Step 1: best-practices 레퍼런스 작성**

Create `.claude/skills/skill-creator/references/skill-authoring-best-practices.md`:
```markdown
# 스킬 저작 best practice / 자가검증 체크리스트

## 원칙
1. **name**: 디렉터리명과 동일, ascii 소문자-하이픈(kebab). 동사(gerund)나 명사구.
2. **description**: 3인칭으로 "**언제 쓰는지(트리거)** + **무엇을 하는지**"를 담는다. 자연어 트리거 문구를 포함해 자동 로딩이 되게 한다. ~1024자 이내.
3. **progressive disclosure**: `SKILL.md`는 짧게(무엇을·언제·순서). 긴 규칙/예시는 `references/`로 밀어낸다.
4. **자기완결·비휘발성**: 날짜·수치 등 시간민감 정보를 본문에 하드코딩하지 않는다.
5. **보조 자원**: 반복 스캐폴딩은 `templates/`, 실행 로직은 `scripts/`, 참고 문서는 `references/`.

## 생성 후 자가검증 (모두 통과해야 완료)
- [ ] `name`이 디렉터리와 일치하고 ascii-kebab인가
- [ ] `description`에 트리거 + 동작이 3인칭으로 들어갔나
- [ ] 시간민감 정보 하드코딩이 없나
- [ ] `SKILL.md`가 간결하고 세부는 references로 갔나
- [ ] (지식 베이스를 다루는 스킬이면) 규약 파일을 참조하고 있나
- [ ] 나가는 참조/트리거가 실제 파일·의도와 맞나
```

- [ ] **Step 2: house 템플릿 작성**

Create `.claude/skills/skill-creator/templates/SKILL.template.md`:
```markdown
---
name: <ascii-kebab-name>
description: <언제 쓰는지(자연어 트리거 문구 포함) + 무엇을 하는지, 3인칭 한 문단>
---

# <스킬 표시 이름>

<한 줄 목적>

## 언제
- 트리거: "<자연어 문구1>", "<문구2>" …

## 순서
1. <단계>
2. <단계>

## 참고
- <필요 시 references/… 링크>
- (지식 베이스를 다루는 스킬이면) 규약: `.claude/skills/_shared/<conventions>.md` 및 해당 프로젝트 스키마 문서

## 마무리
- (해당 시) 산출물/인덱스/로그 갱신, 작업 완료 시 커밋.
```

- [ ] **Step 3: skill-creator SKILL.md 작성**

Create `.claude/skills/skill-creator/SKILL.md`:
```markdown
---
name: skill-creator
description: 새 Claude Code 스킬을 정석 구조(SKILL.md + references/ + templates/)로 스캐폴딩할 때 사용한다. "스킬 만들어줘", "새 스킬 생성", "skill 만들어줘", "슬래시 명령 추가" 같은 요청에서 트리거된다. 범용 생성기 — 위키 스킬뿐 아니라 어떤 스킬이든 만든다.
---

# skill-creator

새 스킬을 house 표준으로 찍어내는 범용 생성기. 이후 모든 스킬은 손이 아니라 이걸로 만든다.

## 언제
- 트리거: "스킬 만들어줘", "새 스킬 생성", "skill 만들어줘", "슬래시 명령 추가".

## 순서
1. **수집** — `name`(ascii-kebab), `description`(트리거+동작), 본문 개요, 필요한 `references/`·`templates/`·`scripts/` 여부. 조금이라도 모호하면 AskUserQuestion으로 확인.
2. **스캐폴딩** — `templates/SKILL.template.md`를 채워 `.claude/skills/<name>/SKILL.md` 생성. 필요한 하위 폴더/스텁 생성.
3. **위키 여부 판단** — 이 스킬이 이 위키의 지식(raw/people/concepts/companies)을 다루면, 본문에 `.claude/skills/_shared/wiki-conventions.md`와 `CLAUDE.md` 참조를 넣는다. (생성기 자체는 범용이며 위키를 강제하지 않는다.)
4. **자가검증** — `references/skill-authoring-best-practices.md` 체크리스트를 모두 통과시킨다.
5. **등록** — 위키 스킬이면 `CLAUDE.md`의 스킬 카탈로그 표에 한 줄 추가, `log.md`에 생성 기록.

## 참고
- 체크리스트/원칙: `references/skill-authoring-best-practices.md`
- 템플릿: `templates/SKILL.template.md`
```

- [ ] **Step 4: 구조 검증**

Run:
```bash
head -3 .claude/skills/skill-creator/SKILL.md && grep -q "^name: skill-creator" .claude/skills/skill-creator/SKILL.md && test -f .claude/skills/skill-creator/references/skill-authoring-best-practices.md && test -f .claude/skills/skill-creator/templates/SKILL.template.md && echo OK
```
Expected: frontmatter 앞부분 출력 후 `OK`.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/skill-creator
git commit -m "feat(skill-creator): 범용 스킬 생성기 + best-practices + 템플릿"
```

---

## Task 3: wiki-ingest (운영 · ingest)

**Files:**
- Create: `.claude/skills/wiki-ingest/SKILL.md`

- [ ] **Step 1: SKILL.md 작성**

Create `.claude/skills/wiki-ingest/SKILL.md`:
```markdown
---
name: wiki-ingest
description: 새 소스를 seungheyon-wiki에 편입할 때 사용한다. "위키화해줘", "이거 위키에 넣어줘", "위키에 반영/정리해줘", "새 소스 추가", "ingest" 같은 요청에서 트리거된다. raw에 원본을 넣고 관련 wiki 페이지·index·log를 갱신한다.
---

# wiki-ingest

새 소스를 위키에 통합한다. 규약은 `.claude/skills/_shared/wiki-conventions.md`와 `CLAUDE.md` §5를 따른다.

## 언제
- 트리거: "위키화해줘", "위키에 넣어/반영/정리해줘", "새 소스 추가", "ingest".

## 순서
1. **원본 편입** — 소스를 적절한 `<도메인>/raw/…` 경로에 추가. **기존 raw는 절대 수정하지 않는다.** 새 도메인이면 폴더 신설 후 루트 `index.md`에 등록.
2. **핵심 파악·논의** — 소스의 요점을 사용자와 짧게 확인. 모호하면 AskUserQuestion.
3. **wiki 갱신** — 관련 people/concepts/companies 페이지를 갱신. 같은 사실이 흩어져 있으면 캐논 페이지 1개로 통합하고 raw는 `sources:`로만 링크.
4. **신설** — 필요한 새 페이지 생성(유형별 뼈대·frontmatter 준수, 고아 방지 링크 포함).
5. **인덱스/로그** — 도메인 `index.md` 갱신, 루트 `log.md`에 `## [YYYY-MM-DD] ingest | 제목` append.
6. **완료** — 작업이 끝났으면 규칙 #1에 따라 커밋 & 푸시.

## 참고
- 규약: `.claude/skills/_shared/wiki-conventions.md`, `CLAUDE.md`
```

- [ ] **Step 2: 구조 검증**

Run:
```bash
grep -q "^name: wiki-ingest" .claude/skills/wiki-ingest/SKILL.md && grep -q "위키화해줘" .claude/skills/wiki-ingest/SKILL.md && echo OK
```
Expected: `OK`.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/wiki-ingest
git commit -m "feat(wiki-ingest): ingest 워크플로우 스킬"
```

---

## Task 4: wiki-query (운영 · query)

**Files:**
- Create: `.claude/skills/wiki-query/SKILL.md`

- [ ] **Step 1: SKILL.md 작성**

Create `.claude/skills/wiki-query/SKILL.md`:
```markdown
---
name: wiki-query
description: seungheyon-wiki에 축적된 지식으로 질문에 답할 때 사용한다. "위키에서 찾아줘/알려줘", "위키 기준으로 ~", 이승현의 프로필·프로젝트·지원 현황 등 축적된 지식에 대한 질의에서 트리거된다. 일반 잡담 Q&A에는 쓰지 않는다.
---

# wiki-query

위키 지식으로 답하고, 재사용 가치가 있으면 페이지로 파일백한다.

## 언제
- 트리거: "위키에서 찾아/알려줘", "위키 기준으로 ~", 이승현 축적 지식 질의.
- 쓰지 않을 때: 위키와 무관한 일반 지식·잡담.

## 순서
1. **인덱스 우선** — 관련 도메인 `index.md`를 먼저 읽어 관련 페이지를 찾는다.
2. **읽기·종합** — 해당 페이지를 읽고 인용(`[[페이지명]]`)과 함께 답한다.
3. **파일백 제안** — 새 비교/종합/발견이 재사용 가치가 있으면 새 concept 페이지로 남길지 사용자에게 제안하고, 승인 시 생성 + index/log 갱신.
4. **완료** — 파일을 바꿨으면 규칙 #1에 따라 커밋 & 푸시.

## 참고
- 규약: `.claude/skills/_shared/wiki-conventions.md`, `CLAUDE.md`
```

- [ ] **Step 2: 구조 검증**

Run:
```bash
grep -q "^name: wiki-query" .claude/skills/wiki-query/SKILL.md && echo OK
```
Expected: `OK`.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/wiki-query
git commit -m "feat(wiki-query): query 워크플로우 스킬"
```

---

## Task 5: wiki-lint (운영 · lint)

**Files:**
- Create: `.claude/skills/wiki-lint/SKILL.md`

- [ ] **Step 1: SKILL.md 작성**

Create `.claude/skills/wiki-lint/SKILL.md`:
```markdown
---
name: wiki-lint
description: 위키 건강검진이 필요할 때 사용한다. "위키 점검", "위키 린트", "위키 건강검진", "모순 찾아줘", "오래된 내용 있나 봐줘" 같은 요청에서 트리거된다. 모순·stale·고아·누락 링크·페이지 없는 개념을 점검하고 수정을 제안한다.
---

# wiki-lint

위키의 일관성/건강을 점검한다.

## 언제
- 트리거: "위키 점검/린트/건강검진", "모순 찾아줘", "오래된 내용 봐줘".

## 순서
1. **점검 항목** — (a) 페이지 간 모순, (b) 새 소스가 갱신했는데 반영 안 된 stale 주장, (c) 고아 페이지(들어오는 링크 없음), (d) 누락 상호링크, (e) 언급되지만 자기 페이지 없는 개념, (f) 웹서치로 메울 수 있는 데이터 공백.
2. **리포트** — 발견을 항목별로 정리해 사용자에게 보고.
3. **적용** — 승인받은 수정을 반영(캐논/링크/신설). raw는 건드리지 않는다.
4. **기록** — `log.md`에 `## [YYYY-MM-DD] lint | 제목` append. 변경했으면 규칙 #1에 따라 커밋 & 푸시.

## 참고
- 규약: `.claude/skills/_shared/wiki-conventions.md`, `CLAUDE.md`
```

- [ ] **Step 2: 구조 검증**

Run:
```bash
grep -q "^name: wiki-lint" .claude/skills/wiki-lint/SKILL.md && echo OK
```
Expected: `OK`.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/wiki-lint
git commit -m "feat(wiki-lint): lint 워크플로우 스킬"
```

---

## Task 6: interview-prep (커리어 사고 · 특수 query)

**Files:**
- Create: `.claude/skills/interview-prep/SKILL.md`

- [ ] **Step 1: SKILL.md 작성**

Create `.claude/skills/interview-prep/SKILL.md`:
```markdown
---
name: interview-prep
description: 특정 기업 면접을 대비할 때 사용한다. "<회사> 면접 준비/대비", "예상질문 뽑아줘", "면접 준비 도와줘" 같은 요청에서 트리거된다. 기업 페이지 + 이승현 허브 + 약점클러스터 + 성과지표를 읽어 예상질문과 답변 스캐폴드를 만든다.
---

# interview-prep

위키 지식으로 면접을 대비한다(특수 query).

## 언제
- 트리거: "<회사> 면접 준비/대비", "예상질문 뽑아줘", "면접 준비 도와줘".

## 순서
1. **대상 확인** — 어느 기업/직무인지 확인(모호하면 AskUserQuestion).
2. **읽기** — `companies/<회사>` + `people/이승현` + `concepts/자기인식_약점클러스터` + `concepts/성과지표`(+ 관련 프로젝트 페이지).
3. **생성** — 예상질문 + 답변 스캐폴드. **이승현은 즉흥 자기질문(강점/공백기/전공전환)에 약하고 조사한 대상 질문에 강하다** — 자기질문 대비를 특히 강화한다.
4. **파일백 제안** — 결과가 재사용 가치 있으면 해당 회사 페이지에 남길지 제안.
5. **완료** — 파일을 바꿨으면 규칙 #1에 따라 커밋 & 푸시.

## 참고
- 규약: `.claude/skills/_shared/wiki-conventions.md`, `CLAUDE.md`
- 약점 맥락: `취업-IT/concepts/자기인식_약점클러스터`
```

- [ ] **Step 2: 구조 검증**

Run:
```bash
grep -q "^name: interview-prep" .claude/skills/interview-prep/SKILL.md && echo OK
```
Expected: `OK`.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/interview-prep
git commit -m "feat(interview-prep): 면접 대비 스킬(특수 query)"
```

---

## Task 7: decision-journal (커리어 사고 · 특수 ingest)

**Files:**
- Create: `.claude/skills/decision-journal/SKILL.md`

- [ ] **Step 1: SKILL.md 작성**

Create `.claude/skills/decision-journal/SKILL.md`:
```markdown
---
name: decision-journal
description: 커리어 관련 결정(오퍼 수락/거절, 직무 선택, 방향 전환 등)을 근거와 함께 기록할 때 사용한다. "이 결정 기록해줘", "의사결정 저널", "오퍼 받았는데 정리해줘", "방향 정했어" 같은 요청에서 트리거된다. 결정을 concept 페이지로 남기고 허브에 링크한다.
---

# decision-journal

커리어 결정을 근거·대안·맥락과 함께 위키에 남긴다(특수 ingest). 취업 이후 커리어 방향 관리의 핵심.

## 언제
- 트리거: "이 결정 기록해줘", "의사결정 저널", "오퍼 정리해줘", "방향 정했어".

## 순서
1. **결정 수집** — 무엇을 결정했나 / 고려한 대안 / 선택 근거 / 당시 맥락·감정 / 되돌아볼 트리거. 빠진 항목은 AskUserQuestion.
2. **페이지 생성** — `<도메인>/concepts/결정_<주제>_<YYYYMMDD>` 신설(concept frontmatter, `type: concept`, `status` 적절히).
3. **링크** — `people/이승현`(및 있으면 방향 페이지)에서 이 결정으로 나가는 링크 추가(고아 방지).
4. **로그** — `log.md`에 `## [YYYY-MM-DD] ingest | 결정: 제목` append, 도메인 index 갱신.
5. **완료** — 규칙 #1에 따라 커밋 & 푸시.

## 참고
- 규약: `.claude/skills/_shared/wiki-conventions.md`, `CLAUDE.md`
```

- [ ] **Step 2: 구조 검증**

Run:
```bash
grep -q "^name: decision-journal" .claude/skills/decision-journal/SKILL.md && echo OK
```
Expected: `OK`.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/decision-journal
git commit -m "feat(decision-journal): 의사결정 저널 스킬(특수 ingest)"
```

---

## Task 8: Phase 4 — CLAUDE.md에 글로벌 규칙 + 스킬 카탈로그

**Files:**
- Modify: `CLAUDE.md` (파일 끝에 두 섹션 추가)

- [ ] **Step 1: `CLAUDE.md` 끝에 §7, §8 추가**

`CLAUDE.md` 맨 아래(§6 다음)에 아래 내용을 append:
```markdown

---

## 7. 글로벌 운영 규칙 (이 레포 한정 · 반드시 준수)

이 세 규칙은 훅이 아니라 이 문서 + 레포 커밋 파일로 강제한다. `git clone` 시 그대로 따라오며 machine-global 설정을 만들지 않는다.

1. **작업 완료 후 필수 `git commit & push`** — 파일을 변경한(=실제 작업이 끝난) 턴에는 durable 승인 하에 자동으로 `git add` → `commit` → `push`(origin main)한다. 단순 질문답변/탐색만 한 턴은 예외. 커밋 메시지는 무엇을 왜 바꿨는지 한 줄 요약.
2. **셀프 임프루빙 (강한 강제)** — 사용자가 피드백을 주거나 회고 중 내 실수를 발견하면 **즉시 `.claude/LESSONS.md`에 `- [YYYY-MM-DD] 교훈 / 왜 / 적용` 형식으로 append**하고 두 번 다시 반복하지 않는다. **매 세션 시작 시 `.claude/LESSONS.md`를 반드시 읽고** 준수한다.
3. **모호하면 AskUserQuestion** — 요구사항·범위·방식에 조금이라도 모호함이 있으면 추측하지 말고 반드시 AskUserQuestion으로 물어본다.

## 8. 스킬 카탈로그 / 트리거

스킬은 `.claude/skills/`에 있다. 자연어로 아래 트리거를 말하면 해당 스킬이 로딩된다.

| 스킬 | 유형 | 대표 트리거 |
|---|---|---|
| `skill-creator` | 생성기(범용) | "스킬 만들어줘", "새 스킬 생성" |
| `wiki-ingest` | ingest | "위키화해줘", "위키에 넣어/반영/정리해줘", "새 소스 추가" |
| `wiki-query` | query | "위키에서 찾아/알려줘", "위키 기준으로 ~" |
| `wiki-lint` | lint | "위키 점검/린트/건강검진", "모순 찾아줘" |
| `interview-prep` | 특수 query | "<회사> 면접 준비/대비", "예상질문 뽑아줘" |
| `decision-journal` | 특수 ingest | "이 결정 기록해줘", "오퍼 정리해줘", "방향 정했어" |

새 스킬은 `skill-creator`로 만들고 이 표에 한 줄 추가한다.
```

- [ ] **Step 2: 구조 검증**

Run:
```bash
grep -q "## 7. 글로벌 운영 규칙" CLAUDE.md && grep -q "## 8. 스킬 카탈로그" CLAUDE.md && grep -q "LESSONS.md" CLAUDE.md && echo OK
```
Expected: `OK`.

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(CLAUDE): §7 글로벌 규칙 + §8 스킬 카탈로그/트리거 추가"
```

---

## Task 9: 검증 리허설 + log 기록 + 최종 push

**Files:**
- Modify: `log.md`

- [ ] **Step 1: 트리거 리허설 (드라이런, 파일 변경 없음)**

각 스킬을 대표 트리거로 1건씩 로딩·수행 리허설. 최소 다음 2건은 실제로 확인:
- `wiki-query`: "위키 기준으로 이승현의 핵심 프로젝트 3개 알려줘" → `취업-IT/index.md` → 관련 페이지 인용 답변이 나오는가.
- `wiki-lint`: 현재 위키 1회 점검 → 고아/모순 리포트가 산출되는가.

관찰 결과(문제 발견 시)는 `.claude/LESSONS.md`에 append.

- [ ] **Step 2: `log.md`에 구축 항목 추가**

`log.md` 끝에 append:
```markdown

## [2026-07-28] ingest | 스킬 하네스 구축 — .claude 패키지

- `.claude/skills/`에 스킬 하네스 신설: `skill-creator`(범용 생성기) + 운영 3종(`wiki-ingest`/`wiki-query`/`wiki-lint`) + 커리어 2종(`interview-prep`/`decision-journal`).
- 공통 규약 단일 출처 `.claude/skills/_shared/wiki-conventions.md`, 셀프임프루빙 로그 `.claude/LESSONS.md` 추가.
- `CLAUDE.md`에 §7 글로벌 규칙(커밋&푸시 / 셀프임프루빙 / 모호시 질문), §8 스킬 카탈로그/트리거 추가.
- 설계·계획 문서: `docs/superpowers/specs/2026-07-28-wiki-skill-harness-design.md`, `docs/superpowers/plans/2026-07-28-wiki-skill-harness.md`.
```

- [ ] **Step 3: 최종 커밋 & 푸시 (규칙 #1)**

```bash
git add log.md
git commit -m "docs(log): 스킬 하네스 구축 ingest 기록"
git push origin main
```
Expected: `... main -> main` (푸시 성공).

- [ ] **Step 4: 전체 구조 최종 점검**

Run:
```bash
find .claude -type f | sort && for f in skill-creator wiki-ingest wiki-query wiki-lint interview-prep decision-journal; do grep -q "^name: $f" .claude/skills/$f/SKILL.md && echo "$f OK" || echo "$f MISSING"; done
```
Expected: 파일 목록 + 6개 모두 `OK`.

---

## Self-Review (계획 작성자 확인 완료)

- **스펙 커버리지**: 스펙 §4(레이아웃)→Task1·2, §5(생성기)→Task2, §6(5종 스킬)→Task3~7, §7(트리거)→각 SKILL description + Task8 §8표, §8(3규칙)→Task8 §7, §9(빌드순서)→Task1~9 순서, §10(검증)→각 태스크 검증 스텝 + Task9. 누락 없음.
- **Placeholder 스캔**: 템플릿 파일 내부의 `<…>`는 의도된 채움표시(SKILL.template.md)이며 계획 자체의 미완성 placeholder 아님. 그 외 TBD/TODO 없음.
- **일관성**: 스킬 `name`은 디렉터리명과 전 태스크에서 동일하게 사용(`wiki-ingest` 등). `.claude/LESSONS.md` 경로·형식이 Task1·Task8·스펙에서 일치.
```
