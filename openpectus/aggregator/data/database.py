import json
from typing import Any, Optional

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import registry, Session, sessionmaker

reg = registry()
engine: Optional[Engine] = None
SessionLocal = None

def configure_db(database_file_path: str):
    global engine
    engine = create_engine(
        "sqlite://" + "/" + database_file_path,
        echo=False,
        connect_args={"check_same_thread": False},
        json_serializer=json_serialize,
        json_deserializer=json_deserialize)
    # json_serializer=lambda obj: json.dumps(obj, ensure_ascii=False))
    # engine.update_execution_options
    global SessionLocal
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_db():
    """ Create database tables for registered models. """
    assert engine is not None, "Database access is not configured. Use configure_db() "

    if len(reg.mappers) == 0:
        raise ValueError("No data classes have been mapped")

    reg.metadata.drop_all(engine)
    reg.metadata.create_all(engine)


def json_serialize(instance) -> str:
    return json.dumps(instance)


def json_deserialize(instance) -> dict[str, Any]:
    return json.loads(instance)
