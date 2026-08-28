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
