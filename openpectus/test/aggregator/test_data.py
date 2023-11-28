
import unittest
from peewee import TextField, OperationalError

from openpectus.aggregator.data import database, DBModel


class DatabaseTest(unittest.TestCase):
    class TestModel(DBModel):
        name = TextField()

    def test_create_db(self):
        database.configure_db(":memory:")        
        database.register_model(DatabaseTest.TestModel)
        database.bind_models()

        with self.assertRaises(OperationalError):
            result = DatabaseTest.TestModel.select()
            self.assertEqual(0, len(result))

        database.create_db()

        result = DatabaseTest.TestModel.select()
        self.assertEqual(0, len(result))

    def test_create_row(self):
        database.configure_db(":memory:")
        database.register_model(DatabaseTest.TestModel)
        database.bind_models()
        database.create_db()

        model = DatabaseTest.TestModel()
        model.name = "foo"  # type: ignore

        self.assertEqual(model.id, None)
        model.save()
        self.assertEqual(model.id, 1)

        result = DatabaseTest.TestModel.select()
        self.assertEqual(1, len(result))

        persisted_model = result[0]
        assert isinstance(persisted_model, DatabaseTest.TestModel)
        self.assertEqual(persisted_model.id, 1)
        self.assertEqual(persisted_model.name, "foo")


if __name__ == "__main__":
    unittest.main()
