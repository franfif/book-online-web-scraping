def get_value_from_table(soup, header):
    rows = soup.select('table tr')
    for row in rows:
        if row.select_one('th').string == header:
            return row.select_one('td').string
