
from peewee import (
    Model,
    IntegerField,
    TextField,
)

import openpectus.aggregator.data.database as database


class DBModel(Model):
    id = IntegerField(primary_key=True)

    class Meta:
        database = database.db


class Foo(DBModel):
    name = TextField()


database.register_model(Foo)
