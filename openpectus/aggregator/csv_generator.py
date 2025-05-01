import csv
import logging
from io import StringIO
from operator import concat
from typing import Iterable

from openpectus.aggregator.routers.dto import PlotLog, RecentRun, ProcessValueValueType

logger = logging.getLogger(__name__)


def generate_csv_string(plot_log: PlotLog, recent_run: RecentRun):
    csv_string = StringIO()
    csv_writer = csv.writer(csv_string)
    _write_metadata_rows(csv_writer, plot_log, recent_run)
    _write_header_row(csv_writer, plot_log)
    _write_data_rows(csv_writer, plot_log, _get_tick_times(plot_log))
    return csv_string


def _write_metadata_rows(csv_writer, plot_log: PlotLog, recent_run: RecentRun):
    csv_writer.writerow(['# Run Id', recent_run.run_id])
    csv_writer.writerow(['# Engine Id', recent_run.engine_id])
    csv_writer.writerow(['# Engine Computer Name', recent_run.engine_computer_name])
    csv_writer.writerow(['# Open Pectus Engine Version', recent_run.engine_version])
    csv_writer.writerow(['# Engine Hardware string', recent_run.engine_hardware_str])
    csv_writer.writerow(['# UOD Author Name', recent_run.uod_author_name])
    csv_writer.writerow(['# UOD Author Email', recent_run.uod_author_email])
    csv_writer.writerow(['# UOD File Name', recent_run.uod_filename])
    csv_writer.writerow(['# Aggregator Computer Name', recent_run.aggregator_computer_name])
    csv_writer.writerow(['# Open Pectus Aggregator Version', recent_run.aggregator_version])
    csv_writer.writerow(['# Started Date (UTC)', recent_run.started_date])
    csv_writer.writerow(['# Completed Date (UTC)', recent_run.completed_date])
    csv_writer.writerow(concat(['# Contributors'], recent_run.contributors))
    csv_writer.writerow([])


def _get_tick_times(plot_log: PlotLog):
    list_of_all_tick_times = (value.tick_time for entry in plot_log.entries.values() for value in entry.values)
    unique_tick_times = list(set(list_of_all_tick_times))
    unique_tick_times.sort()
    return unique_tick_times


def _write_data_rows(csv_writer, plot_log: PlotLog, unique_tick_times: Iterable[float]):
    for tick_time in unique_tick_times:
        row: list[ProcessValueValueType] = []
        for entry in plot_log.entries.values():
            if len(entry.values) == 0:
                row.append(None)
                continue
            elif len(entry.values) >= 2 and tick_time >= entry.values[1].tick_time:
                entry.values.pop(0)
            row.append(entry.values[0].value)
        csv_writer.writerow(row)


def _write_header_row(csv_writer, plot_log: PlotLog):
    # write header row and ensure values are sorted by tick_time
    header_row: list[str] = []
    for entry in plot_log.entries.values():
        entry.values.sort(key=lambda e: e.tick_time)
        header_row.append(entry.name + (f' [{entry.value_unit}]' if entry.value_unit is not None else ''))
    csv_writer.writerow(header_row)
