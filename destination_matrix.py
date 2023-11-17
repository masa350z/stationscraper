#%%
import requests
import json
from settings import settings
from datetime import datetime
#%%
# Google Map API Key
apikey = settings['APIKEY']
# Google Map Distance Matrix API URL
api = 'https://maps.googleapis.com/maps/api/directions/json'
# Google Map Distance Matrix API mode
# %%
params = {
    'origin': '東京駅',
    'destination': '秋葉原駅',
    'key': apikey,
    'mode': 'transit',
    #'transit_mode': 'rail',
    #'region': 'jp'
    #'arrival_time': datetime(2023,4,1,9)
}
# Google Map APIにリクエスト
raw_response = requests.get(api, params=params)
parsed_response = json.loads(raw_response.text)
# %%
parsed_response
# %%
parsed_response['routes'][0]
# %%
url = 'https://roote.ekispert.net/result?arr=%E5%85%AB%E5%8D%83%E4%BB%A3%E7%B7%91%E3%81%8C%E4%B8%98&arr_code=29081&connect=true&dep=%E6%9D%B1%E4%BA%AC&dep_code=22828&express=true&highway=true&hour&liner=true&local=true&minute&plane=true&shinkansen=true&ship=true&sleep=false&sort=time&surcharge=3&type=dep&via1=&via1_code=&via2=&via2_code='
# %%
from bs4 import BeautifulSoup
res = requests.get(url)
soup = BeautifulSoup(res.text, "html.parser")
# %%
soup
# %%
