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
    try:
        if type(res['ResultSet']['Point']) is list:
            ret_name = res['ResultSet']['Point'][0]['Station']['Name']
        else:
            ret_name = res['ResultSet']['Point']['Station']['Name']

        return ret_name
    except KeyError:
        return False


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

    try:
        ret_lis = []
        elements = table.find_all('tr')

        for i in elements:
            candidate_list = i.find_all('p', class_="candidate_list_txt")

            required_time = candidate_list[0].find(
                'span').text.split('（')[-1][:-1]

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

    except AttributeError:
        return False


def ret_min_minute(from_, to_):
    to_station = ret_station_name(to_)
    from_station = ret_station_name(from_)

    if to_station is False or from_station is False:
        return False
    else:
        min_minute = calc_min_minute(ret_res_url(from_station,
                                                 to_station))

        if min_minute is False:
            return False
        else:
            return min_minute


# %%
to_stations = ['渋谷']
staion_price = pd.read_csv('csv/staion_price_2ldk.csv')
pre_df = pd.read_csv('csv/to_shibuya/trans_min_price_2ldk.csv')
# %%
data_list = []
for to_ in to_stations:
    for j in tqdm(range(len(staion_price))):
        from_ = staion_price.iloc[j]['station']
        line = staion_price.iloc[j]['line']
        price = staion_price.iloc[j]['price']

        condition01 = pre_df['line'] == line
        condition02 = pre_df['price'] == price
        condition03 = pre_df['from'] == from_
        condition04 = pre_df['to'] == to_

        if np.sum(condition01*condition02*condition03*condition04) == 0:
            min_minute = ret_min_minute(from_, to_)

            if min_minute is False:
                pass
            else:
                data_list.append(
                    [line, price, from_, to_, min_minute[0], min_minute[1]])

        if j % 100 == 0:
            temp_df = pd.DataFrame(data_list,
                                   columns=['line', 'price', 'from', 'to', 'trans', 'min'])
            pd.concat([pre_df, temp_df]).reset_index(
                drop=True).to_csv('csv/to_shibuya/trans_min_price_2ldk.csv', index=False)
# %%
walk_min = {'六本木': 7,
            '六本木一丁目': 17,
            '乃木坂': 7,
            '赤坂': 14}

walk_min_lis = []
for i in pre_df['to']:
    walk_min_lis.append(walk_min[i])

walk_min_lis = np.array(walk_min_lis) + np.array(pre_df['min'])
walk_df = pd.DataFrame(walk_min_lis, columns=['train+walk_min'])
# %%
pd.concat([pre_df, walk_df], axis=1).to_csv(
    'csv/to_roppongi/trans_min_price.csv', index=False)
# %%
temp_df = pd.DataFrame(data_list,
                       columns=['line', 'price', 'from', 'to', 'trans', 'min'])
pd.concat([pre_df, temp_df]).reset_index(
    drop=True).to_csv('csv/to_shibuya/trans_min_price_2ldk.csv', index=False)

# %%
