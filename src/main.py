# %%
"""
データパイプラインのメイン実行スクリプト

駅データ、家賃データ、経路情報を取得・統合するパイプラインを実行する。
各処理の詳細はfunctions.pyに定義されている。
"""
import os
from functions import (
    make_station_master,
    add_geocode_to_station_master,
    make_rent_data,
    make_merged_data,
    make_route_data,
)

# %%
# データパイプラインのメイン処理
# 各関数は入力としてDataFrameを受け取り、処理結果のDataFrameを返す

data_dir = "../data"

# 1. 駅マスタを取得
station_master_df = make_station_master()

# 2. 座標を付与
station_with_coords_df = add_geocode_to_station_master(
    station_master_df,
    os.path.join(data_dir, "station_master", "station_address_with_coordinates.csv")
)

# 3. 家賃データを取得
rent_data_df = make_rent_data()

# 4. マージ
merged_df = make_merged_data(station_with_coords_df, rent_data_df)

# 5. 経路情報を取得
route_data_dict = make_route_data(merged_df)

# 6. 全経路を統合（必要に応じて）
# final_df = merge_all_route_data(route_data_dict)
