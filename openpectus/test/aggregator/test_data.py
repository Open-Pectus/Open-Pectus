
import unittest

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import select
from sqlalchemy.exc import OperationalError

from openpectus.aggregator.data import database
from openpectus.aggregator.data.models import DBModel, BatchJobData
from openpectus.aggregator.data.repository import BatchJobDataRepository

import openpectus.aggregator.routers.dto as D
from openpectus.aggregator.routers.serialization import deserialize, serialize


def init_db():
    database.configure_db(":memory:")
    database.create_db()


class DatabaseTest(unittest.TestCase):
    class TestModel(DBModel):
        __tablename__ = "TestModel"
        name: Mapped[str] = mapped_column()

    def test_create_db(self):
        database.configure_db(":memory:")

        stmt = select(DatabaseTest.TestModel)

        # select() raises when db does not exist
        with self.assertRaises(OperationalError):
            with database.SessionLocal() as session:
                _ = session.execute(stmt)

        # create the tables
        database.create_db()

        with database.SessionLocal() as session:
            # now it works
            result = session.execute(stmt)
            # self.assertEqual(0, len(result))
            self.assertIsNotNone(result)

    def test_create_row(self):
        init_db()

        model = DatabaseTest.TestModel()
        model.name = "foo"

        self.assertEqual(model.id, None)

        with database.SessionLocal() as session:
            # now it works
            session.add(model)
            session.commit()
            # refresh is required ...
            session.refresh(model)

        # ... to access updated property outside of the session
        self.assertEqual(model.id, 1)

        stmt = select(DatabaseTest.TestModel).where(DatabaseTest.TestModel.id == 1)
        with database.SessionLocal() as session:
            result = session.execute(stmt)
            self.assertEqual(1, len(result.all()))


class SerializationTest(unittest.TestCase):
    """ Test custom serialization for dto's used when serializing dto's as json database fields. """

    def test_json_serialization(self):
        data = D.ControlState(is_running=True, is_holding=False, is_paused=True)
        json_dict = serialize(data)
        self.assertEqual({"_type": "ControlState", 'is_running': True, 'is_holding': False, "is_paused": True}, json_dict)

    def test_json_deserialization(self):
        data = D.ControlState(is_running=True, is_holding=False, is_paused=True)
        json_dict = serialize(data)
        instance = deserialize(json_dict)
        self.assertIsNotNone(instance)
        self.assertIsInstance(instance, D.ControlState)
        self.assertEqual(instance.is_running, True)  # type: ignore

    # Enums not working. Not sure yet if they need to
    # def test_json_serialization_enum(self):
    #     data = D.UserRole.ADMIN
    #     json_dict = serialize(data)
    #     self.assertEqual({"_type": "UserRole"}, json_dict)

    def test_json_serialization_complex(self):
        complex_data = D.ProcessUnitState.InProgress(state=D.ProcessUnitStateEnum.IN_PROGRESS, progress_pct=87)
        json_str = serialize(complex_data)
        self.assertEqual({"_type": "ProcessUnitState.InProgress", "state": "in_progress", "progress_pct": 87}, json_str)

    def test_json_deserialization_complex(self):
        complex_data = D.ProcessUnitState.InProgress(state=D.ProcessUnitStateEnum.IN_PROGRESS, progress_pct=87)
        json_dict = serialize(complex_data)
        instance = deserialize(json_dict)
        self.assertIsNotNone(instance)
        self.assertIsInstance(instance, D.ProcessUnitState.InProgress)
        self.assertEqual(instance.progress_pct, 87)  # type: ignore


class RepositoryTest(unittest.TestCase):
    def test_can_insert(self):
        init_db()

        # at the data level we can insert any kind of junk
        entity = BatchJobData()
        entity.engine_id = "my_eng_id"
        entity.computer_name = "my_computer_name"
        entity.uod_name = "my_uod_name"

        entity_id = 0

        with database.SessionLocal() as s:
            s.add(entity)
            s.commit()
            entity_id = entity.id

        self.assertEqual(entity_id, 1)

        with database.SessionLocal() as s:
            repo = BatchJobDataRepository(s)

            created_entity = repo.get_by_id(entity_id)
            assert created_entity is not None
            self.assertEqual("my_computer_name", created_entity.computer_name)
            self.assertEqual("my_uod_name", created_entity.uod_name)

    def test_can_update(self):
        init_db()

        entity = BatchJobData()
        entity.engine_id = "my_eng_id"
        entity.computer_name = "my_computer_name"
        entity.uod_name = "my_uod_name"

        entity_id = 0

        with database.SessionLocal() as s:
            s.add(entity)
            s.commit()
            entity_id = entity.id

        self.assertEqual(1, entity.id)

        with database.SessionLocal() as s:
            repo = BatchJobDataRepository(s)

            created_entity = repo.get_by_id(entity_id)
            assert created_entity is not None
            created_entity.computer_name = "updated_computer_name"
            s.commit()

        with database.SessionLocal() as s:
            repo = BatchJobDataRepository(s)

            updated_entity = repo.get_by_id(entity_id)
            assert updated_entity is not None
            self.assertEqual("updated_computer_name", updated_entity.computer_name)
            self.assertEqual("my_uod_name", updated_entity.uod_name)

    def test_can_find(self):
        init_db()

        entity = BatchJobData()
        entity.engine_id = "my_eng_id"
        entity.computer_name = "my_computer_name"
        entity.uod_name = "my_uod_name"
        entity.contributors = ['foo', 'bar']

        with database.SessionLocal() as s:
            s.add(entity)
            s.commit()

        with database.SessionLocal() as s:
            repo = BatchJobDataRepository(s)
            created_entity = repo.get_by_engine_id("my_eng_id")
            self.assertIsNotNone(created_entity)
            self.assertIsInstance(created_entity, BatchJobData)

    def test_json(self):
        init_db()

        entity = BatchJobData()
        entity.engine_id = "my_eng_id"
        entity.computer_name = "my_computer_name"
        entity.uod_name = "my_uod_name"
        entity.contributors = ['foo', 'bar']

        entity_id = 0

        with database.SessionLocal() as s:
            s.add(entity)
            s.commit()
            entity_id = entity.id

        self.assertEqual(1, entity.id)

        with database.SessionLocal() as s:
            repo = BatchJobDataRepository(s)

            created_entity = repo.get_by_id(entity_id)
            assert created_entity is not None
            self.assertEqual(['foo', 'bar'], created_entity.contributors)

            # Must reassign with new instance for change to be persisted
            contributors = list(created_entity.contributors)
            contributors.append('baz')
            created_entity.contributors = contributors
            s.commit()

        with database.SessionLocal() as s:
            repo = BatchJobDataRepository(s)
            updated_entity = repo.get_by_id(entity_id)
            assert updated_entity is not None
            self.assertEqual(['foo', 'bar', 'baz'], updated_entity.contributors)


if __name__ == "__main__":
    unittest.main()
