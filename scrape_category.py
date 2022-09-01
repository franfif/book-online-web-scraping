import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

url = 'http://books.toscrape.com/catalogue/category/books/mystery_3/index.html'

parsed_url = urlparse(url)
root_url = parsed_url.scheme + '://' + parsed_url.netloc

page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')

books = soup.select('.product_pod>div>a')
for book in books:
    book_url = book.attrs.get('href')
    book_url = book_url.replace('../../..', root_url + '/catalogue')
    print(book_url)
