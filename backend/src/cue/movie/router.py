from fastapi import APIRouter, Query

from cue.db import Session
from cue.movie import service
from cue.movie.schemas import MovieCreate, MovieRead

router = APIRouter(prefix="/movies", tags=["movies"])


@router.post("", response_model=MovieRead, status_code=201)
async def create_movie(data: MovieCreate, session: Session):
    return await service.create_movie(session, data)


@router.get("", response_model=list[MovieRead])
async def list_movies(
    session: Session,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    return await service.list_movies(session, limit, offset)
