import argparse
import multiprocessing
import os

from app.config import TEMPLATES_FILE
from app.core.engine import LogParser
from app.utils import parse_templates_file, merge_tables, print_table


def main() -> None:
    parser = argparse.ArgumentParser(description="Logs Parser")

    parser.add_argument("files", nargs="+", help="input file names")
    parser.add_argument("-r", "--report", metavar="REPORT_NAME", help="name of the report")
    parser.add_argument("-o", "--output", metavar="OUTPUT_FILE", help="name of the output report file")

    args = parser.parse_args()
    missing_files = [f for f in args.files if not os.path.exists(f)]
    if missing_files:
        parser.error(f"these files does not exist: {', '.join(missing_files)}")

    if not os.path.exists(TEMPLATES_FILE):
        parser.error(f"template file '{TEMPLATES_FILE}' does not exist")

    report_template = parse_templates_file(TEMPLATES_FILE, args.report)
    if not report_template:
        parser.error(f"template file '{TEMPLATES_FILE}' is not correct")

    result_queue = multiprocessing.Queue()
    processes = []

    for file_name in args.files:
        parser = LogParser(report_template, file_name, result_queue)
        processes.append(parser)
        parser.start()

    for process in processes:
        process.join()

    collected_data = []
    while not result_queue.empty():
        collected_data.append(result_queue.get())

    merged_data = merge_tables(*collected_data)

    if args.output:
        directory = os.path.dirname(args.output)

        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        with open(args.output, "w") as f:
            print_table(merged_data, report_template, file=f)
        print(f"Report file '{args.output}' was created")
    else:
        print_table(merged_data, report_template)
