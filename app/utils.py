import json
import sys
from collections import defaultdict
from typing import TextIO

from app.config import LOG_LEVELS


REQUIRED_FIELDS = {
    "log_formats": list,
    "filters": dict,
    "x_axis": str,
    "y_axis": str,
}


def parse_json(file: str) -> dict | None:
    try:
        with open(file, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as e:
        print(f"No such file: '{file}'. Please check the file path")
    except json.decoder.JSONDecodeError as e:
        print(f"Invalid JSON format in file '{file}': {e}")
    except Exception as e:
        print(f"Unexpected error reading '{file}': {e}")
    return None


def parse_templates_file(file: str, report_name: str) -> dict:
    data = parse_json(file)

    if not isinstance(data, dict):
        return {}

    if report_name not in data:
        print(f"No report '{report_name}' template found in '{file}'")
        return {}

    for field, field_type in REQUIRED_FIELDS.items():
        if field not in data[report_name]:
            print(f"No field '{field}' found in '{file}'")
            return {}

        if not isinstance(data[report_name][field], field_type):
            print(f"Field '{field}' in file '{file}' has to be of type '{field_type}'")
            return {}

    if len(data[report_name]["log_formats"]) == 0:
        print(f"No log formats found in '{file}'")
        return {}

    for filter in data[report_name]["filters"]:
        for log_format in data[report_name]["log_formats"]:
            if f"<{filter}>" in log_format:
                break
            print(f"Filters found in '{file}' are incorrect. No field '{filter}' found in log templates.")
            return {}


    return data[report_name]


def table_factory():
    return defaultdict(int)


def merge_tables(*tables: defaultdict[str, dict[str, int]]) -> defaultdict[str, dict[str, int]]:
    result = defaultdict(table_factory)

    for table in tables:
        for y_key, inner in table.items():
            for x_key, count in inner.items():
                result[y_key][x_key] += count

    return result


def print_table(
        merged_data: defaultdict[str, dict[str, int]],
        report_template: dict,
        file: TextIO = None,
) -> None:
    headers_from_data = sorted({value for row in merged_data.values() for value in row.keys()})
    unexpected = [level for level in headers_from_data if level not in LOG_LEVELS]
    if unexpected:
        headers = [report_template["y_axis"]] + headers_from_data
    else:
        headers = [report_template["y_axis"]] + LOG_LEVELS
    total = sum(sum(row.values()) for row in merged_data.values())
    total_counts = {level: 0 for level in headers[1:]}

    first_column_width = max([len(key) for key in merged_data.keys()] + [len("HANDLER")]) + 1

    column_widths = {
        header: max(len(header), max(len(str(levels.get(header, 0))) for levels in merged_data.values()))
        for header in headers[1:]
    }
    print(f"Total {report_template["total"]}: {total}", file=file)

    header_row = [f"{headers[0].upper():<{first_column_width}}"] + [
        f"{header:<{column_widths[header]}}" for header in headers[1:]
    ]
    print(" ".join(header_row), file=file)

    # строки
    for url, levels in sorted(merged_data.items(), key=lambda x: x[0]):
        row = [url.ljust(first_column_width)]
        for level in headers[1:]:
            count = levels.get(level, 0)
            row.append(f"{count:<{column_widths[level]}}")
            total_counts[level] += count
        print(" ".join(row), file=file)

    totals_row = ["".ljust(first_column_width)] + [
        f"{total_counts[level]:<{column_widths[level]}}" for level in headers[1:]
    ]
    print(" ".join(totals_row), file=file)
