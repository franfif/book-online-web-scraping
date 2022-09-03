# Extract prices from Books to Scrape

This project allows the user to scrape the website http://books.toscrape.com/ to get sale information about books.

It will create:

- a csv file per category listing the following information for each book in the category:
    - product_page_url
    - universal_product_code (upc)
    - title
    - price_including_tax
    - price_excluding_tax
    - number_available
    - product_description
    - category
    - review_rating
    - image_url
- a folder per category containing the image of each book of the category

Before using the application, please install all the packages as stated in [requirements.txt](requirements.txt)
From the terminal, use the command `pip install -r requirements.txt`.

To use the application, run `python3 scrape_book.py`.

Please note:

- This application only works for http://books.toscrape.com/
- Any change in the structure of the website by the owner might change the result of the application

