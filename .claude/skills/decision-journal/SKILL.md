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
