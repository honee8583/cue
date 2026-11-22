# cue backend

영화/공연 실시간 예매 서비스의 API 서버. 대용량 데이터 처리 학습용 개인 프로젝트.
(저장소 루트 `cue/`가 git 모노레포이고, 이 폴더는 그중 backend 프로젝트. 공통 규칙은 `../CLAUDE.md`)

## 스택
- FastAPI + SQLAlchemy 2 (async) + asyncpg, Python 3.12, uv로 관리
- PostgreSQL 17 — 루트의 `../compose.yaml`로 실행

## 실행 방법

### 사전 준비
- Docker Desktop 실행 중
- uv 설치: `brew install uv`

### 1. 데이터베이스 (PostgreSQL 17)
```bash
docker compose up -d      # 상위 폴더의 compose.yaml을 자동으로 찾음. 호스트 포트 5433
docker compose down       # 종료 (데이터는 pgdata 볼륨에 유지)
```
- 접속 정보: `postgresql://cue:cue@localhost:5433/cue`
- 5432가 아닌 5433인 이유: 로컬의 다른 postgres 컨테이너가 5432를 사용 중

### 2. 서버 (FastAPI) — 이 폴더(backend/)에서 실행
```bash
uv sync                               # 최초 1회: Python 3.12 + 라이브러리 설치
uv run fastapi dev src/cue/main.py    # 개발 서버 (코드 수정 시 자동 재시작)
```
- API: http://localhost:8000
- API 문서: http://localhost:8000/docs
- 헬스체크: http://localhost:8000/health → `{"status":"ok"}`면 DB 연결까지 정상

### 3. 테스트
```bash
docker compose exec db createdb -U cue cue_test   # 최초 1회: 테스트 전용 DB 생성
uv run pytest                                     # 전체 테스트 실행
```
- 테스트는 개발 DB(`cue`)가 아닌 `cue_test`를 사용하며, 테스트마다 테이블을 비운다 (`tests/conftest.py`)

### 라이브러리 추가
```bash
uv add <패키지>          # 실행용
uv add --dev <패키지>    # 개발/테스트용 (예: pytest)
```

## 테스트 작성 위치
- 테스트는 `tests/test_<도메인>.py`에 추가한다.
- 테스트 전 DB가 꺼져 있으면 `docker compose up -d`를 먼저 실행한다.

## 아키텍처 (반드시 따를 것)

**계층형(Router → Service) + 도메인별 폴더 + 모놀리스.** 새 기능은 모두 이 구조로 만든다.

```
src/cue/
├── main.py          # 앱 생성, 도메인 router 등록(include_router), /health
├── db.py            # engine, Base(모든 모델의 부모), Session 의존성
└── <도메인>/         # 예: movie/, booking/ — 기능 단위 폴더
    ├── router.py    # HTTP만: URL, 요청 검증, 응답 모델. 로직 없이 service 호출만
    ├── service.py   # 비즈니스 로직 + DB 쿼리. FastAPI(Request, HTTPException 제외)에 의존하지 않음
    ├── models.py    # SQLAlchemy 테이블 (Base 상속)
    └── schemas.py   # Pydantic 요청/응답 형식 (<이름>Create, <이름>Read ...)
```

### 지켜야 할 점
- 호출 방향은 router → service → DB 한 방향. router에서 DB를 직접 쿼리하지 않는다.
- API 응답은 models가 아닌 schemas로 정의한다 (`response_model`).
- 다른 도메인의 기능이 필요하면 그 도메인의 service 함수를 호출한다. 다른 도메인의 router를 import하지 않는다.
- 새 도메인 추가 시 `main.py`에 `app.include_router(...)`로 등록한다.
- Repository 계층은 아직 두지 않는다. service의 쿼리가 복잡해져 분리가 필요해지면 해당 도메인에 `repository.py`를 추가한다.
- 테이블은 서버 시작 시 `Base.metadata.create_all`로 생성한다 (새 테이블만 생성, 컬럼 변경 불가). 기존 테이블 변경이 필요해지면 Alembic을 도입한다.
- 목록 조회 API는 반드시 `limit`/`offset` 등 페이지네이션을 둔다 (대용량 데이터 전제).
- 참고 예시: `movie/` 도메인

## 우선순위
- 동시성(좌석 중복 예매 방지)과 대용량 데이터 성능을 우선 고려한다.
