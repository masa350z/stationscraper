# %%
import pandas as pd

df = pd.read_csv('csv/to_roppongi/trans_min_price.csv')
# %%
max_trans = 100
max_min = 6000
max_price = 65

concition01 = df['trans'] <= max_trans
concition02 = df['price'] <= max_price
condition03 = df['train+walk_min'] <= max_min

ndf = df[concition01 & concition02 & condition03].reset_index(drop=True)
ndf.to_csv('csv/to_roppongi/all.csv', index=False)
# %%
for i in range(6):
    temp_df = ndf[(ndf['train+walk_min'] > i*10) & (ndf['train+walk_min'] <= (i+1)*10)
                  ].reset_index(drop=True)
    temp_df.to_csv('csv/to_roppongi/{}_{}.csv'.format(i*10, (i+1)*10),
                   index=False)
# %%
