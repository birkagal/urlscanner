import os
import csv
import json
import sqlite3
import logging
from datetime import datetime


class IOManager:
    def __init__(self, log_level: int, output_dir="./output"):
        self.output_dir = output_dir  # Path to the output directory

        # Get logger and set level based on user choice
        self.logger = logging.getLogger("__name__")
        self.logger.setLevel(log_level)

        # Connect to SQLite database and create table if not exist
        self.db = sqlite3.connect("urlscanner.db", isolation_level=None).cursor()
        self.db.execute(
            "create table if not exists queries (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, url TEXT NOT NULL, visibility TEXT NOT NULL)"
        )
        self.db.execute(
            "create table if not exists results (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, url TEXT NOT NULL, screenshotURL TEXT NOT NULL, isMalicious TEXT NOT NULL, maliciousness TEXT NOT NULL, report_url TEXT NOT NULL)"
        )

    def __check_query_in_database(self, query: dict) -> bool:
        self.db.execute("SELECT id FROM queries WHERE url = ?", (query["url"],))
        data = self.db.fetchall()
        return len(data) != 0

    def __add_query_to_database(self, query: dict) -> None:
        self.db.execute(
            "INSERT INTO queries VALUES (?, ?, ?)",
            (None, query["url"], query["visibility"]),
        )

    def __add_result_to_database(self, result: dict) -> None:
        self.db.execute(
            "INSERT INTO results VALUES (?, ?, ?, ?, ?, ?)",
            (
                None,
                result["url"],
                result["screenshotURL"],
                result["isMalicious"],
                result["maliciousness"],
                result["report_url"],
            ),
        )

    def add_queries_to_queue_from_file(
        self, scanner: object, queue: object, path: str
    ) -> None:
        try:
            with open(path) as f:
                for counter, query in enumerate(f):
                    # Parse query and validate existence of URL attribute
                    try:
                        query = json.loads(query)
                    except ValueError:
                        self.logger.debug(f"Invalid JSON object. Recieved: {query}")
                        continue
                    if "url" not in query:
                        self.logger.debug(
                            f"Query provided without url attribute. Ignoring: {query}"
                        )
                        continue

                    # Use visibility if provided else use default to public
                    query["visibility"] = (
                        query["visibility"] if "visibility" in query else "public"
                    )

                    if self.__check_query_in_database(query):
                        self.logger.debug(f"{query['url']} already in DB. skipping...")
                        continue

                    if not scanner.update_quotas(query["visibility"]):
                        self.logger.critical("Closing the file...")
                        self.logger.info(
                            f"Scanned the first {counter} rows in the file."
                        )
                        break

                    self.__add_query_to_database(query)
                    queue.put(query)  # Add query to work queue

        except FileNotFoundError:
            self.logger.critical(f"Couldn't open file at {path}")

        queue.join()  # Wait for queue to get empty

    def save_csv(self, reports: list) -> None:
        self.logger.critical("All work completed. Saving data...")

        if not reports:
            self.logger.critical("Noting to save.")
            return

        # Check if output directory exists, create if doesn’t
        if not os.path.isdir(self.output_dir):
            os.mkdir(self.output_dir)

        # Generate output filename based on current time
        filename = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")

        with open(f"{self.output_dir}/{filename}.csv", "w+", newline="") as f:
            output = csv.writer(f)
            output.writerow(
                ["url", "screenshotURL", "isMalicious", "maliciousness", "report_url"]
            )
            output.writerow([])
            for report in reports:
                if report:
                    self.__add_result_to_database(report)
                    output.writerow(
                        [
                            report["url"],
                            report["screenshotURL"],
                            report["isMalicious"],
                            report["maliciousness"],
                            report["report_url"],
                        ]
                    )
        self.logger.critical(
            f"Saving completed. You can check the result at {f'{self.output_dir}/{filename}.csv'}"
        )
        self.db.close()  # Close the database
