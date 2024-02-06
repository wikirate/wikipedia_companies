from typing import Dict, List, Optional
import datetime
import requests
from bs4 import BeautifulSoup
from decouple import config
from wikirate4py import API

LINK_TEXT_TO_FIND = "Official website"
DATETIME_NOW = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
LOG_FILE_PATH = f"company_links_log_{DATETIME_NOW}.txt'"


class WikipediaCompanyLinks:
    """
        Initialize the WikipediaCompanyLinks class with API credentials.

        Args:
            api_key (str): API key for authentication with the WikiRate API.
    """
    def __init__(self, api_key: str):
        url = config('URL', default=None)
        user = config('USER', default=None)
        password = config('PASSWORD', default=None)
        if url and user and password:
            self.api = API(
                api_key,
                wikirate_api_url=url,
                auth=(user, password))
        else:
            self.api = API(api_key)
        self.log_file = (
            f"company_links_log_{DATETIME_NOW}.txt"
        )

    def log_info(self, message: str):
        """
        Log a message to the log file.

        Args:
            message (str): The message to be logged.
        """
        with open(self.log_file, 'a', encoding='utf-8') as file:
            file.write(f"{message}\n")

    def fetch_wikipedia_content(self, page_title: str) -> Optional[str]:
        """
        Fetch the HTML content of a Wikipedia page.

        Args:
            page_title (str): The title of the Wikipedia page to fetch.

        Returns:
            Optional[str]: The HTML content of the page, or
            None if the request fails.
        """
        URL = f"https://en.wikipedia.org/wiki/{page_title}"
        response = requests.get(URL, timeout=10)
        if response.status_code == 200:
            return response.text
        return None

    def extract_links_with_text(
            self,
            page_content: str,
            link_text: str
            ) -> List[str]:
        """
        Extract all links from a Wikipedia page that contain the specified
        link text.

        Args:
            page_content (str): The HTML content of the Wikipedia page.
            link_text (str): The text to search for within link anchors.

        Returns:
            List[str]: A list of URLs found that contain the specified
            link text.
        """
        soup = BeautifulSoup(page_content, "html.parser")
        links = soup.find_all("a", string=link_text)
        return [link.get('href') for link in links if link.get('href')]

    def extract_official_website_links(self,
                                       wikipedia_urls: List[Dict[str, str]],
                                       link_text_to_find: str
                                       ) -> Dict[str, List[str]]:
        """
        Extract official website links for each company from their
        Wikipedia URLs.

        Args:
            wikipedia_urls (List[Dict[str, str]]): A list of dictionaries
            containing company identifiers and their corresponding Wikipedia
            URLs.
            link_text_to_find (str): The text to search for in link anchors to
            find official websites.

        Returns:
            Dict[str, List[str]]: A dictionary mapping company identifiers to
            lists of official website URLs.
        """
        official_links_per_company = {}
        for company_dict in wikipedia_urls:
            identifier, page_title = next(iter(company_dict.items()))
            page_content = self.fetch_wikipedia_content(page_title)
            if page_content:
                official_links = self.extract_links_with_text(
                    page_content,
                    link_text_to_find
                    )
                official_links_per_company[identifier] = official_links
            else:
                official_links_per_company[identifier] = []
                self.log_info(
                    f"No Wikipedia page found for company ID {identifier}"
                    )
        return official_links_per_company

    def insert_official_company_pages(self,
                                      identifier: str,
                                      official_company_link: str
                                      ):
        """
        Insert an official company page into Wikirate.

        Args:
            identifier (str): The identifier of the company.
            official_company_link (str): The official website link of the
            company.
        """
        try:
            self.api.update_company(identifier, website=official_company_link)
            self.log_info(
                f"Successfully updated company ID {identifier} \
                with link {official_company_link}"
                )
        except Exception as e:
            self.log_info(
                f"Failed to update company ID {identifier} with link \
                {official_company_link}: {e}"
                )

    def get_and_insert_official_website_links(self):
        """
        Fetches companies in batches and processes each to find and insert
        their official website links on Wikipedia.

        If a compnay is linked to a Wikipedie entry it attempts to find
        the official website link by scraping the company's Wikipedia page.
        If successful, the official website link is updated in WikiRate.
        It logs the progress and results of these operations,
        including successes and failures.

        The method continues fetching and processing companies in batches
        until all companies have been processed.
        """
        batch_size = 100
        offset = 0
        while True:
            companies = self.api.get_companies(limit=batch_size, offset=offset)
            self.log_info(f"Processing batch starting from offset {offset}.")

            if not companies:
                break

            wikipedia_urls = [{company.id: company.wikipedia_url} for company in companies if company.wikipedia_url]  # noqa: E501
            official_links_per_company = self.extract_official_website_links(
                wikipedia_urls,
                LINK_TEXT_TO_FIND
                )

            for company_id, links in official_links_per_company.items():
                if links:
                    for link in links:
                        self.insert_official_company_pages(company_id, link)
                else:
                    self.log_info(
                        f"No official website links found for company ID \
                        {company_id}"
                        )

            offset += batch_size

    @staticmethod
    def extract_company_ids_from_log(log_file_path):
        """
        Extract and save company IDs from the log file based on
        update success or failure.

        Args:
            log_file_path (str): The path to the log file.
        """
        updated_company_ids = []
        no_link_company_ids = []

        with open(log_file_path, 'r', encoding='utf-8') as log_file:
            for line in log_file:
                if "Successfully updated company ID" in line:
                    start = line.find("ID") + 3
                    end = line.find("with link") - 1
                    company_id = line[start:end]
                    updated_company_ids.append(company_id)
                elif "No official website links found for company ID" in line:
                    start = line.rfind("ID") + 3
                    company_id = line[start:].strip()
                    no_link_company_ids.append(company_id)

        with open(
            f"updated_company_ids{DATETIME_NOW}.txt",
            encoding='utf-8'
        ) as file:
            for company_id in updated_company_ids:
                file.write(f"{id}\n")

        with open(
            f"no_link_company_ids{DATETIME_NOW}.txt",
            "w",
            encoding='utf-8'
        ) as file:
            for company_id in no_link_company_ids:
                file.write(f"{id}\n")

        print("Company IDs extracted and saved to files.")


wikipedia_company_links = WikipediaCompanyLinks(config("API_KEY"))
wikipedia_company_links.get_and_insert_official_website_links()
wikipedia_company_links.extract_company_ids_from_log(LOG_FILE_PATH)
