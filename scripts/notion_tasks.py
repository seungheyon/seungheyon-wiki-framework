#!/usr/bin/env python3
"""멘토링 노션 "액션 아이템" DB에서 피드백 대상 태스크를 뽑는다.

    python scripts/notion_tasks.py            # 기본: 진행 중·완료 대기 중 마감일이 지난 것
    python scripts/notion_tasks.py --all-open # 열려 있는 것 전부 (예정 포함)
    python scripts/notion_tasks.py --json     # 기계용 출력

기본 필터는 **상태가 진행 중이거나 완료 대기이면서 마감일이 오늘 이전**인 태스크다.

두 상태는 성격이 다르다. `진행 중`은 아직 안 끝난 것이고, `완료 대기`는 **작업자 기준으로는 끝났고
멘토 확인만 남은 것**이다. 그래서 완료 대기에는 지연일을 매기지 않는다 — 며칠 머무는 것이 정상이며
(피드백·추가 과제가 붙으면 길어진다) 그것을 지연으로 세면 틀린 진단이 된다.

마감일이 없는 태스크는 기한 대조가 불가능하므로 빠진다. 여기에는 **매일 하는 상시 과제**(예: 문제
풀이)가 섞여 있는데, 수행 여부는 이 DB에 없으므로 애초에 이 입력으로는 판정할 수 없다.

자격증명은 .secrets/notion.json 의 mentoring 절에서 읽는다(gitignore 대상).
이 DB는 사용자 본인 워크스페이스가 아니라 멘토 워크스페이스에 있어, 위키의 기본 토큰으로는
접근되지 않는다. 멘토가 발급한 별도 토큰을 쓴다.
"""
import argparse
import datetime
import io
import json
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRETS = os.path.join(ROOT, ".secrets", "notion.json")

OPEN_STATES = ["진행 중", "완료 대기"]
PLANNED_STATE = "예정"


def load():
    with io.open(SECRETS, encoding="utf-8") as f:
        cfg = json.load(f)
    return cfg["mentoring"], cfg["notion_version"]


def query(db_id, token, version, body):
    req = urllib.request.Request(
        "https://api.notion.com/v1/databases/%s/query" % db_id,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + token,
            "Notion-Version": version,
            "Content-Type": "application/json",
        },
    )
    return json.load(urllib.request.urlopen(req))


def plain(prop):
    """노션 속성 하나를 사람이 읽는 값으로."""
    kind = prop["type"]
    if kind == "title":
        return "".join(x.get("plain_text", "") for x in prop["title"])
    if kind == "rich_text":
        return "".join(x.get("plain_text", "") for x in prop["rich_text"])
    if kind in ("select", "status"):
        return (prop[kind] or {}).get("name", "")
    if kind == "date":
        return (prop["date"] or {}).get("start", "")
    if kind == "formula":
        f = prop["formula"]
        return str(f.get(f["type"], ""))
    return ""


def main():
    # 윈도우에서 파일로 리다이렉트하면 기본 인코딩이 cp949라 한글이 깨진다.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser()
    parser.add_argument("--all-open", action="store_true",
                        help="예정 포함, 마감일 없는 것도 포함")
    parser.add_argument("--json", dest="as_json", action="store_true")
    args = parser.parse_args()

    cfg, version = load()
    today = datetime.date.today().isoformat()

    states = OPEN_STATES + ([PLANNED_STATE] if args.all_open else [])
    state_filter = {"or": [{"property": "상태", "select": {"equals": s}} for s in states]}

    if args.all_open:
        body = {"filter": state_filter}
    else:
        body = {"filter": {"and": [
            state_filter,
            {"property": "마감일", "date": {"before": today}},
        ]}}
    body["sorts"] = [{"property": "마감일", "direction": "ascending"}]

    rows = query(cfg["task_database_id"], cfg["api_token"], version, body)["results"]

    tasks = []
    for page in rows:
        props = page["properties"]
        values = {name: plain(p) for name, p in props.items()}
        due = values.get("마감일") or ""
        state = values.get("상태", "")
        # 완료 대기는 작업자 기준 완료 상태다. 지연으로 세지 않는다.
        overdue = None
        if due and state != "완료 대기":
            overdue = (datetime.date.fromisoformat(today)
                       - datetime.date.fromisoformat(due[:10])).days
        tasks.append({
            "할 일": values.get("할 일", ""),
            "상태": state,
            "유형": values.get("유형", ""),
            "마감일": due,
            "지연일": overdue,
        })

    if args.as_json:
        print(json.dumps({"기준일": today, "태스크": tasks}, ensure_ascii=False, indent=2))
        return

    print("기준일: %s   대상 %d건" % (today, len(tasks)))
    if not tasks:
        print("(조건에 맞는 태스크 없음)")
        return
    for t in tasks:
        if t["상태"] == "완료 대기":
            mark = "  (작업자 기준 완료, 확인 대기 — 지연 아님)"
        elif t["지연일"] is not None:
            mark = "  D+%d 지연" % t["지연일"]
        else:
            mark = ""
        print("- %-46s [%s] %s %s%s"
              % (t["할 일"][:46], t["상태"], t["유형"] or "-", t["마감일"] or "마감없음", mark))


if __name__ == "__main__":
    main()
