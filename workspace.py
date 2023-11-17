# %%
import pandas as pd
import numpy as np
import math
from math import log

def ret_time_weight(a, x, t=40):
    res = 100*1/(1+math.e**(-a*(x-t)))

    return res

def ret_price_weight(a, b, x, p=50):
    if x <= p:
        res = a*x
    else:
        res = b**(x+(log(a/log(b)))/log(b)-p)-b**(log(a/log(b))/log(b))+a*p

    return res
# %%
mm = 50
mx = 100
df = pd.read_csv('req_min_price.csv')
df = df[(df['req_min+walk'] >= mm)&(df['req_min+walk'] < mx)]
df = df.reset_index(drop=True)

dfn = np.array(df)

price_n = dfn[:,-1].astype('float16')
req_n = dfn[:,-2].astype('float16')

price_f = np.array([ret_price_weight(0.6, 1.03, i*10) for i in price_n])
req_f = np.array([ret_time_weight(0.09, i) for i in req_n])

cost_performance = price_f*req_f
cost_performance = pd.DataFrame(cost_performance, columns=['cost_performance'])

sort = np.argsort(price_f*req_f)
ret_df = pd.concat([df, cost_performance], axis=1)

df_sorted = ret_df.iloc[sort]
df_sorted = df_sorted.reset_index(drop=True)

ret_df_sorted = df_sorted[~df_sorted[['from', 'trans']].duplicated()]
ret_df_sorted = ret_df_sorted.reset_index(drop=True)
ret_df_sorted = ret_df_sorted[['from', 'to', 'trans', 'req_min', 'req_min+walk', 'price', 'cost_performance']]
# %%
ret_df_sorted
# %%
ret_df_sorted.to_csv('df_sorted_{}_{}.csv'.format(mm,mx), index=False)
# %%
