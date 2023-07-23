# README

This code is a Scrapy spider written in Python that extracts contact information (phone numbers and email addresses) from a list of companies based on their names. It uses web scraping techniques to find the companies' official websites and then extracts the contact information from the "Contact Us" pages of those websites.

## Dependencies

To run this code successfully, you need to have the following Python packages and programs installed:

1. `scrapy`: An open-source web crawling and scraping framework for Python.
2. `pandas`: A powerful library for data manipulation and analysis. It is used here to read the input CSV file in chunks.
3. `phonenumbers`: A Python library for parsing, formatting, and validating international phone numbers.
4. `re`: The built-in `re` module for regular expression operations, used for pattern matching.
5. `requests`: A Python library for making HTTP requests, which is used for searching companies on Google.
6. `beautifulsoup4` (bs4): A Python library for parsing HTML and XML documents. It is used here to extract information from web pages.
7. `email_validator`: A library for validating email addresses against RFC standards.
8. `fake_useragent`: A library to generate random user agents for making HTTP requests.
9. `googlesearch-python`: A Python library to perform Google searches programmatically.
10. `selenium`: A popular web automation library used here to interact with web pages and extract URLs.

## External Programs

In addition to the Python packages, you also need to install the following external program:

1. `chromedriver`: This is the WebDriver executable for Chrome. You need to download the appropriate version of `chromedriver` compatible with your Chrome browser version and specify its path in the script.

## Setting Up

1. Install the required Python packages using `pip`. Open a terminal or command prompt and run the following command:

```
pip install scrapy pandas phonenumbers requests beautifulsoup4 email_validator fake_useragent googlesearch-python selenium
```

2. Download the appropriate version of `chromedriver` from the official website: https://sites.google.com/a/chromium.org/chromedriver/downloads

3. Replace the placeholders in the `contact_info_scraper/spiders/exammple.py` with your specific file paths and adjust the settings as needed. Specifically, you need to replace:

   - `input_file`: Replace with the path to your input CSV file containing the list of companies (replace `""` with the actual path).
   - `output_file`: Replace with the path to your output CSV file where the contact information will be saved (replace `""` with the actual path).
   - `service = Service('')`: Replace `''` with the path to your `chromedriver` executable.

## Running the Spider

To run the Scrapy spider, use the following command:

```
scrapy crawl example
```

Make sure to run this command in the same directory where your Scrapy project is located, and the spider should be named `example` based on the provided code.

The spider will read the input CSV file in chunks, search for each company's official website on Google, and then scrape contact information from their "Contact Us" pages. The extracted information will be saved in the output CSV file.

Please note that web scraping should be done responsibly and respectfully. Ensure that you have the right to scrape the websites you are targeting, and consider adding appropriate delays between requests to avoid overloading the servers. Always refer to the website's robots.txt file or terms of service for guidance on scraping permissions.