import requests
from bs4 import BeautifulSoup
from decouple import config
from wikirate4py import API


class WikipediaCompanyLinks:
    def __init__(self, api_key):
        self.api = API(api_key)

    def fetch_wikipedia_content(self, page_title):
        URL = f'https://en.wikipedia.org/wiki/{page_title}'
        response = requests.get(URL)
        if response.status_code == 200:
            return response.text
        return None

    def extract_links_with_text(self, page_content, link_text):
        soup = BeautifulSoup(page_content, 'html.parser')
        links = soup.find_all('a', text=link_text)
        return [link['href'] for link in links]

    def extract_official_website_links(self, wikipedia_urls, link_text_to_find):
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

    def get_official_website_links(self, link_text_to_find):
        companies = self.api.get_companies()
        wikipedia_urls = [{company.id: company.wikipedia_url} for company in companies if company.wikipedia_url is not None]

        official_links = self.extract_official_website_links(wikipedia_urls, link_text_to_find)

        return official_links

    def insert_official_company_pages(self, identifier, official_company_link):
        self.api.update_company(identifier, official_company_link=official_company_link)


api_key = config('API_KEY')
link_text_to_find = 'Official website'

company_links = WikipediaCompanyLinks(api_key)
official_links = company_links.get_official_website_links(link_text_to_find)

for company_identifier, links in official_links.items():
    if links:
        for official_link in links:
            company_links.insert_official_company_pages(company_identifier, official_link)
    else:
        print(f"No official website links found for company {company_identifier} with the link text '{link_text_to_find}'.")
