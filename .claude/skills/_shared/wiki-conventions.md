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
domain: career
tags: [태그]
updated: YYYY-MM-DD
sources:
  - "[[raw/경로/파일명]]"
status: null | 진행중 | 종료 | 대기
---
```

## 위키링크
- 내부 참조는 항상 `[[페이지명]]` (확장자 없이).
- raw도 `[[career/raw/…]]`로 링크.
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
