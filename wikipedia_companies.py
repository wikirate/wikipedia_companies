# Two approaches to find the Official Website link from Wikipedia:
# 1. Wikipedia API call -> list of external extract_links_with_text
# This approach needs further processing to extract the actual official website
# Returns a list of external links

import requests

S = requests.Session()

URL = "https://en.wikipedia.org/w/api.php"

PARAMS = {
    "action": "query",
    "titles": "Google",
    "prop": "extlinks",
    "format": "json"
}

R = S.get(url=URL, params=PARAMS)
DATA = R.json()

print(DATA)

# 2. This approach scrapes the Wikipedia company page and returns the Official website.
# The drawback is that the Company name should be a pretty good match. 
# For example 'Apple' refers to the yummy fruit.

from bs4 import BeautifulSoup

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

company_name = "Apple Inc"
link_text_to_find = "Official website"

page_content = fetch_wikipedia_content(company_name)
if page_content:
    official_links = extract_links_with_text(page_content, link_text_to_find)

    if official_links:
        print("Official Website Links:")
        for official_link in official_links:
            print(official_link)
    else:
        print(f"No official website links found with the link text '{link_text_to_find}'.")
else:
    print(f"Failed to fetch Wikipedia content for '{company_name}'.")
