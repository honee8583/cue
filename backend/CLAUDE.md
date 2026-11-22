# cue backend

영화/공연 실시간 예매 서비스의 API 서버. 대용량 데이터 처리 학습용 개인 프로젝트.
(저장소 루트 `cue/`가 git 모노레포이고, 이 폴더는 그중 backend 프로젝트)

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

## 작업 절차 (반드시 따를 것)
1. 요청받은 기능을 구현한다.
2. 새 기능/변경된 동작에 대한 테스트를 `tests/test_<도메인>.py`에 추가한다.
3. `uv run pytest`로 전체 테스트를 실행한다 (DB가 꺼져 있으면 `docker compose up -d` 먼저).
4. 실패하면 원인을 찾아 코드를 고치고 3번부터 다시 한다. 모두 통과할 때까지 반복한다.
   - 테스트를 통과시키려고 테스트 자체를 지우거나 약하게 고치지 않는다. 테스트가 틀린 경우에만 고치고 그 이유를 설명한다.
5. **커밋하지 않는다.** 커밋/푸시는 사용자가 명시적으로 요청할 때만 한다.

## 커밋 규칙 (커밋을 요청받았을 때)

### 형식
```
<타입>(<범위>): <제목>
- <내용>
- <내용>
```
예시:
```
feat(movie): 영화 등록/목록 조회 API 추가
- POST /movies, GET /movies 구현
- 목록 조회에 limit/offset 페이지네이션 적용
```

- **타입**
  - `feat`: 새 기능
  - `fix`: 버그 수정
  - `refactor`: 동작 변화 없는 코드 구조 개선
  - `test`: 테스트 추가/수정
  - `docs`: 문서 (CLAUDE.md, README 등)
  - `chore`: 설정, 의존성, 빌드 등 기타
- **범위**: 변경된 도메인이나 영역 (예: `movie`, `booking`, `db`, `config`, `claude`)
- **제목**: 한국어로, 무엇을 했는지 간결하게. 끝에 마침표를 쓰지 않는다.
- **내용**: `- `로 시작하는 줄로 변경 사항을 나열한다.

### 단위
- 하나의 커밋에는 하나의 목적만 담는다. 성격이 다른 변경은 나눠서 커밋한다.
  - 예: 기능 구현 / 관련 없는 리팩터링 / 설정 변경 → 각각 별도 커밋
- 기능과 그 기능의 테스트는 같은 커밋에 넣는다.
- 각 커밋 시점에도 테스트가 통과하는 상태여야 한다.
- 커밋 전에 어떻게 나눌지 먼저 보여준다.

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

## 소통 규칙
- 사용자는 Python/FastAPI/PostgreSQL 입문자. 구현한 기능은 처음 배우는 사람 기준으로 한국어로 설명한다.
- 동시성(좌석 중복 예매 방지)과 대용량 데이터 성능을 우선 고려한다.
