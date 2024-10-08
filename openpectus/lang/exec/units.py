from __future__ import annotations
import logging

import pint
from pint import UnitRegistry, Quantity


ureg = UnitRegistry(cache_folder="./pint-cache")
Q_ = Quantity
logger = logging.getLogger(__name__)

# https://en.wikipedia.org/wiki/International_System_of_Units
# defines all the units we accept, each with their quantity name (similar to pint dimensionality).
QUANTITY_UNIT_MAP = {
    'time': ['s', 'min', 'h', 'ms'],            # SI quantities
    'length': ['m', 'cm'],
    'mass': ['kg', 'g'],
    'temperature': ['degC', 'degF', 'degK'],
    'amount_of_substance': ['mol'],
    'volume': ['L', 'mL'],                      # Derived quantities
    'flow': ['L/h', 'L/min', 'L/d'],
    'frequency': ['Hz', 'kHz'],
    'pressure': ['Pa', 'bar', 'pascal'],        # Note: pint prefers pascal over Pa so we define both.
    'mass flow rate': ['kg/h', 'g/s', 'g/min', 'g/h'],
    'electrical conductance': ['mS/cm'],
    'percentage': ['%'],                        # Custom quantity but supported by pint
    'column volume': ['CV'],                    # Custom quantity
    'absorbance': ['AU'],
}
""" Map quantity names to unit names. """

QUANTITY_PINT_MAP: dict[str, str] = {
    'time': '[time]',
    'length': '[length]',
    'mass': '[mass]',
    'flow': '[length] ** 3 / [time]',
    'volume': '[length] ** 3',
    'frequency': '1 / [time]',
    'temperature': '[temperature]',
    'amount_of_substance': '[substance]',
    'pressure': '[mass] / [length] / [time] ** 2',
    'mass flow rate': '[mass] / [time]',
    'electrical conductance': '[current] ** 2 * [time] ** 3 / [length] ** 3 / [mass]',
    'percentage': 'percentage',
}
""" Map quantity names to pint dimensions or None if not a pint dimension. """

# build list of all supported units
_supported_units: list[None | str] = [None]
for v in QUANTITY_UNIT_MAP.values():
    _supported_units.extend(v)

# These units are not stored as a tag unit but as a tag value in the Base tag,
# so they need special treatment.
# Note that this list is a total static list. The actual valid units depend on the
# totalizers that are defined in the uod.
BASE_VALID_UNITS = ['L', 'h', 'min', 's', 'mL', 'CV', 'g', 'kg']


def get_supported_units() -> list[str | None]:
    return list(_supported_units)

def is_supported_unit(unit: str) -> bool:
    return unit in _supported_units

def get_volume_units():
    return QUANTITY_UNIT_MAP['volume']

def get_unit_quantity_name(unit: str) -> str:
    """ For a supported unit that is not None, return its quantity name. Raises ValueError if the unit is not supported. """
    for key in QUANTITY_UNIT_MAP.keys():
        if unit in QUANTITY_UNIT_MAP[key]:
            return key
    raise ValueError(f"Invalid unit: '{unit}'")

def _get_quantity_name_for_pint_dim(pint_dimension: str) -> str | None:
    for key in QUANTITY_PINT_MAP.keys():
        vals = QUANTITY_PINT_MAP[key]
        if vals is not None:
            if pint_dimension == vals:
                return key

def get_compatible_unit_names(unit: str | None) -> list[str]:
    """ For a supported unit, return its compatible units. If the unit is not supported, a ValueError is raised. """
    if unit is None:
        return [""]

    quantity_name = get_unit_quantity_name(unit)
    assert quantity_name is not None and quantity_name != ""

    pint_mapping = QUANTITY_PINT_MAP.get(quantity_name)
    if pint_mapping is None:
        # non-pint unit, return all units of this quantity name
        return QUANTITY_UNIT_MAP[quantity_name]

    pu = _get_pint_unit(unit)
    if pu is None:
        return [""]
    elif unit == "%":
        return ['%']
    elif pu.dimensionless:
        return [""]
    else:
        dims = pu.dimensionality
        quantity_name = _get_quantity_name_for_pint_dim(str(dims))
        if quantity_name is not None:
            return QUANTITY_UNIT_MAP[quantity_name]
        raise NotImplementedError(f"Pint unit '{pu}' with dimensionality '{str(dims)}' has no defined quantity name")

def are_comparable(unit_a: str | None, unit_b: str | None) -> bool:
    """ Determine whether two supported units are comparable, i.e. have the same quantity name.

    For example, 'cm' and 'm' are comparable because they have the same quantity name, 'length'.

    If one or both units are not supported, raise ValueError.
    """
    if unit_a == unit_b:
        return True
    if unit_a is None or unit_b is None:
        return False
    if get_unit_quantity_name(unit_a) != get_unit_quantity_name(unit_b):
        return False
    compatibles_a = get_compatible_unit_names(unit_a)
    result = unit_b in compatibles_a
    return result

def compare_values(op: str, value_a: str, unit_a: str | None, value_b: str, unit_b: str | None) -> bool:
    """ Compare two values using the provided operator (<, <=, >, >=, =, ==, !=) and return the comparison result.

    If units are given, the units are checked for comparability. The units may be different as long as they are comparable.

    In case of error, a ValueError is raised.
    """
    if not are_comparable(unit_a, unit_b):
        raise ValueError(f"Cannot compare values with incompatible units '{unit_a}' and '{unit_b}'")

    def is_pint():
        if unit_a is not None and unit_a != unit_b:
            quantity_name = get_unit_quantity_name(unit_a)
            assert quantity_name is not None and quantity_name != ""

            pint_mapping = QUANTITY_PINT_MAP.get(quantity_name, None)
            if pint_mapping is None:
                # different non-pint units cannot currently be compared. To support these, we must provide a conversion
                # to the base (SI) unit that can be applied before comparison. We don't currently need this.
                raise NotImplementedError(f"Custom comparison of non-pint units {unit_a} and {unit_b} is not supported")
            else:
                return True
        return False

    is_pint_units = is_pint()
    if is_pint_units:
        fval_a, fval_b = as_float(value_a), as_float(value_b)
        if fval_a is None:
            raise ValueError("Cannot compare values, first value is missing or not numeric")
        if fval_b is None:
            raise ValueError("Cannot compare values, second value is missing or not numeric")
        quantity_a = value_a if unit_a is None else pint.Quantity(fval_a, unit_a)
        quantity_b = value_b if unit_b is None else pint.Quantity(fval_b, unit_b)
    else:
        assert unit_a == unit_b, f"Units should be the same but are not, '{unit_a}' vs '{unit_b}'"
        quantity_a = value_a
        quantity_b = value_b

    # we can now ignore units and conversion - either they're None or equal - or they are
    # pint units for which Quantity handles comparison automatically

    # infer when to do numeric vs string comparison. this is only relevant for non-pint units
    if not is_pint_units:
        if op in ['<', '<=', '>', '>=']:  # these operators only make sence for numeric values
            assert isinstance(quantity_a, str), f"quantity_a '{quantity_a}' should be a str here"
            assert isinstance(quantity_b, str), f"quantity_b '{quantity_b}' should be a str here"
            quantity_a, quantity_b = as_float(quantity_a), as_float(quantity_b)
            if quantity_a is None:
                raise ValueError("Cannot compare values, first value is missing or not numeric")
            if quantity_b is None:
                raise ValueError("Cannot compare values, second value is missing or not numeric")
        else:
            # if both are numerical, perform a numerical comparison
            assert isinstance(quantity_a, str), f"quantity_a '{quantity_a}' should be a str here"
            assert isinstance(quantity_b, str), f"quantity_b '{quantity_b}' should be a str here"
            quantity_a_f, quantity_b_f = as_float(quantity_a), as_float(quantity_b)
            if quantity_a_f is not None and quantity_b_f is not None:
                quantity_a, quantity_b = quantity_a_f, quantity_b_f

    try:
        match op:
            case '<':
                result = quantity_a < quantity_b  # type: ignore
            case '<=':
                result = quantity_a <= quantity_b  # type: ignore
            case '=' | '==':
                result = quantity_a == quantity_b
            case '>':
                result = quantity_a > quantity_b  # type: ignore
            case '>=':
                result = quantity_a >= quantity_b  # type: ignore
            case '!=':
                result = quantity_a != quantity_b
            case _:
                raise ValueError(f"Invalid operator: '{op}'")
    except TypeError:
        msg = "Conversion type error for values {!r} and {!r}".format(value_a, value_b)
        logger.error(msg, exc_info=True)
        raise ValueError("Conversion error")

    assert isinstance(result, bool), f"Comparison result was not type bool but {type(result)}"
    return result

def as_float(value: str) -> float | None:
    """ Parse string value as a float and return it. If the value is not a number, return None. """
    try:
        return float(value)
    except Exception:
        return None

def as_int(value: str) -> int | None:
    """ Parse string value as int and return it. If the value is not an int, return None. """
    fval = as_float(value)
    if fval is not None:
        if fval.is_integer():
            return int(fval)
    return None

def _get_pint_unit(unit: str | None) -> pint.Unit | None:
    if unit is None:
        return None
    try:
        return pint.Unit(unit)
    except Exception:
        logger.error(f"Could not get pint unit for unit '{unit}'")
        raise
