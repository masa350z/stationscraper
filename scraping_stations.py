#%%
import requests
import json
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import time
# %%
url = 'https://www.traveltowns.jp/railwaylines/kanto/'
res = requests.get(url)
ret_df = pd.DataFrame({})
soup = BeautifulSoup(res.text, "html.parser")
# %%
tables = soup.find_all('table')
jr_west_table = tables[1]
shitetsu_table = tables[2]
subway_table = tables[3]
local_table = tables[4]

jr_west_links = jr_west_table.find_all('a')
shitetsu_links = shitetsu_table.find_all('a')
subway_links = subway_table.find_all('a')
local_links = local_table.find_all('a')
# %%
for i in range(len(jr_west_links)):
    url = 'https://www.traveltowns.jp' + jr_west_links[i]['href']
    line = jr_west_links[i].text
    temp_df = pd.DataFrame([[url, line]])
    ret_df = pd.concat([ret_df, temp_df])

for i in range(len(shitetsu_links)):
    url = 'https://www.traveltowns.jp' + shitetsu_links[i]['href']
    line = shitetsu_links[i].text
    temp_df = pd.DataFrame([[url, line]])
    ret_df = pd.concat([ret_df, temp_df])

for i in range(len(subway_links)):
    url = 'https://www.traveltowns.jp' + subway_links[i]['href']
    line = subway_links[i].text
    temp_df = pd.DataFrame([[url, line]])
    ret_df = pd.concat([ret_df, temp_df])

for i in range(len(local_links)):
    url = 'https://www.traveltowns.jp' + local_links[i]['href']
    line = local_links[i].text
    temp_df = pd.DataFrame([[url, line]])
    ret_df = pd.concat([ret_df, temp_df])
# %%
ret_df = ret_df.reset_index(drop=True)
ret_df.columns = ['url', 'line']
ret_df.to_csv('line_url.csv', index=False)
#%%
line_url = pd.read_csv('line_url.csv')
station_address_df = pd.DataFrame({})
# %%
for j in tqdm(range(len(line_url))):
    try:
        url = line_url.iloc[j]['url']
        line = line_url.iloc[j]['line']

        res = requests.get(url)
        ret_df = pd.DataFrame({})
        soup = BeautifulSoup(res.text, "html.parser")

        tables = soup.find('table')

        trs = tables.find_all('tr')[1:]
        for i in range(len(trs)):
            if trs[i].find('a'):
                station_name = trs[i].find('a').text
                temp_df = pd.DataFrame([[line, station_name]])
                station_address_df = pd.concat([station_address_df, temp_df])
        
        station_address_df = station_address_df.reset_index(drop=True)
        station_address_df.to_csv('station_address_df.csv', index=False)
    except Exception as e:
        print(e)
    time.sleep(10)
# %%
line_url.iloc[54]['url']
# %%
