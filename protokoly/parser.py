import re
import requests
from bs4 import BeautifulSoup

# define url
# url = "https://bazakonkurencyjnosci.funduszeeuropejskie.gov.pl/publication/view/1241478"


def bk_dict_from_url(url):
    # Set headers
    headers = requests.utils.default_headers()
    headers.update(
        {
            'User-Agent':
                'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
        }
    )
    # get data from url
    req = requests.get(url, headers)
    # create bs soup
    soup = BeautifulSoup(req.content, 'html.parser')
    # dicionary containing sections as keys and section text as values
    data_dict = {}
    # find top panel div
    div_panel = soup.find("div", class_="panel-body")
    # find title
    site_title = div_panel.find(class_='title-site')
    # add title to data
    data_dict['site-title'] = site_title.text
    # find data publikacji
    data_publikacji = div_panel.find(text=re.compile('Data publikacji'))
    # add data publikacji to data dict
    data_dict['Data publikacji'] = data_publikacji.replace(
        'Data publikacji:', ''
    ).strip()
    # print('div_container: ', div_container)
    # FInd site header text
    text_informacje = soup.find(
        text="Informacje o ogłoszeniu", class_="plain-text"
    )
    # get data container div from header text
    div_data = text_informacje.find_parent('div')
    # retrive all headers by h3
    headers = div_data.find_all('h3')
    # retrive all data by div class
    headers_data = div_data.find_all('div', class_="under-space gray-row")
    # merge 2 first rows and add them to data dict
    data_dict[headers[0].text.strip()] = ' '.join(
        headers[1].get_text().strip().strip()
    )
    data_dict[headers[2].text.strip()] = ' '.join(headers[3].get_text().strip())
    # iterate over other data
    # for addres is nessesery additionall processsing
    index_plus = False
    for index, header in enumerate(headers[4:]):
        key = header.text
        key = key.strip()
        if key == "Adres":
            # print(key)
            adres = headers_data[index].get_text('\n') + ' ' + headers_data[
                index + 1].get_text('\n')
            data_dict[key] = ' '.join(adres.strip().split())
            index_plus = True
            # print(data_dict['Adres'])
        else:
            if index_plus:
                index += 1
            data_dict[key] = headers_data[index].get_text('\n')
    # fix some data
    data_dict['Numer ogłoszenia'] = ''.join(
        data_dict['Numer ogłoszenia'].strip().split()
    )
    data_dict['Termin składania ofert'] = ''.join(
        data_dict['Termin składania ofert'].strip().split()
    ).replace("do", "do ").replace("dnia", "dnia: ")

    for key, value in data_dict.items():
        data_dict[key] = re.sub(r'\n\s*\n', '\n\n', value)
    # return data dict
    return data_dict
