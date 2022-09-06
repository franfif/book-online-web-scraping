import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.request import urlretrieve
import os
import re
from slugify import slugify
import csv
import helper_table as tab
import helper_number as num


def scrape_page(url, image_path, csvfile):
    """
    Reads a product page, writes metadata into cvs and download images
    :param url: str, url to a book page
    :param image_path: str, relative path to place the images downloaded
    :param csvfile: str, path and name of csv where metadata are written
    :return: nothing
    """
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
    # change relative img src to absolute url
    image_url = urljoin(url, soup.img['src'])

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

    # create image file name
    image_file_name = slugify(title) + '.' + image_url.rsplit('.')[-1]
    # download image
    urlretrieve(image_url, image_path + image_file_name)


def write_book_data(list_of_data, csvfile):
    """
    Takes a list of metadata and append it to a csv file
    :param list_of_data: list, metadata of a product
    :param csvfile: str, path and name of csv where data are written
    :return: nothing
    """
    with open(csvfile, 'a', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(list_of_data)


def scrape_category(url, category):
    """
    Gets links from a category and scrape each book of the category
    :param url: str, url to a book category
    :param category: str, name of the category
    :return: nothing
    """

    def get_books_urls(category_url, books_urls):
        """
        Gathers all books in category page recursively, returns list of urls
        :param category_url: str, url of the category
        :param books_urls: list(str), accumulator of book urls
        :return: list(str), list of book urls
        """
        page = requests.get(category_url)
        soup = BeautifulSoup(page.content, 'html.parser')
        new_books_urls = soup.select('.product_pod>div>a')

        def join_url(book):
            """
            Extracts href from soup selection, returns absolute url using category_url
            :param book: soup object, contains a relative url under href
            :return: str, absolute url combining category_url and book url
            """
            return urljoin(category_url, book.attrs.get('href'))

        new_books_urls = list(map(join_url, new_books_urls))
        books_urls = books_urls + new_books_urls
        # check for next page and call get_books_urls recursively
        next_page = soup.select_one('.next a')
        if next_page:
            next_url = urljoin(category_url, next_page['href'])
            return get_books_urls(next_url, books_urls)
        else:
            return books_urls

    # create headers for csv files
    headers = [
        'product_page_url',
        'universal_product_code',
        'title',
        'price_including_tax',
        'price_excluding_tax',
        'number_available',
        'product_description',
        'category',
        'review_rating',
        'image_url'
    ]
    # create directory for website if it does not exist
    cat_path = 'books_toscrape/'
    if not os.path.exists(cat_path):
        os.mkdir(cat_path)
    # create csv file for the category
    category_csv = cat_path + category + '.csv'
    # create dir for images if it does not exist
    image_path = 'books_toscrape/' + category + '_images/'
    if not os.path.exists(image_path):
        os.mkdir(image_path)
    # add headers to category csv file
    with open(category_csv, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(headers)

    # call scrape_page() for each book in the category
    for book_url in get_books_urls(url, []):
        scrape_page(book_url, image_path, category_csv)


def scrape_website():
    """
    Gets links for each category and scrape each of them
    :return: nothing
    """
    url = 'http://books.toscrape.com'

    def get_categories(root_url):
        """
        Gets categories from the entire website
        :param root_url: url of the website
        :return: dictionary, pairs of each category and its url
        """
        page = requests.get(root_url)
        soup = BeautifulSoup(page.content, 'html.parser')
        # stock category names and urls in a dictionary
        categories = {}
        for cat in soup.select('.side_categories ul ul li a'):
            key = cat.string.strip()
            value = urljoin(root_url, cat.attrs.get('href'))
            categories[key] = value
        return categories

    # call scrape_category() for each category in the website
    for cat_name, cat_url in get_categories(url).items():
        scrape_category(cat_url, cat_name)
        # progression information
        print(cat_name + ' is done')
    # progression information
    print("You're all set!")


scrape_website()
