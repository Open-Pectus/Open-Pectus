from starlette_admin.contrib.sqla import Admin, ModelView

from openpectus.aggregator.data.models import (
    RecentEngine,
    RecentRun,
    RecentRunMethodAndState,
    RecentRunRunLog,
    RecentRunErrorLog,
    RecentRunPlotConfiguration,
    PlotLogEntryValue,
    PlotLogEntry,
    PlotLog,
)

def build_administration(engine):
    assert engine
    admin = Admin(
        engine,
        title="Administration Panel",
        )

    for model in [
        RecentEngine,
        RecentRun,
        RecentRunMethodAndState,
        RecentRunRunLog,
        RecentRunErrorLog,
        RecentRunPlotConfiguration,
        PlotLogEntryValue,
        PlotLogEntry,
        PlotLog]:
        admin.add_view(ModelView(model))
    return admin