# seungheyon-wiki 스킬 하네스 설계 스펙

- 작성일: 2026-07-28
- 상태: 설계 확정 (구현 계획 대기)
- 대상 저장소: `seungheyon-wiki` (Karpathy LLM-wiki 패턴 기반 개인 위키)

---

## 1. 배경 / 현재 상태

이 저장소는 `reference/llm-wiki.md`의 3계층 패턴(raw / wiki / schema)을 따르는 개인 위키다.
지식 저장소 구조(스키마 `CLAUDE.md`, 루트/도메인 `index.md`, `log.md`, `취업-IT` 도메인의 people/concepts/companies/raw)는 이미 완성되어 있다.

**문제**: Ingest / Query / Lint 워크플로우가 `CLAUDE.md` §5의 **산문 규칙**으로만 존재한다.
`/명령`으로 부를 수 있는 실제 스킬이 하나도 없어서, 매 세션 사람이 규칙을 다시 상기시켜야 하고 실행이 일관되지 않는다.

**목표**: 이 위키를 **지속적으로 관리할 하네스**로 만든다.

- 운영 워크플로우를 재현 가능한 스킬로 코드화한다.
- 취업 준비뿐 아니라 **취업 이후 커리어 방향**까지 관리하는 "커리어 사고 레이어" 스킬을 추가한다.
- 스킬을 앞으로 계속 찍어낼 **생성기(skill-creator)** 를 먼저 만든다.
- 하네스 운영을 강제하는 **글로벌 규칙**(커밋&푸시 / 셀프임프루빙 / 모호시 질문)을 레포에 심는다.

## 2. Non-Goals

- 임베딩 기반 RAG나 외부 검색엔진(qmd 등) 도입 — 현 규모에서는 `index.md`로 충분. 나중에 필요하면 별도 스펙.
- employment 프로젝트의 방법론 템플릿(A1~H1)을 위키로 복사 — `CLAUDE.md` §6 유지. 위키 스킬은 그와 별개다.
- 회고 캡처 / 커리어 방향 점검 스킬 — 이번 범위 밖. 나중에 `skill-creator`로 추가.
- machine-global(`~/.claude/`) 설정 — 사용자가 명시적으로 거부. 모든 것은 레포 안에.

## 3. 확정된 설계 결정 (Q&A 결과)

| 결정 | 값 | 근거 |
|---|---|---|
| 스킬 경계 | 운영 3종 + 커리어 사고 2종 | 위키가 지식 저장 + 사고 도구 둘 다 담당 |
| 커리어 사고 우선순위 | 면접 대비 · 의사결정 저널 | 회고캡처/방향점검은 후순위 |
| skill-creator 성격 | **범용** 생성기 | 위키 외 스킬도 찍어낼 수 있게. 위키 규약은 `_shared/`로 분리 |
| 운영 스킬 이름 | `wiki-` 접두어 | 네임스페이스 명확화 |
| 자연어 트리거 | 필수 | "위키화해줘" 등으로 적절 스킬 자동 로딩 |
| 세 글로벌 규칙 범위 | **이 레포에만** | 클론 이식성. 다른 PC에서 클론해도 동일 적용, 전역 오염 없음 |
| 커밋&푸시 방식 | **작업 완료 시 규칙기반** (훅 아님) | push는 되돌리기 어려움 → 맥락 인식 필요. 규칙이 git으로 이식됨 |
| 셀프임프루빙 저장소 | **레포 내 `.claude/LESSONS.md`** | 기본 메모리 디렉터리는 machine-local이라 클론에 안 따라옴 |

## 4. 아키텍처 — `.claude/` 패키지 레이아웃

```
.claude/
├── LESSONS.md                          # 셀프임프루빙 로그 (레포 커밋, 세션 시작 시 필독)
└── skills/
    ├── _shared/
    │   └── wiki-conventions.md          # 위키 규약 요약 + CLAUDE.md 포인터 (DRY 단일 출처)
    ├── skill-creator/
    │   ├── SKILL.md
    │   ├── references/
    │   │   └── skill-authoring-best-practices.md
    │   └── templates/
    │       └── SKILL.template.md
    ├── wiki-ingest/SKILL.md
    ├── wiki-query/SKILL.md
    ├── wiki-lint/SKILL.md
    ├── interview-prep/SKILL.md
    └── decision-journal/SKILL.md
```

**설계 원칙**

- **Progressive disclosure**: `SKILL.md`는 짧게(언제·무엇을·순서), 세부 규칙/예시는 `references/`로. (Anthropic 스킬 저작 best practice)
- **DRY**: 위키 스킬들은 `CLAUDE.md` 규칙을 복붙하지 않고 `_shared/wiki-conventions.md`와 `CLAUDE.md`를 참조.
- **식별자 규약**: 스킬 디렉터리/`name`은 ascii 소문자-하이픈. `description`/본문은 한국어.

## 5. `skill-creator` (범용 생성기) — 가장 먼저 구축

목적: 어떤 스킬이든 정석 구조로 스캐폴딩하는 재사용 생성기. 이후 모든 스킬은 손이 아니라 이걸로 만든다.

동작 순서:

1. 새 스킬 정보 수집 — `name`(ascii-kebab), `description`(트리거 포함), 본문 개요, 필요한 `references/`·`templates/`·`scripts/` 여부. 모호하면 AskUserQuestion.
2. `templates/SKILL.template.md`를 채워 `.claude/skills/<name>/SKILL.md` 생성 + 필요한 하위 폴더/스텁 생성.
3. `references/skill-authoring-best-practices.md` 체크리스트로 자가검증:
   - `name`이 디렉터리와 일치하고 ascii-kebab인가
   - `description`이 **"언제 쓰는지(트리거)" + "무엇을 하는지"** 를 3인칭으로 담았는가
   - 시간민감/휘발성 정보가 본문에 하드코딩되지 않았는가
   - `SKILL.md`가 간결하고 세부는 references로 밀어냈는가
4. 위키용 스킬을 만들 때는 "본문에서 `_shared/wiki-conventions.md`를 참조하라"고 안내(생성기 자체는 위키를 모르지만, 위키 스킬 생성 시 이 참조를 넣도록 템플릿이 유도).

산출물: `SKILL.template.md`, `skill-authoring-best-practices.md`, `skill-creator/SKILL.md`.

## 6. 생성할 스킬 5종

각 스킬은 `skill-creator`로 생성하며, `description`에 한국어 트리거 문구를 넣어 자연어로 자동 로딩되게 한다.

### 6.1 `wiki-ingest` (운영 · ingest)
- **하는 일**: raw에 원본 추가 → 핵심 논의 → 관련 wiki 페이지 갱신/신설 → 도메인 `index.md`·루트 `log.md` 갱신. (`CLAUDE.md` §5 Ingest 그대로)
- **트리거(자연어)**: "위키화해줘", "이거 위키에 넣어줘", "위키에 반영/정리해줘", "새 소스 추가", "ingest".
- **건드리는 계층**: raw(추가만), people/concepts/companies(갱신·신설), index, log.
- **불변식**: raw는 절대 수정하지 않는다. 중복은 캐논 페이지 + `sources:` 링크로 해소.

### 6.2 `wiki-query` (운영 · query)
- **하는 일**: 관련 도메인 `index.md` 먼저 읽고 → 관련 페이지 종합·인용 답변 → 재사용 가치 있으면 페이지로 파일백 제안.
- **트리거(자연어)**: "위키에서 찾아줘/알려줘", "위키 기준으로 ~", 이승현의 축적된 지식에 대한 질문.
- **주의**: 일반 잡담 Q&A까지 삼키지 않도록 description에 "위키 지식 기반 질의일 때"로 범위 한정.

### 6.3 `wiki-lint` (운영 · lint)
- **하는 일**: 페이지 간 모순, stale 주장, 고아 페이지, 누락 상호링크, 페이지 없는 개념, 데이터 공백 점검 → 수정 제안/적용.
- **트리거(자연어)**: "위키 점검/린트/건강검진", "모순 찾아줘", "오래된 내용 있나 봐줘".

### 6.4 `interview-prep` (커리어 사고 · 특수 query)
- **하는 일**: 대상 기업 페이지 + `people/이승현` + `concepts/자기인식_약점클러스터` + `concepts/성과지표`를 읽어 **예상 질문 + 답변 스캐폴드** 생성. IKC 면접에서 드러난 "즉흥 자기질문에 약함"을 겨냥해 자기질문 대비를 강화.
- **트리거(자연어)**: "<회사> 면접 준비/대비", "예상질문 뽑아줘", "면접 준비 도와줘".
- **출력**: 마크다운(질문/모범답변 뼈대). 가치 있으면 해당 회사 페이지에 파일백 제안.

### 6.5 `decision-journal` (커리어 사고 · 특수 ingest)
- **하는 일**: 오퍼 수락/거절·직무 선택·방향 전환 같은 결정을 **근거·대안·당시 맥락과 함께** 기록 → `concepts/`에 결정 페이지 신설 → `people/이승현` 및(있으면) 방향 페이지에 링크 → log 기록.
- **트리거(자연어)**: "이 결정 기록해줘", "의사결정 저널", "오퍼 받았는데 정리해줘", "방향 정했어".
- **취업 이후 확장의 핵심**: 커리어 방향 결정들이 여기에 누적된다.

## 7. 자연어 트리거 / 디스커버리 설계

요구사항: 사용자가 "위키화해줘"류 자연어를 말하면 적절한 위키 스킬이 자동 로딩되어야 한다.

- 각 `SKILL.md`의 `description`은 Claude Code가 스킬 로딩을 판단하는 근거다. 따라서 위 6.x의 **트리거 문구를 description에 명시**한다.
- 대표 매핑: "위키화/위키에 넣어/정리해줘" → `wiki-ingest` · "위키에서 찾아/알려줘" → `wiki-query` · "위키 점검/린트" → `wiki-lint` · "면접 준비" → `interview-prep` · "결정 기록" → `decision-journal`.
- `CLAUDE.md`에 짧은 "스킬 카탈로그 + 트리거" 표를 추가해 사람·LLM 모두 발견 가능하게 한다.

## 8. 세 글로벌 규칙 (이 레포 한정, `CLAUDE.md`에 신설 §7)

훅이 아니라 **CLAUDE.md 규칙 + 레포 커밋 파일**로 구현한다 → `git clone` 시 그대로 따라오고 machine-global 설정이 없다.

1. **작업 완료 후 필수 `git commit & push`**
   - 파일을 변경한(= 실제 작업이 끝난) 턴에는 durable 승인 하에 자동으로 `git add` → `commit` → `push`.
   - 단순 질문답변/탐색만 한 턴은 예외.
   - 커밋 메시지는 무엇을 왜 바꿨는지 한 줄 요약 + 필요 시 본문.
2. **셀프 임프루빙 (강한 강제)**
   - 사용자가 피드백을 주거나, 회고 중 내 실수를 발견하면 **즉시 `.claude/LESSONS.md`에 `- [YYYY-MM-DD] 교훈 / 왜 / 어떻게 적용` 형식으로 append** 하고 두 번 다시 반복하지 않는다.
   - **매 세션 시작 시 `.claude/LESSONS.md`를 반드시 읽고** 그 교훈을 준수한다.
3. **모호하면 AskUserQuestion**
   - 요구사항·범위·방식에 조금이라도 모호함이 있으면 추측하지 말고 반드시 AskUserQuestion으로 물어본다.

`.claude/LESSONS.md`는 헤더 + append-only 항목 리스트로 시작한다(초기엔 이 하네스 구축에서 얻은 교훈 몇 개를 시드).

## 9. 빌드 순서 (phase)

- **Phase 0 — 뼈대**: `.claude/skills/` 생성, `.claude/LESSONS.md` 시드, `_shared/wiki-conventions.md` 작성.
- **Phase 1 — 생성기**: `skill-creator`(SKILL.md + best-practices 레퍼런스 + SKILL.template.md).
- **Phase 2 — 운영 3종**: `skill-creator`로 `wiki-ingest` → `wiki-query` → `wiki-lint` 생성.
- **Phase 3 — 커리어 2종**: `skill-creator`로 `interview-prep` → `decision-journal` 생성.
- **Phase 4 — 글로벌 규칙**: `CLAUDE.md`에 §7 규칙 + 스킬 카탈로그/트리거 표 추가.
- 각 스킬 생성/문서 변경 시 `log.md`에 기록, phase 끝마다 commit & push(규칙 #1의 첫 적용).

## 10. 검증 방법

- **구조 검증**: 각 `SKILL.md` frontmatter에 `name`(디렉터리 일치, ascii-kebab)·`description`(트리거+동작) 존재. 본문에 시간민감 하드코딩 없음.
- **동작 검증(드라이런)**: 생성 후 대표 트리거 문구로 각 스킬이 로딩·수행되는지 1건씩 리허설.
  - `wiki-ingest`: 더미/실제 소스 1건 ingest → 관련 페이지·index·log가 실제로 갱신되는지.
  - `wiki-query`: 기존 지식 1건 질의 → 인용 포함 답변.
  - `wiki-lint`: 현재 위키에 대해 1회 실행 → 고아/모순 리포트가 나오는지.
  - `interview-prep`: 한 회사로 예상질문 세트 생성.
  - `decision-journal`: 더미 결정 1건 기록 → concept 페이지 생성·링크·log.
- **규칙 검증**: 작업 완료 턴에 commit&push가 실제 발생하는지, LESSONS append가 동작하는지.

## 11. 리스크 / 유의점

- **wiki-query가 일반 Q&A를 과도하게 삼킬 위험** → description 범위 한정으로 완화.
- **commit&push가 미완성 상태를 밀어낼 위험** → "작업이 끝난 턴"으로 한정, 훅 대신 맥락 인식 규칙 사용.
- **LESSONS.md 비대화** → 항목은 짧게(1~3줄), 주기적으로 lint 때 정리.
- **skill-creator 범용성 ↔ 위키 편의 충돌** → 생성기는 범용 유지, 위키 특화는 템플릿의 "위키면 `_shared` 참조" 안내로만 스며들게.

## 12. Open Questions

- 없음(핵심 결정은 §3에서 모두 확정). 구현 중 새 모호점 발생 시 규칙 #3에 따라 AskUserQuestion.
