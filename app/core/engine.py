from collections import defaultdict
import multiprocessing
import re

from app.utils import table_factory


class LogParser(multiprocessing.Process):
    def __init__(
            self, report_template: dict, log_file: str,
            result_queue: multiprocessing.Queue
    ) -> None:
        super().__init__()

        self.log_formats = report_template["log_formats"]
        self.filters = report_template["filters"]
        self.x_axis = report_template["x_axis"]
        self.y_axis = report_template["y_axis"]

        self.table = defaultdict(table_factory)

        self.log_file = log_file
        self.result_queue = result_queue

    @staticmethod
    def format_to_regex(pattern: str) -> re.Pattern:
        parts, last = [], 0
        tokens = list(re.finditer(r"<(\w+)>", pattern))
        for i, m in enumerate(tokens):
            parts += [re.escape(pattern[last:m.start()]),
                      f"(?P<{m.group(1)}>{'.*' if i == len(tokens) - 1 else '.*?'})"]
            last = m.end()
        parts.append(re.escape(pattern[last:]))
        return re.compile('^' + ''.join(parts) + '$')

    def best_match(self, log: str, formats: list[str]) -> tuple[str, dict] | None:
        best = None
        best_data = {}
        max_fields = 0

        for fmt in formats:
            exp = self.format_to_regex(fmt)
            match = exp.match(log)
            if match:
                data = match.groupdict()
                filled_fields = sum(1 for v in data.values() if v)
                if filled_fields > max_fields:
                    best = fmt
                    best_data = data
                    max_fields = filled_fields

        return (best, best_data) if best else None


    def parse_line(self, line: str) -> dict:
        data = {}
        result = self.best_match(line, self.log_formats)

        if result:
            _, data = result
            for log_filter in self.filters:
                if log_filter not in data:
                    return {}
                if data[log_filter] != self.filters[log_filter]:
                    return {}

        return data

    def parse_file(self) -> defaultdict[str, dict[str, int]]:
        with open(self.log_file, 'r') as f:
            for line in f:
                line_data = self.parse_line(line)

                x_val = line_data.get(self.x_axis)
                y_val = line_data.get(self.y_axis)

                if x_val and y_val:
                    self.table[y_val][x_val] += 1

        return self.table

    def run(self):
        result = self.parse_file()
        self.result_queue.put(result)

