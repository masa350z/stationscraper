# %%
import pandas as pd
# %%
v1 = pd.read_csv('from_to_min.csv')
v2 = pd.read_csv('from_to_min2.csv')
v3 = pd.read_csv('from_to_min3_.csv')
v4 = pd.read_csv('from_to_min3.csv')
# %%
df = pd.concat([v1, v2, v3, v4])
df = df[~df.duplicated()]
df = df.reset_index(drop=True)
df.columns = ['line', 'from', 'to', 'trans', 'req_min']
# %%
trans = df['trans'] <= 1
req = df['req_min'] <= 60

n_df = df[trans & req].reset_index(drop=True)
# %%
walk_min_dic = {'宝町': 3,
                '八丁堀': 3,
                '京橋': 7,
                '東京': 12,
                '日本橋(東京都)': 9,
                '茅場町': 9,
                '銀座一丁目': 11,
                '新富町': 8}
# %%
n_req_min_lis = []
for i in range(len(n_df)):
    t_st = n_df.iloc[i]['to']
    t_min = n_df.iloc[i]['req_min']
    n_req_min_lis.append(t_min + walk_min_dic[t_st])
# %%
n_req_min_df = pd.DataFrame(n_req_min_lis)
n_req_min_df.columns = ['req_min+walk']
# %%
n_df = pd.concat([n_df, n_req_min_df], axis=1)

trans = n_df['trans'] <= 1
req = n_df['req_min+walk'] <= 60

n_df = n_df[trans & req].reset_index(drop=True)
# %%
n_df
# %%
n_df.to_csv('ndf.csv', index=False)
# %%
n_df[~n_df[['line', 'from']].duplicated()]
# %%
