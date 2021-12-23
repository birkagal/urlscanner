import time
import json
import requests
import logging


class UrlScanner:
    MAX_POLL_ATTEMPS = 10  # Maximum number of tries to poll from result API
    PAUSE_BETWEEN_POLL = 5  # Time in seconds between each poll
    PAUSE_BEFORE_RESULT = 10  # Time between scan submission and retrieval

    API_URL = "https://urlscan.io/api/v1"
    QUOTAS_URL = "https://urlscan.io/user/quotas/"

    def __init__(self, api_key: str, log_level: int):
        self.api_key = api_key

        # Set default header since all requests have the same
        self.headers = {"API-Key": self.api_key, "Content-Type": "application/json"}

        # Get logger and set level based on user choice
        self.logger = logging.getLogger("__name__")
        self.logger.setLevel(log_level)

        self.quotas = self.__quotas()

    def __quotas(self) -> dict:
        # Make request to quotas URL and return the 'limits' object with the user quotas
        status, body = self.__fetch("GET", self.QUOTAS_URL)
        if status >= 400:
            self.logger.critical("Error while fetching user quotas.")
            return {}
        return body["limits"]

    def __fetch(
        self, method: str, url: str, headers: dict = None, data: dict = None
    ) -> dict:
        # Set headers and data to either user provided information or object defaults
        headers = self.headers if not headers else headers
        data = "" if not data else json.dumps(data)

        # Send HTTP requests to given URL using given method and parse result
        response = requests.request(method, url, headers=headers, data=data)
        body = json.loads(response.text)
        return response.status_code, body

    def __scan(self, url: str, visibility: str) -> str:
        # Prepare the request url and header, and make the POST request
        api_url = self.API_URL + "/scan/"
        data = {"url": url, "visibility": visibility}
        status, body = self.__fetch("POST", api_url, data=data)

        # Check if the API returned with 429 - Too many requests
        if status == 429:
            self.logger.debug(
                "Too many requests for scan. Waiting {self.PAUSE_BETWEEN_POLL} seconds and trying again..."
            )
            time.sleep(
                self.PAUSE_BETWEEN_POLL
            )  # Wait a bit before making another request
            status, body = self.__fetch(
                "POST", api_url, data=data
            )  # Try to fetch the data again
        if status >= 400:
            self.logger.info(
                f"Scan was not completed. Description: {body['description']}"
            )

        return body["uuid"] if "uuid" in body else ""

    def __result(self, uuid: str) -> dict:
        api_url = self.API_URL + f"/result/{uuid}"

        attemps = 0
        while attemps < self.MAX_POLL_ATTEMPS:
            # Try and retrieve the result from API
            status, body = self.__fetch("GET", api_url)
            if status >= 400:
                # If result is not ready wait a bit and try again
                attemps += 1
                self.logger.debug(
                    f"Result for: {uuid} not ready yet. Tried {attemps} times. Waiting {self.PAUSE_BETWEEN_POLL} seconds..."
                )
                time.sleep(self.PAUSE_BETWEEN_POLL)
            else:
                # Make sure the result is not empty
                if not body["lists"]["ips"]:
                    self.logger.info(
                        f"{body['task']['url']} is unaccessible. Result has been removed."
                    )
                    return {}
                # Return the specific result
                self.logger.debug(f"Received result for {body['task']['url']}")
                return {
                    "url": body["task"]["url"],
                    "screenshotURL": body["task"]["screenshotURL"],
                    "isMalicious": body["verdicts"]["overall"]["malicious"],
                    "maliciousness": body["verdicts"]["overall"]["score"],
                    "report_url": body["task"]["reportURL"],
                }
        return {}

    def generate_report(self, url: str, visibility: str = "public") -> dict:
        # Make scan API request for given URL
        uuid = self.__scan(url, visibility)

        if uuid == "":
            self.logger.critical(f"Couldn't get submission for {url}")
            return {}

        # Wait after sending scan requests and before getting the results
        self.logger.debug(
            f"Submitted {url}, waiting {self.PAUSE_BEFORE_RESULT} seconds before polling."
        )
        time.sleep(self.PAUSE_BEFORE_RESULT)

        result = self.__result(uuid)
        if result == {}:
            self.logger.critical(f"Couldn't get result for {url}.")

        return result

    def update_quotas(self, section: str) -> None:
        if self.quotas[section]["day"]["remaining"] <= 0:
            self.logger.critical(
                f"Not enough daily quotas for section: {section}. Please try again with different section or wait for midnight UTC."
            )
            return False

        if self.quotas[section]["hour"]["remaining"] <= 0:
            self.logger.critical(
                f"Not enough hourly quotas for section: {section}. Please try again with different section or wait for the top of the hour."
            )
            return False

        if self.quotas[section]["minute"]["remaining"] <= 0:
            self.logger.critical(
                f"Not enough minute quotas for section {section}. Please try again with different section or wait a few seconds."
            )
            return False

        # If there is enough quotas, decrease by one and keep going
        self.quotas[section]["minute"]["remaining"] -= 1
        self.quotas[section]["hour"]["remaining"] -= 1
        self.quotas[section]["day"]["remaining"] -= 1

        return True
