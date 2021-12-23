# UrlScanner

> Lightweight Python CLI utility which makes use [URLScan.io](https://urlscan.io/) APIs to automate scanning and retrieving information about URLs

[URLScan.io](https://urlscan.io/) is a useful tool for scanning and obtaining information from potentially malicious websites. URLScan provide a useful [API](https://urlscan.io/docs/api/) which can be used to add some automation to your workflow.

## Install & Setup

1. Clone this repository using `git clone https://github.com/birkagal/urlscanner`

2. Consider adding [virtual environments](https://docs.python.org/3/library/venv.html) and install dependencies using `pip install -r requirements.txt`

3. All set. Use `python application.py --help` to see the man page.

## How to use

![enter image description here](https://i.ibb.co/cknWf30/Capture.png)

UrlScanner support two main modes: Analyze multiple URLs from a input file or Interactive one by one analyze. You can always check `python application.py -h` for more help.

### API Key

[URLScan.io](https://urlscan.io/) make use of personal API KEY to access the API features. You need to sign up an account at [URLScan.io](https://urlscan.io/) and save your personal API KEY at `.env` file with the key being `API_KEY` and the value of your actual key. You can also set an environment variable called `API_KEY`.

### Logging Level

The `-v` flag determines how verbose the logging would be. There are three possible values: 0 (critical), 1 (info), and 2 (debug). The default value is set to 0 when no verbose flag is present. If a flag is added with no value specified, it is set to 2. Otherwise, it will simply use the value specified.

### Batch Analysis

You can use the `-b` flag alongside a specified filename containing URLScan.io query in each line. The query should be in JSON format and contain a `url` key and a `visibility` key. The output would be a CSV file containing searched url, screenshot url, maliciousness score given by the api and link to the full online report.
If your `urls.txt` is inside `input` directory, you can use this command to execute:

    python application.py -b /input/urls.txt

### Interactive Analysis

If no flag is provided the utility would ask you to enter manually a `URL` and a `visibility` parameter to scan. It will then use URLScan.io API to scan the URL and present you with the result. To run this mode simply run the application without specifying any other mode. (You can still use flags)

    python application.py -v

### Display User Quotas

URLScan.io API has a Rate limit mechanism to limit the use of the API. There are different quotas per day, hour and minute for each action. You can use the `-q` flag to list the user remaining quotas for each action.

    python application.py -q

## TODO

In this section I would list my thought for the future, the features I didn't had the time to implement.

-   [ ] Display the output in a HTML file, using templating to render a single output page with all the information in a visual way.
-   [ ] All the history of queries and results are stored in a database. Make use of the result table to give an option to search for past result from the utility.

## Implementation

UrlScanner has two main objects, UrlScanner and IOManager.

-   UrlScanner is responsible for communicating with the URLScan.io API service. It holds the logic for submission requests, retrieval requests, parsing the information, quotas Rate Limiter. It follows URLScan.io implemantation advises such as respect 429 code (too many requests) and wait before polling for results. HTTP requests are sent using python requests module.
-   IOManager is responsible for Input/Output and database logic. This tool use python's sqlite3 module to manage an SQLite database. The database has 2 tables: queries and results. The query table is used to make sure each url is only sent once even if it was already sent in the past. The result table is currently just storing the data and it will maybe be helpful in the future. The IOManager also read the input from a file (if working in batch mode), validate the query and add it to the work queue.

The main feature of this tool is the batch analysis. This tool use python Queue module and its threading capabilities to manage a work queue that all the threads can access and get work from. Once the work is done and the queue is empty, the IOManager print the result to a designated csv file.

The application also uses python logging module to create different logging levels that the user can chose from, each level show different amount of information.

The argparse module is used to manage user arguments and flag, and display the man page when running `-h` flag
