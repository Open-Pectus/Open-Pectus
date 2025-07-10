
import re
from openpectus.lang.exec.units import BASE_VALID_UNITS


# Functions to create common regular expressions

def RegexNumber(units: list[str] | None, non_negative: bool = False, int_only: bool = False) -> str:
    """ Create a regex that parses a number with optional unit to arguments `number` and optionally `number_unit`.

    `number_unit` is only matched if one or more units are given.
    """
    sign_part = "" if non_negative else "-?"
    unit_part = " ?(?P<number_unit>" + "|".join(re.escape(unit).replace(r"/", r"\/") for unit in units) + ")" \
        if units else ""
    if int_only:
        return rf"^\s*(?P<number>{sign_part}[0-9]+?|{sign_part}[0-9]+)\s*{unit_part}\s*$"
    else:
        return rf"^\s*(?P<number>{sign_part}[0-9]+[.][0-9]*?|{sign_part}[.][0-9]+|{sign_part}[0-9]+)\s*{unit_part}\s*$"


def RegexNumberOptional(units: list[str] | None, non_negative: bool = False, int_only: bool = False) -> str:
    """ Create a regex that parses an optional number with optional unit to arguments `number` and optionally `number_unit`.

    `number_unit` is only matched if one or more units are given.
    """
    rn = RegexNumber(units=units, non_negative=non_negative, int_only=int_only)
    return rf"({rn})|^\s*$"


def RegexCategorical(exclusive_options: list[str] | None = None, additive_options: list[str] | None = None) -> str:
    """ Create a regex that parses categorical text into an argument named `option`.

    Examples - exclusive::

        regex = RegexCategorical(exclusive_options=["Open", "Closed"])

        self.assertEqual(re.search(regex, "Closed").groupdict(), dict(option="Closed"))

        self.assertEqual(re.search(regex, "VA01"), None)

        self.assertEqual(re.search(regex, "Open").groupdict(), dict(option="Open"))

        self.assertEqual(re.search(regex, "Open+Closed"), None)


    Examples - exclusive and additive::

        regex = RegexCategorical(exclusive_options=['Closed'], additive_options=['VA01', 'VA02', 'VA03'])

        self.assertEqual(re.search(regex, "Closed").groupdict(), dict(option="Closed"))

        self.assertEqual(re.search(regex, "Closed+VA01"), None)

        self.assertEqual(re.search(regex, "VA01").groupdict(), dict(option="VA01"))

        self.assertEqual(re.search(regex, "VA01+VA02").groupdict(), dict(option="VA01+VA02"))

        self.assertEqual(re.search(regex, "Open+Closed"), None)
    """
    if exclusive_options is None and additive_options is None:
        raise TypeError("RegexCategorical() missing argument 'exclusive_options' or 'additive_options'.")
    exclusive_option_part = "|".join(re.escape(option) for option in exclusive_options) if exclusive_options else ""
    additive_option_part = "|".join(re.escape(option) for option in additive_options) if additive_options else ""
    return rf"^(?P<option>({exclusive_option_part}|({additive_option_part}|\+)+)(?<!\+))\s*$"


def RegexText(allow_empty: bool = False) -> str:
    """ Parses text into an argument named `text`."""
    allow_empty_part = "*" if allow_empty else "+"
    return rf"^(?P<text>.{allow_empty_part})$"


# Commonly used regular expression instances

REGEX_DURATION = RegexNumber(units=['s', 'min', 'h'], non_negative=True)
""" Regex that parses a duration, ie. a number with a time unit to groups 'number' and 'number_unit' """
REGEX_DURATION_OPTIONAL = RegexNumberOptional(units=['s', 'min', 'h'], non_negative=True)
""" Regex that parses an optional duration, i.e. optional number with time unit to groups 'number' and 'number_unit' """
REGEX_INT = RegexNumber(units=None, non_negative=True, int_only=True)
""" Regex that parses an integer to groups 'number' """
REGEX_TEXT = RegexText(allow_empty=True)
""" Regex that parses text input the group 'text' """
REGEX_BASE_ARG = rf"^\s*({'|'.join(BASE_VALID_UNITS)})\s*$"


def get_duration_end(tick_time: float, time: float, unit: str) -> float:
    """ Helper to obtain duration from REGEX_DURATION value. """
    if unit not in ['s', 'min', 'h']:
        raise ValueError(f"Wait argument unit must be a time unit, not '{unit}'")

    seconds = time
    if unit == 'min':
        seconds = 60 * time
    elif unit == 'h':
        seconds = 60 * 60 * time
    return tick_time + seconds
