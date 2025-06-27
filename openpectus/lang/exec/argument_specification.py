from __future__ import annotations
from functools import wraps
import re


class ArgSpec():
    NoArgsInstance: ArgSpec
    NoCheckInstance: ArgSpec

    def __init__(self, regex):
        self.regex = regex

    def validate(self, argument: str) -> bool:
        match = re.match(self.regex, argument)
        return match is not None

    def validate_w_groups(self, argument: str) -> dict[str, str] | None:
        match = re.match(self.regex, argument)
        return match.groupdict() if match is not None else None

    @staticmethod
    def NoArgs() -> ArgSpec:
        """ Specify that no argument must be present, not even whitespace """
        return ArgSpec.NoArgsInstance

    @staticmethod
    def NoCheck() -> ArgSpec:
        """ Specify that no argument check should be performed """
        return ArgSpec.NoCheckInstance

    @staticmethod
    def Regex(regex: str) -> ArgSpec:
        """ Speficy that the argument must match the given regex """
        return ArgSpec(regex=regex)

    def __str__(self):
        if self.regex == ArgSpec.NoArgsInstance.regex:
            return "ArgSpec.NoArgsInstance"
        elif self.regex == ArgSpec.NoCheckInstance.regex:
            return "ArgSpec.NoCheckInstance"
        else:
            return f"ArgSpec(regex={self.regex})"


# late initialization of static members, seems the only way the type checker accepts it.
ArgSpec.NoArgsInstance = ArgSpec(regex="^$")
ArgSpec.NoCheckInstance = ArgSpec(regex="")


def command_argument(validation_spec: ArgSpec):
    """ Decorator to decorate a command class with an argument validation spec """
    def decorator(cls):
        cls.argument_validation_spec = validation_spec

        @wraps(cls)
        def wrapper(*args, **kwargs):
            return cls(*args, **kwargs)
        return wrapper
    return decorator

def command_argument_none():
    """ Decorator for command class. Specifies that the command takes no arguments. """
    return command_argument(ArgSpec.NoArgs())

def command_argument_regex(regex: str):
    """ Decorator for command class. Specifies that the command arguments string must match
    the given regular expression.

    Additionally, if the regex uses capture groups, the group values for a given argument can
    be extracted in a generic way. """
    return command_argument(ArgSpec.Regex(regex=regex))
