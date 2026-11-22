# cue

영화/공연 실시간 예매 서비스

| 폴더 | 내용 |
|---|---|
| `backend/` | FastAPI + PostgreSQL |
| `frontend/` | (예정) |

## 실행

```bash
docker compose up -d                              # PostgreSQL 실행 (포트 5433)
cd backend && uv run fastapi dev src/cue/main.py  # API 서버 실행
```

- API 문서: http://localhost:8000/docs
- 헬스체크: http://localhost:8000/health
