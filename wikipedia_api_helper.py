import requests

S = requests.Session()

URL = 'https://en.wikipedia.org/w/api.php'

PARAMS = {
    'action': 'query',
    'titles': 'Google',
    'prop': 'extlinks',
    'format': 'json'
}

R = S.get(url=URL, params=PARAMS)
DATA = R.json()

print(DATA)