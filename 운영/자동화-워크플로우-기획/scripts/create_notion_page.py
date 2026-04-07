#!/usr/bin/env python3
import json
import urllib.request
import urllib.error
import sys

import os
home = os.path.expanduser("~")
with open(f"{home}/.config/notion/api_key") as f:
    api_key = f.read().strip()

skill_path = "/home/hongjimin/.openclaw/workspace/skills/운영/자동화-워크플로우-기획/SKILL.md"
evals_path = "/home/hongjimin/.openclaw/workspace/skills/운영/자동화-워크플로우-기획/evals/evals.json"

with open(skill_path) as f:
    skill_content = f.read()
with open(evals_path) as f:
    evals_content = f.read()

# Notion code blocks have a 2000 char limit, need to chunk
def chunk_text(text, size=1990):
    return [text[i:i+size] for i in range(0, len(text), size)]

skill_chunks = chunk_text(skill_content)
evals_chunks = chunk_text(evals_content)

def make_code_blocks(chunks, language):
    blocks = []
    for chunk in chunks:
        blocks.append({
            "object": "block",
            "type": "code",
            "code": {
                "rich_text": [{"text": {"content": chunk}}],
                "language": language
            }
        })
    return blocks

children = [
    {
        "object": "block",
        "type": "heading_1",
        "heading_1": {
            "rich_text": [{"text": {"content": "스킬 개요"}}],
            "color": "yellow_background"
        }
    },
    {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{"text": {"content": "업무: 자동화 워크플로우 기획"}}]
        }
    },
    {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{"text": {"content": "카테고리: 운영"}}]
        }
    },
    {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{"text": {"content": "트리거 상황: 반복 업무를 Make/n8n 등으로 자동화하려 할 때, 수동 작업을 줄이고 싶다는 말이 나올 때"}}]
        }
    },
    {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{"text": {"content": "절감 효과: 자동화 설계 시간 30~60분 단축, 구현 오류율 감소"}}]
        }
    },
    {
        "object": "block",
        "type": "heading_1",
        "heading_1": {
            "rich_text": [{"text": {"content": "SKILL.md"}}],
            "color": "yellow_background"
        }
    }
]

children.extend(make_code_blocks(skill_chunks, "markdown"))

children.append({
    "object": "block",
    "type": "heading_1",
    "heading_1": {
        "rich_text": [{"text": {"content": "테스트 케이스"}}],
        "color": "yellow_background"
    }
})

children.extend(make_code_blocks(evals_chunks, "json"))

children.append({
    "object": "block",
    "type": "heading_1",
    "heading_1": {
        "rich_text": [{"text": {"content": "저장 경로 및 활용법"}}],
        "color": "yellow_background"
    }
})
children.append({
    "object": "block",
    "type": "paragraph",
    "paragraph": {
        "rich_text": [{"text": {"content": "로컬 경로: workspace/skills/운영/자동화-워크플로우-기획/SKILL.md"}}]
    }
})
children.append({
    "object": "block",
    "type": "paragraph",
    "paragraph": {
        "rich_text": [{"text": {"content": "GitHub: https://github.com/jmhong-afk/teamjcurve-skills"}}]
    }
})
children.append({
    "object": "block",
    "type": "paragraph",
    "paragraph": {
        "rich_text": [{"text": {"content": "Claude Code 사용법: @workspace/skills/운영/자동화-워크플로우-기획/SKILL.md 참조 후 자동화하고 싶은 업무를 자연어로 설명"}}]
    }
})

payload = {
    "parent": {"page_id": "2fd9c7b3-864f-80b0-b39d-fe6454fa3c2a"},
    "properties": {
        "title": {"title": [{"text": {"content": "20260406_자동화-워크플로우-기획_SKILL"}}]}
    },
    "children": children
}

data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(
    "https://api.notion.com/v1/pages",
    data=data,
    headers={
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    },
    method="POST"
)

try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
        print("SUCCESS")
        print("PAGE_ID:", result.get("id"))
        print("URL:", result.get("url"))
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print("ERROR:", e.code, body)
    sys.exit(1)
