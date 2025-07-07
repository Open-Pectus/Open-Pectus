from typing import Any
import random
import string

from openpectus.engine.uod_builder_api import (
    UnitOperationDefinitionBase, UodBuilder, tags,
    HardwareLayerBase, Register, RegisterDirection
)
from openpectus.lang.exec.units import QUANTITY_UNIT_MAP


def random_string(n: int) -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=n))

def generate_tag_value(value_type) -> str | float | int | None:
        if value_type is float:
            return random.random()*10**(random.randrange(-4, 4))
        elif value_type is str:
            return ''.join(random.choices(string.ascii_uppercase + string.digits, k=random.randint(5,30)))
        elif value_type is int:
            return random.randint(int(-1e6), int(1e6))

def generate_tags(n_tags):
    tag_names = [random_string(n) for n in [random.randint(5,20) for n in range(n_tags)]]
    possible_units = [unit for units in QUANTITY_UNIT_MAP.values() for unit in units]

    tags = dict()
    for tag_name in tag_names:
        value_type = random.choice([float, str, int, None])
        value = None
        value_unit = None

        # Value
        value = generate_tag_value(value_type)

        # Value unit
        if value_type in [float, int]:
            value_unit = random.choice(possible_units)

        tags[tag_name] = (tag_name, value_type, value, value_unit)

    return tags

random.seed(a=0)
tags_dict = generate_tags(n_tags=1000)

def create() -> UnitOperationDefinitionBase:
    builder = UodBuilder()

    (
    builder
    .with_instrument("HeavyUod")
    .with_author("Demo Author", "demo@openpectus.org")
    .with_filename(__file__)
    .with_hardware(DemoHardware())
    .with_location("Demo location")
    )

    for tag_name, value_type, value, value_unit in tags_dict.values():
        builder.with_hardware_register(
            tag_name,
            RegisterDirection.Read
        )
        builder.with_tag(
            tags.Tag(
                tag_name,
                value=value,
                unit=value_unit
            )
        )
        builder.with_process_value(tag_name=tag_name)

    return builder.build()


class DemoHardware(HardwareLayerBase):

    def read(self, r: Register) -> Any:
        _, value_type, _, _ = tags_dict[r.name]
        value = generate_tag_value(value_type)
        return value

    def write(self, value: Any, r: Register):
        pass
