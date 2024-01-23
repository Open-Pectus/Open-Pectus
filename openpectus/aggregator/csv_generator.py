import csv
from io import StringIO

from openpectus.aggregator.routers.dto import ProcessValueValueType


def generate_csv_string(dto):
    csv_string = StringIO()
    csv_writer = csv.writer(csv_string)
    _write_header_row(csv_writer, dto)
    _write_data_rows(csv_writer, dto, _get_tick_times(dto))
    return csv_string


def _get_tick_times(dto):
    # calculate unique and sorted tick_time values, one for each data row.
    list_of_all_tick_times = (value.tick_time for entry in dto.entries.values() for value in entry.values)
    unique_tick_times = list(set(list_of_all_tick_times))
    unique_tick_times.sort()
    return unique_tick_times


def _write_data_rows(csv_writer, dto, unique_tick_times):
    # write data rows
    for tick_time in unique_tick_times:
        row: list[ProcessValueValueType] = []
        for entry in dto.entries.values():
            if len(entry.values) == 0:
                row.append(None)
                continue
            elif len(entry.values) >= 2 and tick_time >= entry.values[1].tick_time:
                entry.values.pop(0)
            row.append(entry.values[0].value)
        csv_writer.writerow(row)


def _write_header_row(csv_writer, dto):
    # write header row and ensure values are sorted by tick_time
    header_row: list[str] = []
    for entry in dto.entries.values():
        entry.values.sort(key=lambda e: e.tick_time)
        header_row.append(entry.name)
    csv_writer.writerow(header_row)
