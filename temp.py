# %%
import pandas as pd
# %%
min_ = 60
price_ = 20
df = pd.read_csv('csv/to_shibuya/trans_min_price_2ldk.csv')
df = df[(df['min'] < min_) & (df['price'] < price_)
        & (~df['line'].str.contains("新幹線"))]
df = df.reset_index(drop=True)
df
# %%
df.to_csv('csv/to_shibuya/trans_min_price_2ldk_filtered.csv', index=False)
# %%
