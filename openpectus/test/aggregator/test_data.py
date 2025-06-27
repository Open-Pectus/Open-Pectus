import os
import unittest
from datetime import datetime

import openpectus.aggregator.data.models as DMdl
import openpectus.aggregator.models as Mdl
import openpectus.aggregator.routers.dto as Dto
from alembic import command
from alembic.config import Config
from openpectus.aggregator.data import database
from openpectus.aggregator.data.repository import RecentRunRepository
from openpectus.aggregator.routers.serialization import deserialize, serialize
from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Mapped, mapped_column


def configure_db():
    database.configure_db("sqlite:///:memory:")


def create_db():
    # we can't use the migrations scripts, as in the migrate_db function, but must create the tables here on the fly,
    # due to the TestModel only being registered here, and thus not being migrated by the migration scripts
    assert database._engine is not None
    DMdl.DBModel.metadata.create_all(database._engine)


def migrate_db(alembic_cfg: Config):
    command.upgrade(alembic_cfg, 'head')


def get_modified_alembic_config():
    aggregator_prefix = os.path.join(os.path.dirname(__file__), "../../aggregator")
    alembic_cfg = Config(os.path.join(aggregator_prefix, "alembic.ini"))
    existing_script_location = alembic_cfg.get_main_option('script_location')
    assert existing_script_location is not None
    prefixed_script_location = os.path.join(aggregator_prefix, existing_script_location)
    alembic_cfg.set_main_option('script_location', prefixed_script_location)
    return alembic_cfg


def init_db():
    configure_db()
    create_db()


class DatabaseTest(unittest.TestCase):
    class TestModel(DMdl.DBModel):
        __tablename__ = "TestModel"

        name: Mapped[str] = mapped_column()

    def test_create_db(self):
        configure_db()

        stmt = select(DatabaseTest.TestModel)

        # select() raises when db does not exist
        with self.assertRaises(OperationalError):
            with database.create_scope():
                session = database.scoped_session()
                result = session.execute(stmt)
                self.assertIsNotNone(result)

        # create the tables
        create_db()

        # now execute works
        with database.create_scope():
            session = database.scoped_session()
            result = session.execute(stmt)
            self.assertIsNotNone(result)


    def test_no_missing_migration(self):
        db_filename = os.path.join(os.path.dirname(__file__), 'temp_db')
        configure_db()
        alembic_cfg = get_modified_alembic_config()
        alembic_cfg.set_main_option('sqlalchemy.url', "sqlite:///"+db_filename)

        migrate_db(alembic_cfg)
        # command.current(alembic_cfg, True) # useful for debugging
        command.check(alembic_cfg)
        os.remove(db_filename)

    def test_create_row_scoped(self):
        init_db()

        model = DatabaseTest.TestModel()
        model.name = "foo"

        self.assertEqual(model.id, None)

        # cannot access scope when there is no scope (contextmanager)
        with self.assertRaises(Exception):
            with database.scoped_session():
                pass

        with database.create_scope():
            session = database.scoped_session()
            session.add(model)
            session.commit()
            # refresh is required ...
            session.refresh(model)

        # ... to access updated property outside of the session
        self.assertEqual(model.id, 1)

        stmt = select(DatabaseTest.TestModel).where(DatabaseTest.TestModel.id == 1)
        with database.create_scope():
            session = database.scoped_session()
            result = session.execute(stmt)
            self.assertEqual(1, len(result.all()))

    def test_scope_session_identities(self):
        init_db()

        # same scope provides same session
        with database.create_scope():
            sess1 = database.scoped_session()
            id1 = id(sess1)
            sess2 = database.scoped_session()
            id2 = id(sess2)
            self.assertIs(sess1, sess2)
        self.assertEqual(id1, id2)

        # different scope provides different session
        with database.create_scope():
            sess3 = database.scoped_session()
            id3 = id(sess3)

        self.assertNotEqual(id1, id3)


class SerializationTest(unittest.TestCase):
    """ Test custom serialization for dto's used when serializing dto's as json database fields. """

    def test_json_serialization(self):
        data = Dto.ControlState(is_running=True, is_holding=False, is_paused=True)
        json_dict = serialize(data)
        self.assertEqual({"_type": "ControlState", 'is_running': True, 'is_holding': False, "is_paused": True}, json_dict)

    def test_json_deserialization(self):
        data = Dto.ControlState(is_running=True, is_holding=False, is_paused=True)
        json_dict = serialize(data)
        instance = deserialize(json_dict)
        self.assertIsNotNone(instance)
        self.assertIsInstance(instance, Dto.ControlState)
        self.assertEqual(instance.is_running, True)  # type: ignore

    # Enums not working. Not sure yet if they need to
    # def test_json_serialization_enum(self):
    #     data = D.UserRole.ADMIN
    #     json_dict = serialize(data)
    #     self.assertEqual({"_type": "UserRole"}, json_dict)

    def test_json_serialization_complex(self):
        complex_data = Dto.ProcessUnitState.InProgress(state=Dto.ProcessUnitStateEnum.IN_PROGRESS, progress_pct=87)
        json_str = serialize(complex_data)
        self.assertEqual({"_type": "ProcessUnitState.InProgress", "state": "in_progress", "progress_pct": 87}, json_str)

    def test_json_deserialization_complex(self):
        complex_data = Dto.ProcessUnitState.InProgress(state=Dto.ProcessUnitStateEnum.IN_PROGRESS, progress_pct=87)
        json_dict = serialize(complex_data)
        instance = deserialize(json_dict)
        self.assertIsNotNone(instance)
        self.assertIsInstance(instance, Dto.ProcessUnitState.InProgress)
        self.assertEqual(instance.progress_pct, 87)  # type: ignore


class RepositoryTest(unittest.TestCase):
    def test_can_insert(self):
        init_db()

        # at the data level we can insert any kind of junk
        entity = DMdl.RecentRun()
        entity.engine_id = "my_eng_id"
        entity.engine_computer_name = "my_computer_name"
        entity.uod_name = "my_uod_name"
        entity.uod_filename = "my_uod_filename.py"
        entity.uod_author_name = "my_uod_author_name"
        entity.uod_author_email = ""
        entity.run_id = 'a run id'
        entity.started_date = datetime.now()
        entity.completed_date = datetime.now()
        entity.engine_version = '0.0.1'
        entity.engine_hardware_str = 'hardware'
        entity.aggregator_version = '0.0.1'
        entity.aggregator_computer_name = 'aggregator computer name'

        entity_id = 0

        with database.create_scope():
            session = database.scoped_session()
            session.add(entity)
            session.commit()
            entity_id = entity.id

        self.assertEqual(entity_id, 1)

        with database.create_scope():
            session = database.scoped_session()
            repo = RecentRunRepository(session)

            created_entity = repo.get_by_run_id(entity.run_id)
            assert created_entity is not None
            self.assertEqual("my_computer_name", created_entity.engine_computer_name)
            self.assertEqual("my_uod_name", created_entity.uod_name)

    def test_can_update(self):
        init_db()

        entity = DMdl.RecentRun()
        entity.engine_id = "my_eng_id"
        entity.engine_computer_name = "my_computer_name"
        entity.uod_name = "my_uod_name"
        entity.uod_filename = "my_uod_filename.py"
        entity.uod_author_name = "my_uod_author_name"
        entity.uod_author_email = "my_uod_email"
        entity.run_id = 'a run id'
        entity.started_date = datetime.now()
        entity.completed_date = datetime.now()
        entity.engine_version = '0.0.1'
        entity.engine_hardware_str = 'hardware'
        entity.aggregator_version = '0.0.1'
        entity.aggregator_computer_name = 'aggregator computer name'

        entity_id = 0

        with database.create_scope():
            session = database.scoped_session()
            session.add(entity)
            session.commit()
            entity_id = entity.id

        self.assertEqual(1, entity_id)

        with database.create_scope():
            session = database.scoped_session()
            repo = RecentRunRepository(session)

            created_entity = repo.get_by_run_id(entity.run_id)
            assert created_entity is not None
            created_entity.engine_computer_name = "updated_computer_name"
            session.commit()

        with database.create_scope():
            session = database.scoped_session()
            repo = RecentRunRepository(session)

            updated_entity = repo.get_by_run_id(entity.run_id)
            assert updated_entity is not None
            self.assertEqual("updated_computer_name", updated_entity.engine_computer_name)
            self.assertEqual("my_uod_name", updated_entity.uod_name)

    def test_can_find(self):
        init_db()

        entity = DMdl.RecentRun()
        entity.engine_id = "my_eng_id"
        entity.run_id = 'a run id'
        entity.engine_computer_name = "my_computer_name"
        entity.uod_name = "my_uod_name"
        entity.uod_filename = "my_uod_filename.py"
        entity.uod_author_name = "my_uod_author_name"
        entity.uod_author_email = "my_uod_email"
        entity.started_date = datetime.now()
        entity.completed_date = datetime.now()
        entity.contributors = list([Mdl.Contributor(name='foo', id='foo'), Mdl.Contributor(name='baz', id='baz')])
        entity.engine_version = '0.0.1'
        entity.engine_hardware_str = 'hardware'
        entity.aggregator_version = '0.0.1'
        entity.aggregator_computer_name = 'aggregator computer name'

        with database.create_scope():
            session = database.scoped_session()
            session.add(entity)
            session.commit()

        with database.create_scope():
            session = database.scoped_session()
            repo = RecentRunRepository(session)
            created_entity = repo.get_by_run_id("a run id")
            self.assertIsNotNone(created_entity)
            self.assertIsInstance(created_entity, DMdl.RecentRun)

    def test_json(self):
        init_db()

        entity = DMdl.RecentRun()
        entity.engine_id = "my_eng_id"
        entity.engine_computer_name = "my_computer_name"
        entity.uod_name = "my_uod_name"
        entity.uod_filename = "my_uod_filename.py"
        entity.uod_author_name = "my_uod_author_name"
        entity.uod_author_email = "my_uod_email"
        entity.contributors = list([Mdl.Contributor(name='foo', id='foo'), Mdl.Contributor(name='bar', id='bar')])
        entity.run_id = 'a run id'
        entity.started_date = datetime.now()
        entity.completed_date = datetime.now()
        entity.engine_version = '0.0.1'
        entity.engine_hardware_str = 'hardware'
        entity.aggregator_version = '0.0.1'
        entity.aggregator_computer_name = 'aggregator computer name'

        entity_id = 0
        with database.create_scope():
            session = database.scoped_session()
            session.add(entity)
            session.commit()
            entity_id = entity.id

        self.assertEqual(entity_id, 1)

        with database.create_scope():
            session = database.scoped_session()
            repo = RecentRunRepository(session)

            created_entity = repo.get_by_run_id(entity.run_id)
            assert created_entity is not None
            self.assertEqual([{'id': 'foo', 'name': 'foo'}, {'id': 'bar', 'name': 'bar'}], created_entity.contributors)

            # Must reassign with new instance for change to be persisted
            contributors = list(created_entity.contributors)
            contributors.append(Mdl.Contributor(name='baz', id='baz'))
            created_entity.contributors = contributors
            session.commit()

        with database.create_scope():
            session = database.scoped_session()
            repo = RecentRunRepository(session)
            updated_entity = repo.get_by_run_id(entity.run_id)
            assert updated_entity is not None
            self.assertEqual([{'id': 'foo', 'name': 'foo'}, {'id': 'bar', 'name': 'bar'}, {'id': 'baz', 'name': 'baz'}], updated_entity.contributors)

    def test_nested_json(self):
        init_db()

        run_id = 'fdsa'

        plot_configuration = Mdl.PlotConfiguration.empty()
        plot_configuration.process_value_names_to_annotate = ['x']

        recent_run_plot_configuration = DMdl.RecentRunPlotConfiguration()
        recent_run_plot_configuration.run_id = run_id
        recent_run_plot_configuration.plot_configuration = plot_configuration

        with database.create_scope():
            session = database.scoped_session()
            session.add(recent_run_plot_configuration)
            session.commit()

            repo = RecentRunRepository(session)
            from_db = repo.get_plot_configuration_by_run_id(run_id)
            dto: Dto.PlotConfiguration = Dto.PlotConfiguration.model_validate(from_db)
            self.assertIsInstance(dto, Dto.PlotConfiguration)
            self.assertEqual(dto.process_value_names_to_annotate, plot_configuration.process_value_names_to_annotate)


if __name__ == "__main__":
    unittest.main()
