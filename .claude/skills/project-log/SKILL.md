---
name: project-log
description: 진행 중인 사이드 프로젝트에 설계 논의나 의사결정을 계속 추가할 때 사용한다. "<프로젝트>에 이 논의/결정 기록해줘", "설계 바뀐 거 반영해줘" 같은 요청에서 트리거된다. projects 도메인의 프로젝트 허브 페이지에 결정을 append하고 링크한다.
---

# project-log

진행 중인 사이드 프로젝트의 설계 변경·의사결정을 근거와 함께 위키에 남긴다(특수 ingest, decision-journal의 프로젝트 버전).

## 언제
- 트리거: "<프로젝트>에 이 결정 기록해줘", "설계 논의 정리해줘", "방향 바뀐 거 반영해줘".
- 대상 프로젝트 페이지(`projects/concepts/프로젝트_<이름>.md`)가 아직 없으면 이 스킬 대신 [[project-kickoff]]을 먼저 실행한다.

## 순서
1. **결정 수집** — 무엇을 결정했나 / 고려한 대안 / 선택 근거 / 계기(어떤 논의·이슈에서 나왔나). 빠진 항목은 AskUserQuestion.
2. **페이지 생성** — `projects/concepts/decisions/결정_<프로젝트>_<주제>_<YYYYMMDD>.md` 신설(`type: concept`, `domain: projects`). 폴더가 없으면 새로 만든다.
3. **허브 갱신** — `projects/concepts/프로젝트_<이름>.md`의 "설계 로그" 섹션에 `[[decisions/결정_...]]` 형태로 이 결정으로 나가는 링크 추가. 결정 페이지에서 허브로 돌아오는 링크는 `[[../프로젝트_...]]`로 상대경로를 붙인다. 결정이 MVP 요구사항 자체를 바꿨다면(범위 추가/제외, 우선순위 변경 등) 해당 섹션도 함께 갱신한다.
4. **로그** — 루트 `log.md`에 `## [YYYY-MM-DD] ingest | <프로젝트> 결정: 제목` append, 필요 시 `projects/index.md` 갱신.
5. **완료** — 규칙 #1에 따라 커밋 & 푸시.

## 참고
- 규약: `.claude/skills/_shared/wiki-conventions.md`, `CLAUDE.md` §1("projects 도메인 전용 규칙")
- career 도메인의 [[decision-journal]]과 동일 패턴, 대상 도메인만 다르다.
