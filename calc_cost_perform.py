# %%
import pandas as pd
from tqdm import tqdm
# %%
ndf = pd.read_csv('ndf.csv')
station_price = pd.read_csv('staion_price.csv')
# %%
ret_lis = []

for i in tqdm(range(len(ndf))):
    try:
        t_lis = list(ndf.iloc[i])
        station_name = ndf.iloc[i]['from']
        if station_name == '日本橋(東京都)':
            station_name = '日本橋'
        price = station_price[station_price['station'] ==station_name]['price'].reset_index(drop=True)[0]
        t_lis.append(price)

        ret_lis.append(t_lis)
    except Exception as e:
        print(e)
        print(t_lis)
# %%
nndf = pd.DataFrame(ret_lis)
nndf.columns=['line', 'from', 'to', 'trans', 'req_min', 'req_min+walk', 'price']
# %%
nndf.to_csv('req_min_price.csv', index=False)
# %%
