import os

from dotenv import load_dotenv
load_dotenv()
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlmodel.ext.asyncio.session import AsyncSession
from supabase import AsyncClient, acreate_client

from app.models.user import User, Profile
from app.models.app import App
from app.models.sandbox import Sandbox
from app.models.comment import Comment
# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


engine = create_async_engine(os.environ.get("SUPABASE_DB_STRING"), poolclass=NullPool, connect_args={"statement_cache_size": 0})

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_supabase_client() -> AsyncClient:
    client = await acreate_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
    return client


async def get_db_session():
    async with async_session() as session:
        yield session


def init_db():
    # TODO: prepare initial data here
	pass
