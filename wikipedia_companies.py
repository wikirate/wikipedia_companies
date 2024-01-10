import requests
from bs4 import BeautifulSoup
from decouple import config

def fetch_wikipedia_content(page_title):
    URL = f"https://en.wikipedia.org/wiki/{page_title}"
    response = requests.get(URL)
    if response.status_code == 200:
        return response.text
    return None

def extract_links_with_text(page_content, link_text):
    soup = BeautifulSoup(page_content, 'html.parser')
    links = soup.find_all('a', text=link_text)
    return [link['href'] for link in links]

def extract_official_website_links(wikipedia_urls, link_text_to_find):
    official_links_per_company = {}

    for company_url in wikipedia_urls:
        page_content = fetch_wikipedia_content(company_url)
        
        if page_content:
            official_links = extract_links_with_text(page_content, link_text_to_find)
            official_links_per_company[company_url] = official_links
        else:
            official_links_per_company[company_url] = []

    return official_links_per_company

from wikirate4py import API

api = API(config('API_KEY'))
companies = api.get_companies()

wikipedia_urls = [company.wikipedia_url for company in companies if company.wikipedia_url is not None]
link_text_to_find = "Official website"

official_links = extract_official_website_links(wikipedia_urls, link_text_to_find)

for company_url, links in official_links.items():
    print(f"Company: {company_url}")
    if links:
        print("Official Website Links:")
        for official_link in links:
            print(official_link)
    else:
        print(f"No official website links found with the link text '{link_text_to_find}'.")
