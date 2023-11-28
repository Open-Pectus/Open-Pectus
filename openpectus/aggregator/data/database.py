
from peewee import SqliteDatabase


db = SqliteDatabase(None)


def configure_db(database_file_path: str):
    """ Configure the database file. Must be invoked before any queries are performed.

    Supports the special path ':memory:' to use an in-memory database.
    """
    # all available pragmas: https://sqlite.org/pragma.html
    pragmas = {
        'journal_mode': 'wal',
        'cache_size': 10000,  # 10000 pages, or ~40MB
        'foreign_keys': 1,  # Enforce foreign-key constraints
    }
    db.init(database=database_file_path, pragmas=pragmas)


registered_models: set[type] = set()


def register_model(cls: type):
    registered_models.add(cls)


def bind_models():
    db.bind(registered_models)


def create_db():
    db.create_tables(registered_models)
