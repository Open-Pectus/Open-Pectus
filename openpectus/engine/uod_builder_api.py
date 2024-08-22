"""
Defines the standard imports for uod modules.
"""
from openpectus.engine.hardware import HardwareLayerBase, Register
from openpectus.lang.exec.uod import (
    UnitOperationDefinitionBase, UodCommand, UodBuilder,
    RegexNumber, RegexText, RegexCategorical,
)
from openpectus.protocol.models import PlotConfiguration, SubPlot, PlotAxis, PlotColorRegion
import openpectus.lang.exec.tags_impl as tags

__all__ = [
    'HardwareLayerBase', 'Register',
    'UnitOperationDefinitionBase', 'UodCommand', 'UodBuilder',
    'RegexNumber', 'RegexText', 'RegexCategorical',
    'PlotConfiguration', 'SubPlot', 'PlotAxis', 'PlotColorRegion',
    "tags"
]


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
