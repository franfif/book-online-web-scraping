import csv


def write_row(data, csvfile):
    """
    Takes a list of metadata and append it to a csv file
    :param data: list, metadata of a product
    :param csvfile: str, path and name of csv where data are written
    :return: nothing
    """
    with open(csvfile, 'a', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(data)
