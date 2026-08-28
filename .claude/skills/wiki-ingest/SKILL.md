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
