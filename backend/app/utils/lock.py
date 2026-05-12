from contextlib import asynccontextmanager
from enum import Enum
from sqlmodel import text
from app.core.db import async_session


class LockPrefix(Enum):
    """
    A namespace for different types of locks, range from 10 to 99
    """

    REBUILD_APP = 10


def make_lock_id(prefix: LockPrefix, id: int) -> int:
    if id > 999999999:
        raise ValueError(f"id cannot be greater than 999999999: {id}")
    return int(f"{prefix.value}{id}")


@asynccontextmanager
async def with_pg_advisory_lock_async(id: int):
    async with async_session() as session:
        rows = await session.exec(text("SELECT pg_try_advisory_xact_lock(:id)").bindparams(id=id))
        row = rows.first()
        lock_acquired = row[0] if row else False

        if not lock_acquired:
            raise Exception(f"failed to acquire lock: {id}")

        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
