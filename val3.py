# %%
import requests
from settings import settings
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from tqdm import tqdm


def ret_station_name(station_name):
    apikey = settings['EKISPERT_KEY']
    station_url = 'https://api.ekispert.jp/v1/json/station'

    params = {'key': apikey,
              'name': station_name}

    res = requests.get(station_url, params=params).json()
    if type(res['ResultSet']['Point']) is list:
        ret_name = res['ResultSet']['Point'][0]['Station']['Name']
    else:
        ret_name = res['ResultSet']['Point']['Station']['Name']

    return ret_name


def ret_res_url(from_, to_):
    apikey = settings['EKISPERT_KEY']
    master_url = 'https://api.ekispert.jp/v1/json/search/course/light'

    params = {'key': apikey,
              'from': ret_station_name(from_),
              'to': ret_station_name(to_),
              'time': '0900',
              'searchType': 'arrival'}

    res = requests.get(master_url, params=params).json()
    ret_url = res['ResultSet']['ResourceURI']
    return ret_url


def calc_min_minute(url):
    res2 = requests.get(url)
    soup = BeautifulSoup(res2.text, "html.parser")
    table = soup.find('div', id='tabs_color')

    ret_lis = []
    elements = table.find_all('tr')

    for i in elements:
        candidate_list = i.find_all('p', class_="candidate_list_txt")

        required_time = candidate_list[0].find('span').text.split('（')[-1][:-1]

        hour = 0
        if '時間' in required_time:
            hour = int(required_time.split('時間')[0])
            t_minute = required_time.split('時間')[1][:-1]
            if t_minute == '':
                minute = 0
            else:
                minute = int(required_time.split('時間')[1][:-1])
        else:
            minute = int(required_time[:-1])

        required_time = hour*60 + minute
        transfer_count = int(candidate_list[1].find('span').text[:-1])

        ret_lis.append([transfer_count, required_time])

    ret_lis = np.array(ret_lis)
    min_trans = ret_lis[ret_lis[:, 0] == np.min(ret_lis[:, 0])]
    min_minute = min_trans[min_trans[:, 1] == np.min(min_trans[:, 1])][0]

    return min_minute


def ret_min_minute(from_, to_):
    to_station = ret_station_name(to_)
    from_station = ret_station_name(from_)
    min_minute = calc_min_minute(ret_res_url(from_station,
                                             to_station))

    return min_minute


# %%
to_stations = ['六本木', '六本木一丁目', '乃木坂', '赤坂']
from_stations = pd.read_csv('staion_price.csv')['station']
# %%
to_ = to_stations[0]
from_ = from_stations[0]

min_minute = ret_min_minute(from_, to_)
# %%
pd.read_csv('from_to_min.csv')
# %%
for i in to_stations:
    for j in tqdm(from_stations):
        min_minute = ret_min_minute(j, i)
