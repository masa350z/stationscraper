# %%
import requests
import pandas as pd
from bs4 import BeautifulSoup
# %%
ret_lis = []
error_lis = []
pref_lis = ['tokyo', 'kanagawa', 'saitama', 'chiba']
master_url = 'https://suumo.jp/chintai/soba/{}/ensen/'
# %%
# pref = pref_lis[0]
for pref in pref_lis:
    master_soup = requests.get(master_url.format(pref))
    master_soup = BeautifulSoup(master_soup.text, "html.parser")
    master_table = master_soup.find('table', class_='searchtable')
    lines = master_table.find_all('a')

    # line = lines[0]
    for line in lines:
        try:
            line_name = line.text

            url = 'https://suumo.jp' + line['href']
            url += '?mdKbn=04'
            soup = requests.get(url)
            soup = BeautifulSoup(soup.text, "html.parser")

            table = soup.find('table', class_='graphpanel_matrix')
            stations = table.find_all('tr', class_='js-graph-data')

            # station = stations[0]
            for station in stations:
                tds = station.find_all('td')
                station_name = tds[0].text
                price = float(tds[1].text[:-2])

                ret_lis.append([line_name, station_name, price])
                print([line_name, station_name, price])
        except Exception as e:
            print(e)
            error_lis.append([pref, line, station])
# %%
error_lis
# %%
df = pd.DataFrame(ret_lis)
df.columns = ['line', 'station', 'price']
df = df[~df.duplicated()]
df = df.reset_index(drop=True)
# %%
df.to_csv('staion_price_2ldk.csv', index=False)
# %%
df
# %%
