# %%
import pandas as pd

df = pd.read_csv('csv/to_roppongi/all.csv')
# %%
"""
# df = df[df['to'] == '六本木']

df = df[['price', 'from']]
# df = df[['min', 'from']]
df = df[~df.duplicated()].reset_index(drop=True)
df.to_csv('csv/to_roppongi/all_price.csv', index=False)
"""
# %%
df = pd.read_csv('csv/to_roppongi/all_price.csv')
df
# %%
mx_price = 8
mn_price = 7
condition01 = df['price'] < mx_price
condition02 = df['price'] >= mn_price
# %%
df[condition01 & condition02][80:120]

# %%
