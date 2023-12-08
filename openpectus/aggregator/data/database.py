
import json
from typing import Any, Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import registry, Session

reg = registry()
engine: Optional[Engine] = None


def configure_db(database_file_path: str):
    global engine
    engine = create_engine(
        "sqlite://" + "/" + database_file_path,
        echo=True,
        json_serializer=json_serialize,
        json_deserializer=json_deserialize)
    # json_serializer=lambda obj: json.dumps(obj, ensure_ascii=False))
    # engine.update_execution_options


def create_db():
    """ Create database tables for registered models. """
    assert engine is not None, "Database access is not configured. Use configure_db() "

    if len(reg.mappers) == 0:
        raise ValueError("No data classes have been mapped")

    reg.metadata.create_all(engine)


def get_session() -> Session:
    session = Session(engine)
    return session


def json_serialize(instance) -> str:
    return json.dumps(instance)


def json_deserialize(instance) -> dict[str, Any]:
    return json.loads(instance)
