def get_value_from_table(soup, header):
    return list(filter(lambda x: x.select_one('th').string == header,
                       soup.select('table tr')))[0].select_one('td').string
