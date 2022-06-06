import requests, json
from bs4 import BeautifulSoup as bs
import time
from random import randint, choice
import csv

page_url = 'PUT_THE_LINK_HERE'
page_list = [f'{page_url}/{x}_p/' for x in range(1,21)]
links_list = set()

user_agent_list = [
    {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Referer':'https://www.yandex.ru/',
    'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 10_0 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 YaBrowser/17.4.3.195.10 Mobile/14A346 Safari/E7FBAF'
    }]

session = requests.Session()


def get_page(url:str) -> str:
    """Getting html code from url for further processing"""
    headers = choice(user_agent_list)
    try:
        html = session.get(url, headers=headers, timeout=15)
        html.raise_for_status()
        return html.text
    except(requests.RequestException, ValueError):
        print(f'{url} parse error, skipping...')
        return None


def get_page_links(html:str):
    """Collecting lings to house pages"""
    soup = bs(html, 'lxml')
    links = soup.find_all('script', type="application/ld+json")
    for i in links:
        if len(links_list) < 100:
            try:
                link = json.loads(i.text)['url']
                if 'community' in link:
                    continue
                links_list.add(link)
            except KeyError:
                continue


def get_house_list(html:str) -> dict:
    """Collecting house data"""
    house_dict = {
    'Street Address':None,
    'City':None,
    'State':None,
    'ZIP':None,
    'Sq Ft':None,
    'Year Built':None,
    'Bed':None,
    'Bath':None
    }
    soup = bs(html, 'lxml')
    if "Capcha" in soup.text:
        print('captcha')

    data_list = soup.find('div', class_='ds-home-details-chip')

    bd_bth_sqft = data_list.find_all('span', class_='hdp__sc-rfpg3m-0 bqcSTm')
    bd_bth_sqft_text = [x.text for x in bd_bth_sqft]
    
    for param in bd_bth_sqft_text:
        if 'bd' in param:
            house_dict['Bed'] = param.replace(' bd','')
        elif 'ba' in param:
            house_dict['Bath'] = param.replace(' ba','')
        elif param.split()[-1] in ['sqft', 'Feet', 'Acres']:
            house_dict['Sq Ft'] = param

    address = soup.find('h1', id='ds-chip-property-address').text
    house_dict['Street Address'] = address.split(',')[0]
    house_dict['City'] = address.split(',')[1].strip()
    house_dict['State'] = address.split(' ')[-2]
    house_dict['ZIP'] = address.split(' ')[-1]

    year_list = soup.find('ul', class_='zsg-tooltip-viewport').find_all('li',class_='dpf__sc-2arhs5-0 ecJCxh')
    try:
        house_dict['Year Built'] = [x.find_all('span')[1].text for x in year_list if 'Built' in x.find_all('span')[1].text][0]
    except IndexError:
        house_dict['Year Built'] = None

    return house_dict


if __name__ == '__main__':
    for page in page_list:
        time.sleep(randint(11, 21))
        print(f'I have {len(links_list)} rn, grabbing {page}...')
        get_page_links(get_page(page))
        if len(links_list) >= 100:
            break
    with open('links.txt', 'w', encoding='utf-8') as f:
        for line in links_list:
            f.writelines(line+'\n')

    with open('links.txt', 'r', encoding="utf-8") as links_file:
        lines = links_file.readlines()[:]
        houses = []
        counter = 1
        with open ('houses.csv', 'a', encoding='utf-8', newline='') as target_file:
            fields = ['Street Address', 'City', 'State', 'ZIP', 'Sq Ft', 'Year Built', 'Bed', 'Bath']
            writer = csv.DictWriter(target_file, fields, delimiter = ';')
            writer.writeheader()
            for line in lines:
                if line:
                    print('sleeping...')
                    time.sleep(randint(24, 44))
                    print('sleeping done!')
                    current_line = get_house_list(get_page(line.strip('\n')))
                    try:
                        writer.writerow(current_line)
                        print(f'link -> dict {counter}')
                        counter += 1
                    except ValueError:
                        continue