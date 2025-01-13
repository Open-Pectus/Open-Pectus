import logging
import os
import sentry_sdk
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from openpectus import __version__ as openpectus_version, build_number
from openpectus.lang.exec.uod import UnitOperationDefinitionBase

# Sentry docs: https://docs.sentry.io/platforms/python
# Logging docs: https://docs.sentry.io/platforms/python/integrations/logging

# define valid leves for use as sentry event_level filter
_event_levels: list[int] = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]
EVENT_LEVEL_DEFAULT: str = logging.getLevelName(logging.WARNING)
EVENT_LEVEL_NAMES: list[str] = [logging.getLevelName(level) for level in _event_levels]

SENTRY_DEBUG = False


def _get_event_level_from_name(event_level_name: str) -> int:
    event_level_name = event_level_name.upper()
    if event_level_name not in EVENT_LEVEL_NAMES:
        raise ValueError(f"Invalid event_level_name specified: {event_level_name}. " +
                         f"Must be one of {','.join(EVENT_LEVEL_NAMES)}")
    return logging.getLevelNamesMapping()[event_level_name]


def init_aggregator(event_level_name: str):
    """ Initialize sentry logging for the aggregator component.

    Note: call after initializing logging.

    - Enables integrations FastAPI and Starlette
    - Attaches component='aggregator' to all events
    """
    if os.getenv('SENTRY_DSN'):
        print("Sentry is active")
    else:
        print("Sentry is not active")

    event_level_int = _get_event_level_from_name(event_level_name)

    sentry_sdk.init(
        default_integrations=False,
        auto_enabling_integrations=False,
        integrations=[
            StarletteIntegration(transaction_style="endpoint"),
            FastApiIntegration(transaction_style="endpoint"),
            LoggingIntegration(
                level=logging.INFO,        # Capture info and above as breadcrumbs
                event_level=event_level_int   # Send records as events
            )
        ],
        auto_session_tracking=False,
        send_default_pii=False,
        release=openpectus_version,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # traces_sample_rate=1.0,
        # enable_tracing=True,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        # profiles_sample_rate=1.0,
        debug=SENTRY_DEBUG,
        # server_name is set to machine name by default, which is fine
        # server_name="aggregator",
        # before_send works but we'd rather use tags instead
        # before_send=agg_before_send,
        # before_send_transaction is not currently called
        # maybe transactions are for traces only?
        # before_send_transaction=agg_before_send_transaction,
    )
    # this seems to attach component to all events
    sentry_sdk.set_tag("component", "aggregator")
    sentry_sdk.set_tag("build_number", build_number)

    with sentry_sdk.new_scope():
        sentry_sdk.capture_message("Aggregator sentry logging initialized")

def init_engine(event_level_name: str):
    """ Initialize sentry logging for the engine component.

    - Attaches tag component='engine' to all events
    """

    event_level_int = _get_event_level_from_name(event_level_name)

    sentry_sdk.init(
        # default_integrations=False,
        auto_enabling_integrations=False,
        integrations=[
            LoggingIntegration(
                level=logging.INFO,        # Capture info and above as breadcrumbs
                event_level=event_level_int   # Send records as events
            )
        ],
        auto_session_tracking=False,
        send_default_pii=False,
        release=openpectus_version,
        debug=SENTRY_DEBUG,
    )
    # this seems to attach component to all events
    sentry_sdk.set_tag("component", "engine")
    sentry_sdk.set_tag("build_number", build_number)

    with sentry_sdk.new_scope():
        sentry_sdk.capture_message("Engine sentry logging initialized")

def set_engine_uod(uod: UnitOperationDefinitionBase):
    """ Attaches tags uod_instrument and uod_location to events. """
    sentry_sdk.set_tag("uod_instrument", uod.instrument)
    sentry_sdk.set_tag("uod_location", uod.location)

def engine_method_set(pcode: str):
    """ Attaches tag 'method' with pcode source to events """
    # Note: There is no great format to use but this works reasonably well.
    # To recover pcode formatting, replace \\n with \n (extended/regex) in vscode or npp
    dct = {"pcode": pcode}
    sentry_sdk.set_tag("method", dct)
