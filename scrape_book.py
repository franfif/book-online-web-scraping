import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re
import csv
import helper_table as tab
import helper_number as num


def scrape_page(url, csvfile):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # product_page_url
    product_page_url = url
    # universal_ product_code (upc)
    universal_product_code = tab.get_value_from_table(soup, 'UPC')
    # title
    title = soup.h1.string
    # price_including_tax
    price_including_tax = tab.get_value_from_table(soup, 'Price (incl. tax)')
    # price_excluding_tax
    price_excluding_tax = tab.get_value_from_table(soup, 'Price (excl. tax)')
    # number_available
    text_available = tab.get_value_from_table(soup, 'Availability')
    number_available = re.findall('[0-9]+', text_available)[0]
    # product_description
    try:
        product_description = soup.select('#product_description ~ p')[0].string
    except:
        product_description = "No Description"
    # category
    category = soup.select('.breadcrumb li a')[2].string
    # review_rating
    review_rating = soup.find(class_='star-rating').attrs.get('class')[1]
    review_rating = num.word_to_number(review_rating)
    # image_url
    image_url = soup.img['src']
    # prepare url to correct the image urls
    parsed_url = urlparse(url)
    root_url = parsed_url.scheme + '://' + parsed_url.netloc
    image_url = image_url.replace('../..', root_url)

    # combine metadata in a list
    page_content = [
        product_page_url,
        universal_product_code,
        title,
        price_including_tax,
        price_excluding_tax,
        number_available,
        product_description,
        category,
        review_rating,
        image_url
    ]

    # write data in csv file
    write_book_data(page_content, csvfile)


# take a list of metadata and append it to a csv file
def write_book_data(list_of_data, csvfile):
    with open(csvfile, 'a', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(list_of_data)


# get links from a category and scrape each book of the category
def scrape_category():
    url = 'http://books.toscrape.com/catalogue/category/books/mystery_3/index.html'

    # gather all books in category page, return list of urls
    def get_books_urls(page_url, books_urls):
        page = requests.get(page_url)
        soup = BeautifulSoup(page.content, 'html.parser')
        new_books_urls = soup.select('.product_pod>div>a')

        # extract href from soup selection and join them to page_url
        def join_url(book):
            return urljoin(page_url, book.attrs.get('href'))

        new_books_urls = list(map(join_url, new_books_urls))
        books_urls = books_urls + new_books_urls
        # check for next page and call get_books_urls recursively
        next_page = soup.select_one('.next a')
        if next_page:
            next_url = urljoin(page_url, next_page['href'])
            return get_books_urls(next_url, books_urls)
        else:
            return books_urls

    for book_url in get_books_urls(url, []):
        scrape_page(book_url, 'data_category.csv')


scrape_category()
