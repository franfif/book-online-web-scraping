import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import csv
import helper_table as tab
import helper_number as num

url = "http://books.toscrape.com/catalogue/i-had-a-nice-time-and-other-lies-how-to-find-love-sht-like-that_814/index" \
      ".html"
parsed_url = urlparse(url)
root_url = parsed_url.scheme + '://' + parsed_url.netloc

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
product_description = soup.select('#product_description ~ p')[0].string
# category
category = soup.select('.breadcrumb li a')[2].string
# review_rating
review_rating = soup.find(class_='star-rating').attrs.get('class')[1]
review_rating = num.word_to_number(review_rating)
# image_url
image_url = soup.img['src']
image_url = image_url.replace('../..', root_url)

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

print(page_content)

with open('data.csv', 'a', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(page_content)
