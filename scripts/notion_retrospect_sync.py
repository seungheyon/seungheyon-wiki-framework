#!/usr/bin/env python3
"""노션 "회고" 페이지 하위의 주간 회고를 self-model/raw/회고/ 로 편입한다.

    python scripts/notion_retrospect_sync.py            # 전체
    python scripts/notion_retrospect_sync.py --limit 1  # 앞 N건만
    python scripts/notion_retrospect_sync.py --dry-run  # 파일을 쓰지 않고 결과만

자격증명은 .secrets/notion.json 에서 읽는다(gitignore 대상).

파일명은 노션 페이지 **제목의 날짜**를 쓴다. `created_time`은 15건 전부
일괄 이관일(2026-05-25)로 찍혀 있어 쓸 수 없다는 것이 2026-08-13 실측으로 확인됐다.

child_page 블록은 따라 들어가지 않는다. 실제로 존재하는 2건(251214 회고 하위의
"정제 데이터" 2종)이 회고 원문이 아니라 당시 LLM 정제 산출물이기 때문이다.
제외했다는 사실은 해당 파일 머리말에 남긴다.
"""
import argparse
import io
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRETS = os.path.join(ROOT, ".secrets", "notion.json")
OUT_DIR = os.path.join(ROOT, "self-model", "raw", "회고")

# 노션 제목에서 날짜를 뽑는다. "251207 회고" → 251207
TITLE_DATE = re.compile(r"(\d{6})")


def load_config():
    with io.open(SECRETS, encoding="utf-8") as f:
        return json.load(f)


class Notion:
    def __init__(self, token, version):
        self.token = token
        self.version = version

    def get(self, url):
        req = urllib.request.Request(url, headers={
            "Authorization": "Bearer " + self.token,
            "Notion-Version": self.version,
        })
        return json.load(urllib.request.urlopen(req))

    def children(self, block_id):
        """페이지네이션을 따라가며 자식 블록을 전부 모은다."""
        out, cursor = [], None
        while True:
            url = "https://api.notion.com/v1/blocks/%s/children?page_size=100" % block_id
            if cursor:
                url += "&start_cursor=" + cursor
            data = self.get(url)
            out.extend(data["results"])
            cursor = data.get("next_cursor")
            if not cursor:
                break
        return out


def rich_text(items):
    """노션 rich_text를 마크다운으로. 서식과 링크를 살린다."""
    parts = []
    for r in items:
        text = r.get("plain_text", "")
        if not text:
            continue
        ann = r.get("annotations", {})
        # 코드가 가장 안쪽이어야 다른 서식과 겹칠 때 깨지지 않는다.
        if ann.get("code"):
            text = "`%s`" % text
        if ann.get("bold"):
            text = "**%s**" % text
        if ann.get("italic"):
            text = "*%s*" % text
        if ann.get("strikethrough"):
            text = "~~%s~~" % text
        href = r.get("href")
        if href:
            text = "[%s](%s)" % (text, href)
        parts.append(text)
    return "".join(parts)


def block_text(block):
    body = block.get(block["type"])
    if isinstance(body, dict) and "rich_text" in body:
        return rich_text(body["rich_text"])
    return ""


def render(client, blocks, depth, lines, skipped):
    """블록 목록을 마크다운 줄로 변환한다. 중첩은 들여쓰기로 표현한다."""
    indent = "  " * depth
    numbering = 0

    for block in blocks:
        btype = block["type"]
        text = block_text(block)

        if btype == "child_page":
            skipped.append(block["child_page"]["title"])
            continue

        if btype != "numbered_list_item":
            numbering = 0

        if btype == "heading_1":
            lines.append("")
            lines.append("## " + text)  # 파일 제목이 #이므로 한 단계 내린다
            lines.append("")
        elif btype == "heading_2":
            lines.append("")
            lines.append("### " + text)
            lines.append("")
        elif btype == "heading_3":
            lines.append("")
            lines.append("#### " + text)
            lines.append("")
        elif btype == "bulleted_list_item":
            lines.append(indent + "- " + text)
        elif btype == "numbered_list_item":
            numbering += 1
            lines.append(indent + "%d. " % numbering + text)
        elif btype == "to_do":
            done = block["to_do"].get("checked")
            lines.append(indent + ("- [x] " if done else "- [ ] ") + text)
        elif btype == "quote":
            lines.append(indent + "> " + text)
        elif btype == "code":
            lang = block["code"].get("language", "")
            lines.append(indent + "```" + (lang if lang != "plain text" else ""))
            lines.extend(indent + l for l in text.split("\n"))
            lines.append(indent + "```")
        elif btype == "divider":
            lines.append("")
            lines.append("---")
            lines.append("")
        elif btype == "callout":
            lines.append(indent + "> " + text)
        elif btype == "paragraph":
            lines.append(indent + text if text else "")
        else:
            # 알 수 없는 타입은 버리지 않고 표시해 둔다. 나중에 눈에 띄어야 한다.
            lines.append(indent + ("<!-- 미처리 블록: %s --> %s" % (btype, text)).rstrip())

        if block.get("has_children"):
            render(client, client.children(block["id"]), depth + 1, lines, skipped)


def normalize(lines):
    """빈 줄이 세 줄 이상 이어지지 않게 정리한다."""
    out, blank = [], 0
    for line in lines:
        if line.strip() == "":
            blank += 1
            if blank > 1:
                continue
        else:
            blank = 0
        out.append(line.rstrip())
    while out and out[0] == "":
        out.pop(0)
    while out and out[-1] == "":
        out.pop()
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    cfg = load_config()
    client = Notion(cfg["api_token"], cfg["notion_version"])

    pages = [(b["child_page"]["title"].strip(), b["id"])
             for b in client.children(cfg["retrospect_parent_page_id"])
             if b["type"] == "child_page"]
    if args.limit:
        pages = pages[:args.limit]

    if not args.dry_run:
        os.makedirs(OUT_DIR, exist_ok=True)

    for title, page_id in pages:
        match = TITLE_DATE.search(title)
        if not match:
            print("!! 제목에서 날짜를 찾지 못했다: %r — 건너뛴다" % title)
            continue
        date = match.group(1)

        lines, skipped = [], []
        render(client, client.children(page_id), 0, lines, skipped)
        body = normalize(lines)

        header = ["# " + title, ""]
        header.append("> 노션 회고 페이지 원본. 2026-08-19 위키 편입 (page id `%s`)." % page_id)
        if skipped:
            header.append("> 하위 페이지 %d건(%s)은 회고 원문이 아니라 당시 LLM 정제 산출물이라 제외했다."
                          % (len(skipped), ", ".join('"%s"' % s for s in skipped)))
        header.append("")

        content = "\n".join(header + body) + "\n"
        path = os.path.join(OUT_DIR, "회고_%s.md" % date)

        if args.dry_run:
            print("[dry-run] %s  %d줄 %d자  제외 %d건"
                  % (os.path.basename(path), len(body), len(content), len(skipped)))
        else:
            with io.open(path, "w", encoding="utf-8") as f:
                f.write(content)
            print("%s  %d줄 %d자  제외 %d건"
                  % (os.path.basename(path), len(body), len(content), len(skipped)))


if __name__ == "__main__":
    main()
