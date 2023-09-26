import argparse
import logging


def convert_int_to_logging_level(log_level: int) -> int:
    mapping = {0: logging.CRITICAL, 1: logging.INFO, 2: logging.DEBUG}
    return mapping[log_level]


def create_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="UrlScanner",
        description=(
            """Lightweight CLI for analyzing URLs using URLScan.io API. 
            Please set the API_KEY environment variable with your API key
            from URLScan.io or put it inside a .env file.
            If no mode is specified you would enter queries one by one.
            """
        ),
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help=(
            "Determines how verbose the logging would be. There are three "
            "possible values: 0 (critical), 1 (info), and 2 (debug). The default value "
            "is set to 0 when no verbose flag is present. If a flag is added with no "
            "value specified, it is set to 2. Otherwise, it will simply use the value "
            "specified."
        ),
        choices=[0, 1, 2],
        default=0,
        nargs="?",
        const=2,
        type=int,
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-b",
        "--batch-investigate",
        help=(
            "Investigates the URLScan.io queries included in the specified file. The file format should "
            "Contain a JSON in each row, where each json need a url and visibility attributes. "
            "The output is a CSV file containing searched url, screenshot url, maliciousness score "
            "given by the api and link to the full online report."
        ),
        type=str,
    )

    group.add_argument(
        "-q",
        "--quotas",
        help="Show the remaining quotas of the user.",
        action="store_true",
    )

    return parser
