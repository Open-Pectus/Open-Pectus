import json
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any

from pydantic_core import to_jsonable_python
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.types import ASGIApp

_engine: Engine | None = None
_sessionmaker: sessionmaker[Session] | None = None
_session_ctx: ContextVar[Session | None] = ContextVar("_session", default=None)


@contextmanager
def create_scope():
    """ Used from middleware to create a request context (scope), in which scoped_session() will work.

    Can also be used in non-request contexts to enable scoped_session() there.

    Also used in tests to provide a scope
    """
    if _sessionmaker is None:
        raise DatabaseNotConfiguredError()
    session = _sessionmaker()
    token = _session_ctx.set(session)
    try:
        yield
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
        _session_ctx.reset(token)


def scoped_session() -> Session:
    if _engine is None:
        raise DatabaseNotConfiguredError()
    session = _session_ctx.get()
    if session is None:
        raise SessionMissingError()
    return session


def configure_db(database_url: str):
    global _engine, _sessionmaker
    _engine = create_engine(
        database_url,
        echo=False,
        connect_args={"check_same_thread": False},
        json_serializer=json_serialize,
        json_deserializer=json_deserialize)
    _sessionmaker = sessionmaker(autocommit=False, autoflush=False, bind=_engine)



def json_serialize(instance) -> str:
    return json.dumps(instance, default=to_jsonable_python)


def json_deserialize(instance) -> dict[str, Any]:
    return json.loads(instance)


class DBSessionMiddleware(BaseHTTPMiddleware):
    """ FastAPI middleware that makes request scoped database sessions available """
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        if _sessionmaker is None:
            raise DatabaseNotConfiguredError()
        else:
            with create_scope():
                response = await call_next(request)
            return response


class DatabaseNotConfiguredError(Exception):
    """Excetion raised when trying to access the database before it is configured. """
    def __init__(self, *args: object) -> None:
        super().__init__("Database has not been configured, i.e. configure_db() was not called.")


class SessionMissingError(Exception):
    """Excetion raised when trying to access a database session without a scope."""
    def __init__(self):
        super().__init__("No session is available in the current scope.")
