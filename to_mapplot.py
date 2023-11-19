# %%
import pandas as pd

df = pd.read_csv('csv/to_roppongi/all.csv')
# %%
df = df[df['to'] == '六本木']
# %%
# df = df[['price', 'from']]
df = df[['min', 'from']]
# %%
df = df[~df.duplicated()].reset_index(drop=True)
# %%
df.to_csv('csv/to_roppongi/all_min.csv', index=False)
# %%
df
# %%
df
# %%
