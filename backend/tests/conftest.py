import os

# 개발용 DB(cue)를 더럽히지 않도록 테스트 전용 DB(cue_test)를 쓴다. cue 모듈 import 전에 설정해야 함.
os.environ["DATABASE_URL"] = "postgresql+asyncpg://cue:cue@localhost:5433/cue_test"

import pytest
from fastapi.testclient import TestClient

from cue.db import Base, engine
from cue.main import app


async def _clear_tables():
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest.fixture
def client():
    with TestClient(app) as c:
        c.portal.call(_clear_tables)
        yield c
        # TestClient는 테스트마다 새 이벤트 루프를 쓰므로, 이전 루프에 묶인 DB 연결을 닫아둔다
        c.portal.call(engine.dispose)
