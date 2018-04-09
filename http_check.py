import requests
from bs4 import BeautifulSoup


def hit_site(url):
    print(url)
    r = requests.get(url, stream=True)
    print('HEADER' + r.headers)
    print('ENCODE' + r.encoding)
    print('STATUS' + r.status_code)
    # print(r.json())
    print("---------")
    print(r)
    print("HEADER")
    print(r.request.headers)
    # print(r.response.headers)
    for line in r.iter_lines():
        print(line)
        data = r.text
        soup = BeautifulSoup(data, "html.parser")
        return soup

hit_site("http://www.google.com")
