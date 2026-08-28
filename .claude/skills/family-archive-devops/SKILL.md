---
name: family-archive-devops
description: 가족 아카이브 프로젝트의 배포/인프라 작업(호스팅 연결, 스토리지·DB 프로비저닝, 환경변수/시크릿, CI/CD)을 할 때 사용한다. "가족아카이브 배포하자", "가족아카이브 인프라 설정해줘", "가족아카이브 CI/CD 만들어줘" 같은 요청에서 트리거된다. 위키의 기술 스택 결정을 근거로 구현 저장소(family-archive)·클라우드 플랫폼을 설정한다.
---

# family-archive-devops

가족 아카이브 프로젝트 전용 배포/인프라 스킬. 이 프로젝트에 한정된 구체적 컨텍스트를 담고 있다(다른 프로젝트에는 재사용하지 않는다 — 새 프로젝트가 생기면 그 프로젝트 전용 스킬을 새로 만든다).

## 언제
- 트리거: "가족아카이브 배포하자", "가족아카이브 인프라 설정해줘", "가족아카이브 CI/CD 만들어줘", "가족아카이브 환경변수 등록해줘".

## 핵심 컨텍스트 (고정)
- **구현 저장소**: `<family-archive 저장소 로컬 경로>`
- **설계 원본**: `projects/concepts/decisions/결정_가족아카이브_기술스택_20260728.md` + `projects/concepts/decisions/결정_가족아카이브_배포플랫폼정정_20260729.md`(배포 대상 정정 — Pages 아니라 Workers)
- **호스팅/CI-CD**: **Cloudflare Workers** + Workers Builds(Workers 자체 Git 연동) — GitHub 저장소 연결 시 push마다 자동 빌드·배포. 별도 GitHub Actions 파이프라인은 만들지 않는다. (Cloudflare Pages가 아님 — OpenNext 어댑터가 Worker 번들로 빌드하기 때문.)
- **인프라 구성**: Cloudflare R2(사진 원본 버킷) + Supabase(Postgres, Auth/Storage는 안 씀) + Cloudflare Workers(API — OpenNext 어댑터가 Next.js Route Handler를 포함한 앱 전체를 하나의 Worker로 빌드). 인증은 별도 서비스 없이 그 안에서 직접 구현.
- **환경변수/시크릿**: Cloudflare 대시보드(Worker 프로젝트 설정, 또는 `wrangler secret put`)에 등록 — Supabase URL/키(publishable/secret) 등은 Secret으로, R2는 `wrangler.toml`에 바인딩 선언(예: `binding = "PHOTOS_BUCKET"`).

## 순서
1. **최신 확인** — 작업 시작 전 `projects/concepts/decisions/결정_가족아카이브_기술스택_20260728.md`를 다시 읽어 위 "핵심 컨텍스트"가 그 사이 바뀌지 않았는지 확인(project-log로 갱신됐을 수 있음).
2. **인프라 작업** — `<family-archive 저장소 로컬 경로>`에서 `wrangler.toml` 등 설정 파일 작성, R2/Supabase 연결 코드, Cloudflare **Workers** Git 연동(Workers Builds) 안내를 진행한다. 계정 로그인·결제 등 사용자 본인이 해야 하는 대시보드 조작은 직접 실행하지 않고 안내만 한다.
3. **비밀정보** — API 키·DB URL·비밀번호 등은 절대 wiki에 기록하지 않는다. 구현 저장소의 `.env`(gitignore 대상) 또는 Cloudflare/Supabase 대시보드/시크릿 스토어에만 둔다. wiki에는 "어떤 값이 어디에 등록되었다"는 사실만 남긴다.
4. **새 설계 결정 발생 시** — 인프라 구성이 기존 기술스택 결정과 달라지거나 새로 정해야 하는 부분이 생기면 `project-log`로 wiki에 먼저 남긴 뒤 진행하고, 이 스킬의 "핵심 컨텍스트"도 함께 갱신한다.
5. **완료** — `family-archive`/인프라 변경은 매 작업 단위 종료 시 사용자에게 확인받은 뒤 커밋·푸시·적용한다(자동 아님). 배포·인프라 변경은 되돌리기 어려울 수 있으니 실행 전 사용자에게 명확히 알린다. wiki 쪽 파일을 바꿨다면 규칙 #1에 따라 자동 커밋·푸시.

## 참고
- 공통 안전수칙: `.claude/skills/_shared/implementation-conventions.md`
- UI/UX는 `family-archive-designer`, 기능 구현은 `family-archive-developer`가 담당.
