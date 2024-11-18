from __future__ import annotations
import logging

import pint
from pint import UnitRegistry, Quantity


ureg = UnitRegistry(cache_folder="./pint-cache")
ureg.define("m2 = m**2")
ureg.define("dm2 = dm**2")
ureg.define("cm2 = cm**2")
ureg.define("LMH = mm/h")
ureg.define("wt = 1")
ureg.define("vol = 1")
ureg.define("AU = [absorbance]")
Q_ = Quantity

logger = logging.getLogger(__name__)

# https://en.wikipedia.org/wiki/International_System_of_Units
# defines all the units we accept, each with their quantity name (similar to pint dimensionality).
QUANTITY_UNIT_MAP = {
    'time': ['s', 'min', 'h', 'ms'],                # SI quantities
    'length': ['m', 'cm'],
    'area': ['m**2', 'm2', 'dm2', 'cm2'],
    'mass': ['kg', 'g'],
    'density': ['kg/L', 'g/L'],
    'temperature': ['degC', 'degF', 'K', '°C', '°F'],
    'amount_of_substance': ['mol'],
    'volume': ['L', 'mL'],                          # Derived quantities
    'flow': ['L/h', 'L/min', 'L/d'],
    'frequency': ['Hz', 'kHz'],
    'pressure': ['Pa', 'bar', 'pascal'],            # Note: pint prefers pascal over Pa so we define both.
    'mass flow rate': ['kg/h', 'g/s', 'g/min', 'g/h'],
    'electrical conductance': ['mS/cm'],
    'percentage': ['%', 'vol%', 'wt%', 'mol%'],     # Custom quantity but supported by pint
    'column volume': ['CV'],                        # Custom quantity
    'absorbance': ['AU', 'mAU', 'milliAU'],
    'permeability': ['LMH/bar', 'L/m2/h/bar', 'L/h/m2/bar'],
    'flux': ['LMH', 'L/m2/h', 'L/h/m2'],
}
""" Map quantity names to unit names. """

QUANTITY_PINT_MAP: dict[str, str] = {
    'time': '[time]',
    'length': '[length]',
    'area': '[length] ** 2',
    'mass': '[mass]',
    'density': '[mass] / [length] ** 3',
    'flow': '[length] ** 3 / [time]',
    'volume': '[length] ** 3',
    'frequency': '1 / [time]',
    'temperature': '[temperature]',
    'amount_of_substance': '[substance]',
    'pressure': '[mass] / [length] / [time] ** 2',
    'mass flow rate': '[mass] / [time]',
    'electrical conductance': '[current] ** 2 * [time] ** 3 / [length] ** 3 / [mass]',
    'percentage': '[percentage]',
    'flux': '[length] / [time]',
    'permeability': '[length] ** 2 * [time] / [mass]',
    'absorbance': '[absorbance]',
}
""" Map quantity names to pint dimensions or None if not a pint dimension. """

FLOAT_COMPARE_DELTA = 0.01
""" The precision to use when comparing float values for equality. """

# build list of all supported units
_supported_units: list[None | str] = [None]
for v in QUANTITY_UNIT_MAP.values():
    _supported_units.extend(v)

# These units are not stored as a tag unit but as a tag value in the Base tag,
# so they need special treatment.
# Note that this list is a total static list. The actual valid units depend on the
# totalizers that are defined in the uod.
BASE_VALID_UNITS = ['L', 'h', 'min', 's', 'mL', 'CV', 'DV', 'g', 'kg']


def get_supported_units() -> list[str | None]:
    return list(_supported_units)

def is_supported_unit(unit: str) -> bool:
    return unit in _supported_units

def get_volume_units():
    return QUANTITY_UNIT_MAP['volume']

def convert_value_to_unit(value: float | int, source_unit: str, target_unit: str) -> float:
    """ Convert a value with a unit to the value in another unit.

    Raises ValueError if the units are not compatible.
    """
    try:
        val = ureg.Quantity(value, source_unit).to(target_unit).magnitude
        return val
    except pint.DimensionalityError:
        raise ValueError(f"Cannot convert between units '{source_unit}' and '{target_unit}'")

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
        return ['%', 'vol%', 'wt%', 'mol%']
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
        quantity_a = value_a if unit_a is None else ureg.Quantity(fval_a, unit_a)
        quantity_b = value_b if unit_b is None else ureg.Quantity(fval_b, unit_b)
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
                if isinstance(quantity_a, Quantity) and isinstance(quantity_b, Quantity):
                    diff = quantity_a - quantity_b
                    result = abs(diff.magnitude) < FLOAT_COMPARE_DELTA
                elif isinstance(quantity_a, float) and isinstance(quantity_b, float):
                    result = abs(quantity_a - quantity_b) < FLOAT_COMPARE_DELTA
                else:
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
        return ureg.Unit(unit)
    except Exception:
        logger.error(f"Could not get pint unit for unit '{unit}'")
        raise
