import csv
import pandas as pd
import phonenumbers
import re
import requests
import scrapy
import time

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from email_validator import validate_email, EmailNotValidError
from fake_useragent import UserAgent
from googlesearch import search
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from urllib.parse import urljoin


class ExampleSpider(scrapy.Spider):
    name = 'example'
    allowed_domains = []  # Add the allowed domains if needed

    def start_requests(self):
        ua = UserAgent(verify_ssl=False)
        input_file = ""  # Replace with the path to your input CSV file
        output_file = ""  # Replace with the path to your output CSV file
        chunk_size = 100  # Set the chunk size based on your system's memory capacity
        num_workers = 6   # Number of parallel workers, adjust based on your system's capacity

        # Read the CSV file in chunks
        chunks = pd.read_csv(input_file, chunksize=chunk_size)

        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            for results in executor.map(self.process_chunk, chunks):
                for result in results:
                    company_name = result['company_name']
                    non_promo_url = result['url']
                    if non_promo_url:
                        yield scrapy.Request(url=non_promo_url, callback=self.parse_contact_us, 
                                             meta={'company_name': company_name, 'non_promo_url': non_promo_url, 'output_file': output_file})


    def process_chunk(self, chunk):
        # Process the chunk and return the results
        results = []
        for company_name in chunk['Company Name']:
            non_promo_url = self.search_company_website(company_name)
            if non_promo_url:
                result = {'company_name': company_name, 'url': non_promo_url}
                results.append(result)
        return results


    def search_company_website(self, company_name):
        variations = [
            company_name,
            company_name + " website",
            company_name + " official website"
        ]

        # Configure Chrome options with headless mode
        options = Options()
        options.headless = True
        options.add_argument('--disable-gpu')
        # Add any other desired options here
        options.add_argument('--window-size=1920x1080')  # Set window size to avoid issues with headless mode

        # Set the executable_path using the Service class
        service = Service('')  # Replace with the path to your chromedriver executable
        service.start()

        try:
            driver = webdriver.Chrome(service=service, options=options)
            for query in variations:
                search_url = f'https://www.google.com/search?q={query}'
                driver.get(search_url)
                # Add a delay of a few seconds before processing the page
                time.sleep(2)
                # Extract the first search result link from the search page
                search_results = driver.find_elements('css selector', 'div.tF2Cxc')
                if search_results:
                    first_result = search_results[0]
                    link = first_result.find_element('css selector', 'a').get_attribute('href')
                    return link

        except Exception as e:
            print("Error:", e)
            # If an exception occurs, the driver won't be able to quit.
            # We can handle the error here, e.g., log the error or take some other action.
            print(f"Error occurred while searching for {company_name}. Skipping to the next company.")
        finally:
            driver.quit()
            service.stop()

        return None


    def parse_contact_us(self, response):
        company_name = response.meta['company_name']
        non_promo_url = response.meta['non_promo_url']
        output_file = response.meta['output_file']
        # Use BeautifulSoup to find the contact us link on the website
        soup = BeautifulSoup(response.text, 'html.parser')
        contact_link = soup.find('a', string=re.compile(r'contact', re.IGNORECASE))
        if not contact_link:
            self.logger.info(f"No contact link found for {company_name}")
            return

        # Extract the contact us URL and convert the relative URL to an absolute URL
        contact_us_url = urljoin(response.url, contact_link.get('href'))
        self.logger.info(f"Scraping contact info for {company_name} from {contact_us_url}")
        yield scrapy.Request(url=contact_us_url, callback=self.parse_contact_info, 
                             meta={'company_name': company_name, 'non_promo_url': non_promo_url, 'output_file': output_file})

    def parse_contact_info(self, response):
        company_name = response.meta['company_name']
        non_promo_url = response.meta['non_promo_url']
        output_file = response.meta['output_file']
        phone_numbers = self.extract_phone_numbers(response.text)
        email_addresses = self.extract_email_addresses(response.text)

        # Concatenate phone numbers and email addresses into a single string
        phone_numbers_str = ', '.join(phone_numbers)
        email_addresses_str = ', '.join(email_addresses)

        # Write contact information to the CSV file
        with open(output_file, mode='a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([company_name, non_promo_url, response.url, phone_numbers_str, email_addresses_str])


    def extract_phone_numbers(self, text):
        phone_numbers = set()
        # Use a more lenient regular expression to match different phone number formats
        matches = re.findall(r'(?<!\d)(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})(?!\d)', text)
        for match in matches:
            # Remove any non-digit characters from the match
            cleaned_number = re.sub(r'[^\d]', '', match)
            phone_numbers.add(cleaned_number)
        return phone_numbers


    def extract_email_addresses(self, text):
        email_addresses = set()
        matches = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', text)
        for match in matches:
            try:
                validated_email = validate_email(match)
                email_addresses.add(validated_email.email)
            except EmailNotValidError:
                pass
        return email_addresses
