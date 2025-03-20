import pandas as pd
import numpy as np

def merge_station_info(station_csv_path: str, price_csv_path: str, output_path: str) -> None:
    """
    駅マスタ（路線, 駅）とスクレイピングした家賃情報（路線, 駅, 賃料）をマージしてCSV出力する。
    """
    df_station = pd.read_csv(station_csv_path)
    df_price = pd.read_csv(price_csv_path)

    # 同じキー名に合わせるため、列名を揃えることを想定
    # もともと 'station_price_2ldk.csv' に 'line', 'station', 'price' が入っている想定
    merged = pd.merge(df_station, df_price, on=['line', 'station'], how='left')
    merged.drop_duplicates(inplace=True)
    merged.to_csv(output_path, index=False)
    print(f"マージ完了: {output_path}")


def filter_station_data(input_csv: str, time_threshold: int, price_threshold: float, output_csv: str) -> None:
    """
    時間や家賃などの条件でデータをフィルタして出力する。
    """
    df = pd.read_csv(input_csv)
    # 'min' と 'price' を想定したフィルタ例
    filtered = df[(df['min'] <= time_threshold) & (df['price'] <= price_threshold)]
    filtered = filtered.reset_index(drop=True)
    filtered.to_csv(output_csv, index=False)
    print(f"フィルタリング完了: {output_csv}")


def add_walking_time(df: pd.DataFrame, walk_dict: dict, to_col='to', time_col='min', new_col='train+walk_min') -> pd.DataFrame:
    """
    目的地ごとに徒歩分数を加算して新列を返す。
    walk_dict: {'六本木': 7, ...} のような徒歩時間辞書
    df: ['to', 'min'] 列が入っているDataFrame
    """
    walk_list = []
    for dest in df[to_col]:
        walk_min = walk_dict.get(dest, 0)
        walk_list.append(walk_min)
    walk_array = np.array(walk_list)
    df[new_col] = walk_array + df[time_col].values
    return df