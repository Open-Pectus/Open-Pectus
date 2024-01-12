import json
import logging
from typing import Any
from contextlib import contextmanager
from contextvars import ContextVar
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import registry, Session, sessionmaker

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

reg = registry()
_engine: Engine | None = None
_sessionmaker: sessionmaker[Session] | None = None
_session_ctx: ContextVar[Session | None] = ContextVar("_session", default=None)


@contextmanager
def create_scope():
    """ Used from middleware to create a request context (scope), in which scoped_session() will work.

    Also used in tests to provide a scope
    """
    if _sessionmaker is None:
        raise Exception("_sessionmaker has not been set. Will not be able to provide scoped database sessions")
    session = _sessionmaker()
    token = _session_ctx.set(session)
    try:
        yield
    except Exception:
        session.rollback()
    finally:
        session.close()
        _session_ctx.reset(token)


def scoped_session() -> Session:
    session = _session_ctx.get()
    assert session is not None, "Scoped session unavailable. Are you using this from a FastAPI request context?"
    return session


def configure_db(database_file_path: str):
    global _engine, _sessionmaker
    _engine = create_engine(
        "sqlite://" + "/" + database_file_path,
        echo=False,
        connect_args={"check_same_thread": False},
        json_serializer=json_serialize,
        json_deserializer=json_deserialize)
    _sessionmaker = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def create_db():
    """ Create database tables for registered models. """
    assert _engine is not None, "Database access is not configured. Use configure_db() "

    if len(reg.mappers) == 0:
        raise ValueError("No data classes have been mapped")

    reg.metadata.drop_all(_engine)
    reg.metadata.create_all(_engine)


def json_serialize(instance) -> str:
    return json.dumps(instance)


def json_deserialize(instance) -> dict[str, Any]:
    return json.loads(instance)


class DBSessionMiddleware(BaseHTTPMiddleware):
    """ FastAPI middleware that makes request scoped database sessions available """
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        logger.info("DBSessionMiddleware init complete")

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        if _sessionmaker is None:
            logger.error("_sessionmaker has not been set. Will not be able to provide scoped database sessions")
            response = await call_next(request)
        else:
            with create_scope():
                response = await call_next(request)
        return response


