#!/usr/bin/env python3
"""비공개 원본 위키 -> 이 공개 저장소로 허용목록 기반 단방향 동기화.

제외목록이 아니라 허용목록을 쓰는 이유: 원본에 새 파일이 생겼을 때
제외목록 방식은 기본값이 "공개"라 자동으로 샌다. 허용목록은 기본값이 "비공개"다.

복사 후 익명화 규칙을 적용하고, 민감 패턴이 하나라도 남으면 비정상 종료한다.

    python scripts/sync_public.py --source ../seungheyon-wiki
    python scripts/sync_public.py --source ../seungheyon-wiki --check-only
"""
import argparse
import os
import re
import shutil
import sys

BS = chr(92)  # 역슬래시. 정규식 소스에 리터럴로 두면 편집 과정에서 깨지기 쉬워 상수로 조립한다.
WIN_PATH = "C:" + BS + BS + "study|C:/study|/c/study"

# 원본 기준 상대경로. 디렉터리는 통째로, 파일은 그 파일만 복사한다.
ALLOWLIST = [
    "CLAUDE.md",
    ".claude/skills",
    ".claude/LESSONS.md",
    "reference/llm-wiki.md",
    "scripts/build-graph.mjs",
    "scripts/graph-template.html",
    "scripts/notion_retrospect_sync.py",
    "scripts/notion_tasks.py",
    "docs/superpowers",
]

# 이 저장소에서만 관리하는 파일. 동기화가 덮어쓰지 않는다.
LOCAL_ONLY = ["README.md", "index.md", "examples", "scripts/sync_public.py", ".gitignore"]

# (정규식, 치환문자열) — 복사된 파일에 적용한다.
REDACTIONS = [
    ("`C:" + BS + BS + "study" + BS + BS + "myfolder" + BS + BS
     + r"seunghyeon-resume` \(GitHub `[^`]+`, private\)",
     "웹 이력서 저장소 (로컬 클론 경로는 환경에 따라 다름)"),
    # 남은 로컬 클론 경로는 저장소 이름만 남긴다.
    ("C:" + BS + BS + "study" + BS + BS + "myfolder" + BS + BS + r"([A-Za-z0-9._-]+)",
     r"<\1 저장소 로컬 경로>"),
    (r"C:/study/myfolder/([A-Za-z0-9._-]+)", r"<\1 저장소 로컬 경로>"),
    (r"`anj" + "eongkyun`", "`<mentor>`"),
    (r"가족 구성원\(이정" + "현\)", "가족 구성원"),
]

# 하나라도 남아 있으면 커밋을 막는다.
FORBIDDEN = [
    (WIN_PATH, "로컬 절대경로"),
    (r"(?<!\d)01[016789][-. ]?\d{3,4}[-. ]?\d{4}(?!\d)", "휴대폰 번호"),
    (r"[A-Za-z0-9._%+-]+@(naver|gmail|daum|kakao)\.(com|net)", "개인 이메일"),
    (r"안정균|anjeongkyun", "멘토 실명/핸들"),
    (r"이정현", "가족 구성원 실명"),
    (r"workers\.dev|be-assignment", "비공개 서비스/과제 URL"),
    (r"\b[0-9a-f]{32}\b", "노션 페이지·DB ID"),
    (r"(sk-[A-Za-z0-9]{20,}|ghp_\w+|github_pat_\w+|xox[baprs]-|AKIA[0-9A-Z]{16})", "자격증명"),
]

TEXT_EXT = {".md", ".txt", ".py", ".mjs", ".js", ".html", ".json", ".yml", ".yaml"}


def copy_entry(src_root, dst_root, rel):
    src = os.path.join(src_root, rel)
    dst = os.path.join(dst_root, rel)
    if not os.path.exists(src):
        print(f"  ! 원본에 없음, 건너뜀: {rel}")
        return 0
    os.makedirs(os.path.dirname(dst) or dst_root, exist_ok=True)
    if os.path.isdir(src):
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        return sum(len(f) for _, _, f in os.walk(dst))
    shutil.copy2(src, dst)
    return 1


def redact_tree(root):
    changed = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for name in filenames:
            path = os.path.join(dirpath, name)
            if os.path.abspath(path) == os.path.abspath(__file__):
                continue  # 패턴 정의가 스스로 치환되는 것을 막는다
            if os.path.splitext(name)[1].lower() not in TEXT_EXT:
                continue
            try:
                text = open(path, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue
            new = text
            for pattern, repl in REDACTIONS:
                new = re.sub(pattern, repl, new)
            if new != text:
                open(path, "w", encoding="utf-8", newline="").write(new)
                changed += 1
    return changed


def scan_tree(root):
    hits = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for name in filenames:
            path = os.path.join(dirpath, name)
            if os.path.abspath(path) == os.path.abspath(__file__):
                continue  # 패턴 정의 자체가 매치되므로 제외
            if os.path.splitext(name)[1].lower() not in TEXT_EXT:
                continue
            try:
                lines = open(path, encoding="utf-8").read().splitlines()
            except (UnicodeDecodeError, OSError):
                continue
            for lineno, line in enumerate(lines, 1):
                for pattern, label in FORBIDDEN:
                    if re.search(pattern, line):
                        rel = os.path.relpath(path, root).replace("\\", "/")
                        hits.append((rel, lineno, label))
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="../seungheyon-wiki", help="비공개 원본 위키 경로")
    ap.add_argument("--check-only", action="store_true", help="복사 없이 민감 패턴 검사만")
    args = ap.parse_args()

    dst_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_root = os.path.abspath(args.source)

    if not args.check_only:
        if not os.path.isdir(src_root):
            sys.exit(f"원본 경로를 찾을 수 없다: {src_root}")
        print(f"동기화: {src_root} -> {dst_root}")
        print(f"이 저장소 전용 파일은 건드리지 않는다: {', '.join(LOCAL_ONLY)}")
        total = 0
        for rel in ALLOWLIST:
            n = copy_entry(src_root, dst_root, rel)
            total += n
            print(f"  + {rel} ({n})")
        print(f"복사 {total}건")
        print(f"익명화 적용: {redact_tree(dst_root)}개 파일 수정")

    hits = scan_tree(dst_root)
    if hits:
        print("\n민감 패턴이 남아 있다. 커밋하지 말 것:", file=sys.stderr)
        for rel, lineno, label in hits:
            print(f"  {rel}:{lineno}  [{label}]", file=sys.stderr)
        sys.exit(1)
    print("민감 패턴 검사 통과")


if __name__ == "__main__":
    main()
