# %%
import matplotlib.pyplot as plt
import requests
from settings import settings
import pandas as pd


def get_coordinates(location_name, api_key):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": location_name,
        "key": api_key
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        results = response.json().get("results", [])
        if results:
            return results[0]["geometry"]["location"]
        else:
            return "No results found"
    else:
        return f"Error: {response.status_code}"


# ここで自分のAPIキーを入力してください
api_key = settings['APIKEY']
location_name = "東京タワー"  # 例として東京タワーを検索
coordinates = get_coordinates(location_name, api_key)
print(coordinates)

# %%
# df = pd.read_csv('csv/to_roppongi/all_price.csv')
df = pd.read_csv('csv/to_roppongi/all_min.csv')
# %%
coding_list = []
for i in df['from']:
    code = get_coordinates(i + '駅', api_key)
    coding_list.append(code)
# %%
ret_list = []
for i in coding_list:
    if i == 'No results found':
        ret_list.append([0, 0])
    else:
        ret_list.append([i['lat'], i['lng']])

coding_df = pd.DataFrame(ret_list,
                         columns=['lat', 'lng'])

# %%
# pd.concat([df, coding_df], axis=1).to_csv('csv/to_roppongi/all_price_code.csv')
pd.concat([df, coding_df], axis=1).to_csv('csv/to_roppongi/all_min_code.csv')


# %%
