"""
データ処理・マージモジュール
"""
import pandas as pd
from line_mapping import apply_all_line_mappings

def merge_station_and_price(df_station, df_price):
    """
    駅マスタと家賃データをマージ
    路線名の表記揺れを解決してから結合

    Parameters:
    -----------
    df_station : pandas.DataFrame
        駅マスタ（座標付き）
    df_price : pandas.DataFrame
        家賃データ

    Returns:
    --------
    pandas.DataFrame : マージ済みデータ
    """
    # 路線名を正規化
    print("路線名を正規化中...")
    df_price_normalized = apply_all_line_mappings(df_price, df_station)

    # 駅マスタをベースに左結合
    print("駅データと家賃データをマージ中...")
    merged = pd.merge(
        df_station,
        df_price_normalized,
        on=['line', 'station'],
        how='left'
    )

    # 重複を削除
    merged = merged.drop_duplicates()

    # 統計情報を表示
    price_available = merged['price'].notna().sum()
    price_missing = merged['price'].isna().sum()

    print(f"マージ完了:")
    print(f"  総駅数: {len(merged)}駅")
    print(f"  家賃データあり: {price_available}駅 ({price_available/len(merged)*100:.1f}%)")
    print(f"  家賃データなし: {price_missing}駅 ({price_missing/len(merged)*100:.1f}%)")

    return merged

def merge_route_info(df_base, df_routes):
    """
    基本データと経路情報をマージ

    Parameters:
    -----------
    df_base : pandas.DataFrame
        基本データ（駅、座標、家賃）
    df_routes : pandas.DataFrame
        経路情報データ

    Returns:
    --------
    pandas.DataFrame : マージ済みデータ
    """
    # 経路情報側のpriceカラムを削除（基本データ側のpriceを使用）
    if 'price' in df_routes.columns:
        df_routes = df_routes.drop(columns=['price'])

    # 路線名と駅名でマージ
    merged = pd.merge(
        df_base,
        df_routes,
        on=['line', 'station'],
        how='inner'  # 経路情報がある駅のみ
    )

    return merged

def filter_stations(df, max_price=None, max_time=None, max_trans=None):
    """
    条件に基づいて駅をフィルタリング

    Parameters:
    -----------
    df : pandas.DataFrame
        フィルタリング対象のデータ
    max_price : float
        最大家賃（万円）
    max_time : int
        最大所要時間（分）
    max_trans : int
        最大乗り換え回数

    Returns:
    --------
    pandas.DataFrame : フィルタリング後のデータ
    """
    df_filtered = df.copy()

    # 家賃でフィルタ
    if max_price is not None:
        df_filtered = df_filtered[
            (df_filtered['price'].isna()) |  # 家賃データなしも含める
            (df_filtered['price'] <= max_price)
        ]

    # 所要時間でフィルタ
    if max_time is not None and 'total_min' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['total_min'] <= max_time]

    # 乗り換え回数でフィルタ
    if max_trans is not None and 'trans' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['trans'] <= max_trans]

    return df_filtered

def aggregate_by_target_stations(df_list):
    """
    複数の目的地への経路情報を統合
    各駅から最も近い目的地への情報を保持

    Parameters:
    -----------
    df_list : list of pandas.DataFrame
        各目的地への経路情報のリスト

    Returns:
    --------
    pandas.DataFrame : 統合されたデータ
    """
    if not df_list:
        return pd.DataFrame()

    if len(df_list) == 1:
        return df_list[0]

    # 全データを結合
    df_all = pd.concat(df_list, ignore_index=True)

    # 各駅（line + station）ごとに最短時間のレコードを選択
    idx = df_all.groupby(['line', 'station'])['total_min'].idxmin()
    df_best = df_all.loc[idx]

    return df_best.reset_index(drop=True)

def prepare_final_dataset(df_station, df_price, route_data_dict):
    """
    最終的なデータセットを準備

    Parameters:
    -----------
    df_station : pandas.DataFrame
        駅マスタ（座標付き）
    df_price : pandas.DataFrame
        家賃データ
    route_data_dict : dict
        目的地ごとの経路情報辞書

    Returns:
    --------
    pandas.DataFrame : 完成したデータセット
    """
    # 1. 駅マスタと家賃をマージ
    df_base = merge_station_and_price(df_station, df_price)

    # 2. 経路情報を統合
    if route_data_dict:
        route_df_list = []
        for target_station, df_route in route_data_dict.items():
            if df_route is not None and not df_route.empty:
                route_df_list.append(df_route)

        if route_df_list:
            df_routes = aggregate_by_target_stations(route_df_list)

            # 3. 基本データと経路情報をマージ
            df_final = merge_route_info(df_base, df_routes)
        else:
            df_final = df_base
    else:
        df_final = df_base

    # 4. カラムの順序を整理
    column_order = [
        'line', 'station', 'lat', 'lng', 'price',
        'to_station', 'trans', 'train_min', 'walk_min', 'total_min'
    ]
    existing_columns = [col for col in column_order if col in df_final.columns]
    df_final = df_final[existing_columns]

    print(f"\n最終データセット作成完了: {len(df_final)}駅")

    return df_final