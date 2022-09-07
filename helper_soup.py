from bs4 import BeautifulSoup
from helper_requests import get_page


def get_soup(url):
    return BeautifulSoup(get_page(url).content, 'html.parser')
