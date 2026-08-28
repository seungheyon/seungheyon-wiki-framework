---
name: backend-resume
description: 이승현의 백엔드 엔지니어 신입 이력서를 새로 쓰거나 개정할 때 사용한다. "이력서 써줘", "이력서 고쳐줘", "이력서에 반영해줘", "이력서 피드백 줄게", "레쥬메 수정해줘" 같은 요청에서 트리거된다. 위키 캐논 페이지와 사실관계를 먼저 대조해 검증한 뒤, career/raw/이력서/초안/에 HTML 새 버전을 만들어 PDF로 변환하고, 같은 내용을 배포 중인 웹 이력서(seunghyeon-resume.pages.dev)에도 반드시 함께 재배포한다. 개정 근거는 해당 프로젝트의 위키 페이지에 누적 기록한다.
---

# backend-resume

이승현의 **백엔드 엔지니어 신입 지원용 이력서**를 작성·개정한다.
이력서는 위키의 파생 산출물이므로, 쓰기 전에 항상 위키 캐논 페이지를 먼저 읽고 사실관계를 맞춘다.

---

## 언제
- 트리거: "이력서 써줘", "이력서 고쳐줘/수정해줘", "이력서에 반영해줘", "이력서 피드백 줄게", "레쥬메 ~".

---

## 실행 흐름

### 1. 기준 문서 로딩 (건너뛰지 않는다)

수정 범위가 문구 하나여도 아래를 먼저 읽는다. 구조·내용만 지시받았다고 해서 문체·디자인 기준을 잊으면
개정을 거듭할수록 원본 정체성이 무너진다.

- `references/writing-rules.md` — 문체·구조·금지 패턴
- `references/design-conventions.md` — HTML/CSS 규약, 다이어그램 규칙, PDF 생성
- `references/fact-check.md` — 사실 검증 체크리스트
- 직전 최신 초안 (`career/raw/이력서/초안/` 중 가장 높은 날짜·버전) — 이것이 실질 템플릿이다
- 언급되는 프로젝트의 위키 캐논 페이지 (아래 "프로젝트 ↔ 캐논 페이지 대응" 참고)

### 2. 사실 검증

`references/fact-check.md`의 체크리스트를 돌린다. **사용자가 준 피드백이라도 그대로 반영하지 않는다.**
원자료와 어긋나거나 자체 모순(특히 수치)이 있으면 반영 전에 지적하고 확정을 받는다.

검증에서 걸린 항목은 추측으로 메우지 말고 AskUserQuestion으로 확정한다.
경험하지 않은 기술·활동은 어떤 이유로도 쓰지 않는다.

### 3. 모호함 해소

요구사항에 조금이라도 모호함이 있으면 AskUserQuestion을 먼저 쓴다. 특히 아래는 항상 확인 대상이다.

- 고유명사 변경(프로젝트명 등)이 위키의 기존 용어와 충돌하는가
- 수치 변경 시 파생 지표(개선율 등)까지 같이 바뀌어야 하는가
- "이 내용 빼줘"가 라벨 삭제인지 서술 삭제인지
- 새로 등장한 경험이 위키·raw에 근거가 있는가

### 4. 작성

`references/writing-rules.md`의 구조 규칙과 금지 패턴을 지키며 새 버전 HTML을 만든다.
기존 초안을 덮어쓰지 않고 **새 파일**로 만든다 (raw는 불변 — 새 버전 추가는 허용, 기존 파일 수정은 금지).

파일명: `career/raw/이력서/초안/이력서_YYMMDD_<변경요지>_v<n>.html`
날짜는 반드시 `date +%y%m%d`로 확인해서 쓴다. 기억에 의존하지 않는다.

### 5. PDF 변환

`references/design-conventions.md`의 PDF 생성 절차를 따라 같은 이름의 `.pdf`를 만든다.
이미지·SVG가 있으면 렌더링 결과를 확인한다(로컬 상대경로 `assets/`가 깨지지 않았는지).

### 6. 웹 사이트 재배포 (PDF와 항상 같이)

이력서는 PDF와 정적 웹 페이지 두 가지로 배포된다. PDF만 갱신하고 사이트를 두면 링크로 이력서를 본
사람이 옛 버전을 읽게 되므로, **5단계 직후 같은 작업 단위 안에서** 반드시 이어서 한다.

- 사이트: https://seunghyeon-resume.pages.dev
- 저장소: 웹 이력서 저장소 (로컬 클론 경로는 환경에 따라 다름)

`src/resume.html`·`src/resume.pdf`에 새 버전을 복사하고 `npm run deploy`. 절차와 주의사항(이미지
ASCII 파일명, 웹폰트 추가 금지, 별도 저장소 커밋)은 `references/design-conventions.md` §7에 있다.
배경과 설계 근거는 위키 `career/concepts/이력서_웹배포.md`.

배포 후 URL이 200인지 확인하고, 사용자에게 **PDF 경로와 사이트 URL을 함께** 보고한다.

### 7. 위키 동기화

이력서에서 확정된 사실·표현은 위키에도 반영한다. 이력서만 고치고 위키를 두면 다음 산출물이 다시 어긋난다.

- 사실관계가 바뀌었으면(문제 정의 정정, 수치 정정 등) 해당 캐논 페이지 본문을 고치고 `updated:` 갱신
- 개정 경위(무엇을 왜 바꿨는지)는 캐논 페이지의 "이력서 서술 v<n>" 섹션에 누적한다 — 삭제하지 않고 append
- raw는 절대 수정하지 않는다. raw와 위키가 어긋나면 위키에 "정정" 사실을 명시한다

### 8. 마무리

- 루트 `log.md`에 `## [YYYY-MM-DD] ingest | 이력서 v<n> ...` 형식으로 한 줄 추가
  (웹 사이트도 함께 배포했다는 사실을 같은 항목에 적는다)
- 사용자 피드백에서 드러난 내 실수는 `.claude/LESSONS.md`(세션 전반 행동) 또는 이 스킬의
  `references/`(이력서 산출물 품질)에 기록한다 — 후자가 기본값이다
- `git add` → `commit` → `push`

---

## 프로젝트 ↔ 캐논 페이지 대응

| 이력서 프로젝트 | 캐논 페이지 |
|---|---|
| 가족 아카이브 | `projects/concepts/프로젝트_가족아카이브.md` |
| 커리어 나침반 (AI 어시스턴트) | `career/concepts/프로젝트_Compass-Companion.md` |
| MVPQuest | `career/concepts/프로젝트_MVPQuest.md` |
| Coupong | `career/concepts/프로젝트_Coupong.md` |
| 자기소개 배경 | `career/concepts/커리어나침반.md`, `career/people/이승현.md` |
| 수치 검증 | `career/concepts/성과지표.md` |

> **용어 주의**: `커리어 나침반`은 (1) 노션 기반 주간 회고·목표 관리 시스템, (2) 그 데이터를 쓰는 AI
> 어시스턴트 프로젝트(구 Compass Companion) 두 가지를 가리킨다. 이력서 프로젝트 섹션의 "커리어 나침반"은
> (2)이며, (1)은 "주간 회고 노션 문서" 등으로 풀어 써서 충돌을 피한다.

---

## 참고
- 문체·구조: `references/writing-rules.md`
- 디자인·PDF: `references/design-conventions.md`
- 사실 검증: `references/fact-check.md`
- 웹 배포: `references/design-conventions.md` §7, 위키 `career/concepts/이력서_웹배포.md`
- 위키 규약: `.claude/skills/_shared/wiki-conventions.md`, 루트 `CLAUDE.md`
