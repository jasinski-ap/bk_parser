import re
import requests
from phonenumbers import parse as phone_parse
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
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
    # try 3 times if failed
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    # get request from url
    req = session.get(url)
    # req = requests.get(url, headers)
    # create bs soup by parsing request content
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
        # Some times adress has 2 sections which require to join
        if key == "Adres":
            # print(key)
            # address in section 1
            section1 = headers_data[index].get_text('\n')
            # address continues or phone number
            section2 = headers_data[index + 1].get_text('\n')
            # check section2 is phone number
            try:
                check_phone = phone_parse(
                    section2.strip().replace(' ', '').replace('-', '')
                )
            except Exception:
                check_phone = None
            # if not join sections and swich index
            if not check_phone:
                adres = headers_data[index].get_text('\n') + ' ' + headers_data[
                    index + 1].get_text('\n')
                # swicher for index
                index_plus = True
            else:
                adres = headers_data[index].get_text('\n')
            data_dict[key] = ' '.join(adres.strip().split())
            # print(data_dict['Adres'])
        elif key == "Nazwa i adres, data wpłynięcia oferty oraz jej cena":
            try:
                wykonawca = "Informacja o wybranym wykonawcy"
                data_dict[wykonawca] = headers_data[index].get_text('\n')
                data_dict[key] = headers_data[index + 1].get_text('\n')
            except IndexError:
                data_dict[key] = headers_data[index].get_text('\n')
        else:
            # swich index if address has 2 sections
            if index_plus:
                index += 1
            # add data to key
            data_dict[key] = headers_data[index].get_text('\n')
    # fix display of data
    data_dict['Numer ogłoszenia'] = ''.join(
        data_dict['Numer ogłoszenia'].strip().split()
    )
    # fix display of data
    data_dict['Termin składania ofert'] = ''.join(
        data_dict['Termin składania ofert'].strip().split()
    ).replace("do", "do ").replace("dnia", "dnia: ").replace('-', '.')

    # delete duble spaces in text
    for key, value in data_dict.items():
        data_dict[key] = re.sub(r'\n\s*\n', '\n\n', value)
    # return data dict
    return data_dict
