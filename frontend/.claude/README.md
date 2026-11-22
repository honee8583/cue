# .claude 폴더 안내

Claude Code는 **이 프로젝트 폴더에서 `claude`를 실행했을 때** 아래 파일들을 읽는다.
(이 README.md 자체는 Claude Code가 읽지 않는다. 사람용 안내문.)
각 폴더의 `.gitkeep`은 빈 폴더를 git에 올리기 위한 표시 파일이며, 실제 파일을 넣으면 지워도 된다.

| 경로 | 역할 | 자동으로 읽히나? |
|---|---|---|
| `settings.json` | 권한, hooks 등록, 환경변수 (git 공유) | O |
| `settings.local.json` | 나만 쓰는 설정 (git 제외) | O |
| `rules/*.md` | CLAUDE.md를 주제별로 쪼갠 규칙 | O (항상, 또는 `paths` 지정 시 해당 파일 작업 때) |
| `commands/*.md` | 직접 만드는 슬래시 명령 (`/파일명`) | 호출할 때 |
| `agents/*.md` | 서브 에이전트 (특정 역할을 맡는 별도 Claude) | 필요할 때 |
| `skills/<이름>/SKILL.md` | 상황에 맞으면 Claude가 스스로 꺼내 쓰는 작업 매뉴얼 | 필요할 때 |
| `output-styles/*.md` | 답변 말투/형식 (`/output-style`로 선택) | 선택할 때 |
| `hooks/` | hook이 실행할 스크립트 보관용 (관례) | X — `settings.json`에 등록해야 실행됨 |

> 주의: `rules/`, `commands/`, `agents/` 안의 `.md` 파일은 전부 실제 규칙/명령/에이전트로 읽힌다. 메모용 md를 넣지 말 것.

---

## rules/ — 주제별 규칙
```markdown
---
paths:
  - "src/components/**"
---
# 컴포넌트 규칙
- 컴포넌트 하나는 한 파일에 둔다.
```
`paths`를 생략하면 항상 적용된다.

## commands/ — 슬래시 명령
파일 `commands/new-page.md` → `/new-page movie-list` 으로 실행.
```markdown
---
description: 새 페이지 생성
argument-hint: <페이지 이름>
---
$ARGUMENTS 페이지를 만들어줘.
```

## agents/ — 서브 에이전트
```markdown
---
name: db-reviewer
description: SQL/쿼리 성능과 동시성 문제를 리뷰할 때 사용
tools: Read, Grep, Glob
model: sonnet
---
너는 PostgreSQL 성능 리뷰어다. 인덱스 누락, N+1 쿼리, 락 문제를 찾아라.
```

## skills/ — 스킬
폴더 하나가 스킬 하나: `skills/<이름>/SKILL.md` (+ 필요하면 스크립트, 참고 문서를 같은 폴더에)
```markdown
---
name: load-test
description: 대량 더미 데이터 생성이나 부하 테스트를 할 때 사용
---
1. ...
2. ...
```

## output-styles/ — 답변 스타일
```markdown
---
name: 튜터
description: 입문자에게 개념부터 설명
---
모든 답변은 개념 설명 → 코드 → 요약 순서로 한다.
```

## hooks — 자동 실행
특정 시점(파일 수정 후, 명령 실행 전 등)에 스크립트를 자동 실행한다.
1. 스크립트를 `hooks/`에 넣는다 (예: `hooks/format.sh`, `chmod +x` 필요)
2. `settings.json`에 등록한다:
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/format.sh" }
        ]
      }
    ]
  }
}
```
주요 시점: `PreToolUse`(도구 실행 전, 막을 수 있음), `PostToolUse`(도구 실행 후), `UserPromptSubmit`(질문 보낼 때), `Stop`(답변 끝날 때), `SessionStart`(시작 시).
스크립트는 표준입력(stdin)으로 JSON 형태의 상황 정보를 받는다.

---

## 이 폴더 밖에 있는 Claude Code 파일
- `../CLAUDE.md` — 프로젝트 설명서 (항상 읽힘)
- `../CLAUDE.local.md` — 나만 쓰는 메모 (필요 시 생성, git 제외 권장)
- `../.mcp.json` — MCP 서버(외부 도구 연결) 설정 (필요 시 생성)
