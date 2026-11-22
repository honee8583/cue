from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from cue.db import Base, Session, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ponytail: 서버 시작 시 없는 테이블만 생성. 기존 테이블 컬럼 변경은 못 함 → 필요해지면 Alembic 도입
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="cue", lifespan=lifespan)


@app.get("/health")
async def health(session: Session):
    await session.execute(text("SELECT 1"))
    return {"status": "ok"}
