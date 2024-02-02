import requests
import wikirate4py
from bs4 import BeautifulSoup
from decouple import config
from wikirate4py import API
from typing import Dict, List, Optional


LINK_TEXT_TO_FIND = "Official website"
class WikipediaCompanyLinks:
    """
    Class to handle fetching and processing official company websites from
    Wikipedia.
    """

    def __init__(self, api_key: str):
        """
        Initialize the class with an API key. URL, user, and password are optionally 
        read from environment variables.

        Args:
            api_key (str): The API key for authentication.
        """
        url = config("URL", default=None)
        user = config("USER", default=None)
        password = config("PASSWORD", default=None)

        if url and user and password:
            self.api = API(api_key, wikirate_api_url=url, auth=(user, password))
        else:
            self.api = API(api_key)


    def fetch_wikipedia_content(self, page_title: str) -> Optional[str]:
        """
        Fetch the content of a Wikipedia page given its title.

        Args:
            page_title (str): The title of the Wikipedia page.

        Returns:
            Optional[str]: The content of the Wikipedia page, or None if the
            request fails.
        """
        URL = f"https://en.wikipedia.org/wiki/{page_title}"
        response = requests.get(URL)
        if response.status_code == 200:
            return response.text
        return None

    def extract_links_with_text(self, page_content: str, link_text: str) -> List[str]:
        """
        Extract all links from the given page content that contain the
        specified link text.

        Args:
            page_content (str): The HTML content of the page.
            link_text (str): The text to match in the link"s anchor text.

        Returns:
            List[str]: A list of URLs that contain the specified link text.
        """
        soup = BeautifulSoup(page_content, "html.parser")
        links = soup.find_all("a", text=link_text)
        return [link["href"] for link in links]

    def extract_official_website_links(self, wikipedia_urls: List[Dict[str, str]], link_text_to_find: str) -> Dict[str, List[str]]:
        """
        Extract official website links for each company from Wikipedia URLs.

        Args:
            wikipedia_urls (List[Dict[str, str]]): A list of dictionaries
            containing company identifiers and corresponding Wikipedia URLs.
            link_text_to_find (str): The text to search for in link anchors to
            find official websites.

        Returns:
            Dict[str, List[str]]: A dictionary where each key is a company
            identifier and the value is a list of official website URLs.
        """
        official_links_per_company = {}

        for company_dict in wikipedia_urls:
            for identifier, page_title in company_dict.items():
                page_content = self.fetch_wikipedia_content(page_title)

                if page_content:
                    official_links = self.extract_links_with_text(page_content, link_text_to_find)
                    official_links_per_company[identifier] = official_links
                else:
                    official_links_per_company[identifier] = []

        return official_links_per_company

    def get_official_website_links(self, link_text_to_find: str) -> Dict[str, List[str]]:
        """
        Get official website links for companies.

        Args:
            link_text_to_find (str): The text to match in the link"s anchor
            text to find official websites.

        Returns:
            Dict[str, List[str]]: A dictionary where each key is a company
            identifier and the value is a list of official website URLs.
        """
        # cursor = wikirate4py.Cursor(self.api.get_companies, per_page=100)
        # companies = []
        # while cursor.has_next():
        #     companies += cursor.next()

        offset = 0
        while offset <= 1000:
            companies = self.api.get_companies(offset=offset)
            offset += 20
            wikipedia_urls = [{company.id: company.wikipedia_url} for company in companies if company.wikipedia_url is not None]
            official_links = self.extract_official_website_links(wikipedia_urls, link_text_to_find)
        return official_links

    def insert_official_company_pages(self, identifier: str, official_company_link: str):
        """
        Insert official company pages into wikirate.

        Args:
            identifier (str): The identifier of the company.
            official_company_link (str): The official website link of the
            company.
        """
        self.api.update_company(identifier, website=official_company_link)


company_links = WikipediaCompanyLinks(config("API_KEY"))
official_links = company_links.get_official_website_links(LINK_TEXT_TO_FIND)
# Format to manually test specific company:
# official_links = {8994: ['https://about.google']}

for company_identifier, links in official_links.items():
    if links:
        for official_link in links:
            company_links.insert_official_company_pages(company_identifier, official_link)
    else:
        print(f"No official website links found for company {company_identifier}\
              with the link text '{LINK_TEXT_TO_FIND}'.")
