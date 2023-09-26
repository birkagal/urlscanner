import os
import logging
from dotenv import load_dotenv
from queue import Queue
from threading import Thread
from urlscanner.iomanager import IOManager
from urlscanner.client import UrlScannerClient
from urlscanner.util import create_arg_parser, convert_int_to_logging_level

NUM_THREADS = 10


def interactive_query(scanner: UrlScannerClient) -> None:
    print("Welcome to UrlScanner interactive cli tool.\n")
    url = input("Please enter the requested URL: ")
    while True:  # Loop until user provide valid visibility parameter
        visibility = input(
            "Please enter the requested visibility [public, private, unlisted]: "
        ).lower()
        if visibility not in ["public", "private", "unlisted"]:
            print("Please enter either public, private or unlisted.")
            continue
        break
    print("Fetching results...")
    report = scanner.generate_report(url, visibility)
    if report == {}:
        print(f"Couldn't analyze {url}")
    else:
        print(
            f"""
        FINISHED! 
        Results:
        Scanned URL: {report['url']}
        Screenshot URL: {report['screenshotURL']}
        isMalicious: {report['isMalicious']}
        Maliciousness: {report['maliciousness']}
        Report URL: {report['report_url']}\n
        """
        )


def show_user_quotas(scanner: UrlScannerClient) -> None:
    print(
        f"""
    Public visibility:
    Day: {scanner.quotas['public']['day']['remaining']} remaining.
    Hour: {scanner.quotas['public']['hour']['remaining']} remaining.
    Minute: {scanner.quotas['public']['minute']['remaining']} remaining.

    Unlisted visibility:
    Day: {scanner.quotas['unlisted']['day']['remaining']} remaining.
    Hour: {scanner.quotas['unlisted']['hour']['remaining']} remaining.
    Minute: {scanner.quotas['unlisted']['minute']['remaining']} remaining.

    Private visibility:
    Day: {scanner.quotas['private']['day']['remaining']} remaining.
    Hour: {scanner.quotas['private']['hour']['remaining']} remaining.
    Minute: {scanner.quotas['private']['minute']['remaining']} remaining.

    Result Retrieve:
    Day: {scanner.quotas['retrieve']['day']['remaining']} remaining.
    Hour: {scanner.quotas['retrieve']['hour']['remaining']} remaining.
    Minute: {scanner.quotas['retrieve']['minute']['remaining']} remaining.\n
    """
    )


def batch_investigate(
    scanner: UrlScannerClient, io: IOManager, input_file: str
) -> None:
    reports = []  # List of all queries results
    q = Queue()  # Queue that will manage the work

    # Instantiate NUM_THREADS threads and send them to worker function where they will wait for work
    for _ in range(NUM_THREADS):
        Thread(
            target=worker,
            args=(
                scanner,
                q,
                reports,
            ),
            daemon=True,
        ).start()

    # Read queries from the given file and add each valid query to the queue
    success = io.add_queries_to_queue_from_file(scanner, q, input_file)
    if success:
        # Save the results to a csv file
        io.save_csv(reports)


def worker(scanner, q, reports):
    report = {}  # The result of a given query
    while True:
        query = q.get()  # Get the next query
        # Use API to scan and retrieve result for that query.
        report = scanner.generate_report(query["url"], query["visibility"])
        reports.append(report)
        q.task_done()  # Mark that query as finished


if __name__ == "__main__":
    # Create argparse menu and get program args
    parser = create_arg_parser()
    args = parser.parse_args()
    log_level = convert_int_to_logging_level(args.verbose)

    # Create logging configuration
    logging.basicConfig(
        format="%(asctime)s : %(levelname)s : %(message)s", datefmt="%H:%M:%S"
    )

    # Load the enviorment variable and instantiate the scanner and IO objects
    load_dotenv()
    scanner = UrlScannerClient(os.getenv("API_KEY"), log_level)
    io = IOManager(log_level)

    # Run program in user specified mode
    if args.batch_investigate:
        batch_investigate(scanner, io, args.batch_investigate)
    elif args.quotas:
        show_user_quotas(scanner)
    else:
        interactive_query(scanner)
    print("Exiting...")
