# %%
import pandas as pd
# %%
df = pd.read_csv('csv/to_shibuya/trans_min_price_2ldk.csv')
df[(df['min'] < 50) & (df['price'] < 17) & (~df['line'].str.contains("新幹線"))]
# %%
