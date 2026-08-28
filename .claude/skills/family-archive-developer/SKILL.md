---
name: family-archive-developer
description: 가족 아카이브 프로젝트를 실제로 개발(프론트엔드+백엔드 통합, 풀스택)할 때 사용한다. "가족아카이브 개발해줘", "가족아카이브 이 기능 구현해줘", "가족아카이브 코드 작성해줘" 같은 요청에서 트리거된다. 위키의 MVP 요구사항·기술 스택 결정을 근거로 구현 저장소(family-archive)에 코드를 작성한다.
---

# family-archive-developer

가족 아카이브 프로젝트 전용 풀스택 개발 스킬. 이 프로젝트에 한정된 구체적 컨텍스트를 담고 있다(다른 프로젝트에는 재사용하지 않는다 — 새 프로젝트가 생기면 그 프로젝트 전용 스킬을 새로 만든다). 프론트엔드/백엔드를 나누지 않고 풀스택 하나로 다룬다(Next.js가 경계를 흐리고, 1인 개발 MVP에서 UI 판단은 어차피 `family-archive-designer`가 담당하므로 분리 실익이 적다는 판단 — 필요해지면 나중에 스킬을 쪼갠다).

## 언제
- 트리거: "가족아카이브 개발해줘", "가족아카이브 이 기능 구현해줘", "가족아카이브 코드 작성/수정해줘".

## 핵심 컨텍스트 (고정)
- **구현 저장소**: `<family-archive 저장소 로컬 경로>`
- **설계 원본**: `projects/concepts/프로젝트_가족아카이브.md` + `projects/concepts/decisions/결정_가족아카이브_*`
- **기술 스택**: Next.js(React) + OpenNext Cloudflare 어댑터(`@opennextjs/cloudflare`, 구 `next-on-pages`는 쓰지 않음) + **Cloudflare Workers**(API 포함, Next.js Route Handler가 Worker 번들에 통합됨 — Cloudflare Pages 아님, 2026-07-29 정정: `projects/concepts/decisions/결정_가족아카이브_배포플랫폼정정_20260729.md` 참고) + Cloudflare R2(사진 원본 저장) + Supabase(Postgres 부분만, 메타데이터 저장).
- **MVP 포함 범위**: 관리자(이승현) 1인만 사진 개별/수동 업로드(카톡 파일 파싱 없음, 기존/신규 사진 동일 방식) → 업로드 API 안에서 pure-JS(`exifr` 등)로 EXIF(촬영일자/GPS) 추출·Supabase 저장, 원본은 R2 업로드 → 여행/행사 단위 앨범 그룹핑(EXIF 기준 1차 자동 분류 + 관리자 수동 2차 확인, 메타데이터 없으면 바로 수동 분류) → 앨범 목록/그리드 뷰(날짜순) → 비공개 링크+비밀번호(계정 로그인 없음, Worker 안에서 비밀번호 비교+세션 쿠키로 직접 구현).
- **MVP 제외/미채택**: 가족 직접 업로드, 태그/인물 검색, 개인별 로그인, 카톡 자동 감지 자동화(로컬 폴더 워처 등 — 후순위가 아니라 안 만들기로 확정), 썸네일/리사이징(필요성 못 느껴 보류, Cloudflare Images는 나중에 필요해지면 검토).
- **인프라 설정 자체(계정 생성, 버킷/프로젝트 프로비저닝, 시크릿 등록)는 `family-archive-devops`가 담당** — 이 스킬은 그 위에서 도는 애플리케이션 코드만 다룬다.

## 순서
1. **최신 확인** — 작업 시작 전 `projects/concepts/프로젝트_가족아카이브.md`를 다시 읽어 위 "핵심 컨텍스트"가 그 사이 바뀌지 않았는지 확인(project-log로 갱신됐을 수 있음).
2. **범위 확인** — 지금 구현하려는 게 MVP "포함" 범위인지 확인한다. "제외/미채택" 항목을 구현하려는 요청이면 먼저 사용자에게 범위가 바뀐 건지 확인한다(스코프 임의 확장 금지).
3. **구현** — `<family-archive 저장소 로컬 경로>`에서 실제 코드를 작성·수정한다. cwd·git 안전수칙은 `.claude/skills/_shared/implementation-conventions.md` 참고.
4. **새 설계/기술 결정 발생 시** — 요구사항 해석이 갈리거나 기술적 선택이 새로 필요하면 코드부터 짜지 말고 `project-log`로 wiki에 먼저 결정을 남긴 뒤 구현하고, 이 스킬의 "핵심 컨텍스트"도 함께 갱신한다.
5. **완료** — `family-archive`는 매 작업 단위 종료 시 사용자에게 커밋·푸시 여부를 확인한다(자동 아님). wiki 쪽 파일을 바꿨다면 규칙 #1에 따라 자동 커밋·푸시.

## 참고
- 공통 안전수칙: `.claude/skills/_shared/implementation-conventions.md`
- UI/UX 판단은 `family-archive-designer`, 배포/인프라는 `family-archive-devops`가 담당.
