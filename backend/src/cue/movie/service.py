from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cue.movie.models import Movie
from cue.movie.schemas import MovieCreate


async def create_movie(session: AsyncSession, data: MovieCreate) -> Movie:
    movie = Movie(title=data.title)
    session.add(movie)
    await session.commit()
    return movie


async def list_movies(session: AsyncSession, limit: int, offset: int) -> list[Movie]:
    result = await session.scalars(select(Movie).order_by(Movie.id).limit(limit).offset(offset))
    return list(result)
