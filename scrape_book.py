from urllib.parse import urljoin
import os
import re
from helper_soup import get_soup
from helper_table import get_value_from_table
from helper_number import word_to_number
from helper_write_csv import write_row
from helper_image import download_image


def scrape_page(url, image_path, csvfile):
    """
    Reads a product page, writes metadata into cvs and download images
    :param url: str, url to a book page
    :param image_path: str, relative path to place the images downloaded
    :param csvfile: str, path and name of csv where metadata are written
    :return: nothing
    """
    soup = get_soup(url)

    # product_page_url
    product_page_url = url
    # universal_ product_code (upc)
    universal_product_code = get_value_from_table(soup, 'UPC')
    # title
    title = soup.h1.string
    # price_including_tax
    price_including_tax = get_value_from_table(soup, 'Price (incl. tax)')
    # price_excluding_tax
    price_excluding_tax = get_value_from_table(soup, 'Price (excl. tax)')
    # number_available
    text_available = get_value_from_table(soup, 'Availability')
    number_available = re.findall('[0-9]+', text_available)[0]
    # product_description
    product_description = soup.select('#product_description ~ p')
    if len(product_description) > 0:
        product_description = product_description[0].string
    else:
        product_description = "No Description"
    # category
    category = soup.select('.breadcrumb li a')[2].string
    # review_rating
    review_rating = soup.find(class_='star-rating').attrs.get('class')[1]
    review_rating = word_to_number(review_rating)
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
    write_row(page_content, csvfile)
    # download the book's image
    download_image(image_url, title, image_path)


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
        soup = get_soup(category_url)
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
    write_row(headers, category_csv)

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
        soup = get_soup(root_url)
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
