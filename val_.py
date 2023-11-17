# %%
import requests
from settings import settings
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from tqdm import tqdm
# %%


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


def ret_min_minute(url):
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
# %%


stations = pd.read_csv('from_to_min.csv')
stations = stations[stations['4'] < 100].reset_index(drop=True)
ret_df = pd.DataFrame({})
#%%
to_list = ['八丁堀',
           '京橋',
           '東京',
           '日本橋',
           '茅場町',
           '銀座一丁目',
           '新富町']
# %%
for to_ in to_list:
    for j in tqdm(range(len(stations))):
        try:
            line = stations.iloc[j][0]
            from_ = stations.iloc[j][1]

            ret_url = ret_res_url(from_, to_)

            min_minute = ret_min_minute(ret_url)

            temp_df = pd.DataFrame([[line, from_, to_,
                                     min_minute[0], min_minute[1]]])

            ret_df = pd.concat([ret_df, temp_df], axis=0)

            ret_df = ret_df.reset_index(drop=True)
            ret_df.columns = ['line', 'from', 'to', 'trans', 'req_min']

            ret_df.to_csv('from_to_min.csv', index=False)
        except Exception as e:
            print('some error')
            print(e)

# %%
