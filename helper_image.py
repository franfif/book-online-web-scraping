from slugify import slugify
from urllib.request import urlretrieve


def download_image(url, title, folder):
    """
    Downloads an image from its url and saves it in the specified folder.
    Changes the name of the file with a slugified title
    :param url: str, url of the image
    :param title: str, title of the book associated to the image
    :param folder: str, destination path for the downloaded file
    :return: nothing, saves the image in the specified relative folder
    """
    # create image file name
    image_file_name = slugify(title) + '.' + url.rsplit('.')[-1]
    # download image
    urlretrieve(url, folder + image_file_name)
