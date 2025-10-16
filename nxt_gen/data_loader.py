"""
既存CSVファイルの読み込みモジュール
"""
import pandas as pd
import os
from config import STATION_MASTER_PATH, PRICE_DATA_PATH
from line_mapping import normalize_line_name

def load_station_master():
    """
    座標付き駅マスタを読み込む
    座標が存在する駅のみを返す

    Returns:
    --------
    pandas.DataFrame : 座標ありの駅データ (line, station, lat, lng)
    """
    df = pd.read_csv(STATION_MASTER_PATH)

    # 座標が存在する駅のみフィルタ
    df_with_coords = df[df['lat'].notna() & df['lng'].notna()].copy()

    print(f"駅マスタ読み込み完了:")
    print(f"  全駅数: {len(df)}駅")
    print(f"  座標あり: {len(df_with_coords)}駅")
    print(f"  座標なし（除外）: {len(df) - len(df_with_coords)}駅")

    return df_with_coords

def load_price_data():
    """
    家賃情報を読み込む

    Returns:
    --------
    pandas.DataFrame : 家賃データ (line, station, price)
    """
    df = pd.read_csv(PRICE_DATA_PATH)

    # 家賃情報がある駅のみフィルタ
    df_with_price = df[df['price'].notna()].copy()

    print(f"家賃データ読み込み完了:")
    print(f"  全データ: {len(df)}件")
    print(f"  家賃あり: {len(df_with_price)}件")
    print(f"  家賃なし（除外）: {len(df) - len(df_with_price)}件")

    return df_with_price

def load_existing_route_data(target_station):
    """
    既存の経路情報ファイルがあれば読み込む

    Parameters:
    -----------
    target_station : str
        対象駅名

    Returns:
    --------
    pandas.DataFrame or None : 経路データがあればDataFrame、なければNone
    """
    route_file = f"../data/output/route_info/route_info_{target_station}.csv"

    if os.path.exists(route_file):
        df = pd.read_csv(route_file)

        # カラム名を統一形式に変換
        column_mapping = {
            'from': 'station',
            'to': 'to_station',
            'min': 'train_min',
            'train+walk_min': 'total_min'
        }

        # 存在するカラムのみリネーム
        rename_dict = {old: new for old, new in column_mapping.items() if old in df.columns}
        if rename_dict:
            df = df.rename(columns=rename_dict)

        # walk_minカラムを追加（total_min - train_minから計算）
        if 'total_min' in df.columns and 'train_min' in df.columns:
            df['walk_min'] = df['total_min'] - df['train_min']

        # 路線名を正規化（全角JR→半角JR等）
        if 'line' in df.columns:
            df['line'] = df['line'].apply(normalize_line_name)

        print(f"既存の経路情報を使用: {route_file} ({len(df)}件)")
        return df

    return None

def save_data(df, filename):
    """
    データフレームをCSVファイルに保存

    Parameters:
    -----------
    df : pandas.DataFrame
        保存するデータフレーム
    filename : str
        ファイル名
    """
    from config import OUTPUT_DIR

    # 出力ディレクトリが存在しない場合は作成
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    filepath = os.path.join(OUTPUT_DIR, filename)
    df.to_csv(filepath, index=False)
    print(f"データ保存完了: {filepath} ({len(df)}件)")

    return filepath

def save_route_data_to_legacy_format(df, target_station):
    """
    経路データをレガシー形式で保存

    Parameters:
    -----------
    df : pandas.DataFrame
        保存する経路データ
    target_station : str
        対象駅名
    """
    route_file = f"../data/output/route_info/route_info_{target_station}.csv"

    # ディレクトリが存在しない場合は作成
    os.makedirs(os.path.dirname(route_file), exist_ok=True)

    # レガシー形式にカラム名を変換
    df_save = df.copy()
    df_save = df_save.rename(columns={
        'station': 'from',
        'to_station': 'to',
        'train_min': 'min',
        'total_min': 'train+walk_min'
    })

    # priceカラムがなければ追加（レガシー互換性のため）
    if 'price' not in df_save.columns:
        df_save['price'] = None

    # カラム順を調整
    columns_order = ['line', 'price', 'from', 'to', 'trans', 'min', 'train+walk_min']
    df_save = df_save[[col for col in columns_order if col in df_save.columns]]

    df_save.to_csv(route_file, index=False)
    print(f"  経路データを更新: {route_file}")

def save_intermediate_route_data(df_existing, df_new, target_station):
    """
    中間データを保存（クラッシュ対策）

    Parameters:
    -----------
    df_existing : pandas.DataFrame or None
        既存の経路データ
    df_new : pandas.DataFrame
        新規収集した経路データ
    target_station : str
        対象駅名
    """
    temp_file = f"data/route_info_{target_station}_temp.csv"

    if df_existing is not None:
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new

    df_combined.to_csv(temp_file, index=False)
    print(f"    中間保存完了: {temp_file}")

def load_fallback_route_data():
    """
    六本木駅への経路情報をフォールバックデータとして読み込む

    Returns:
    --------
    dict : {駅名: (所要時間, 家賃)} の辞書
    """
    import os

    fallback_data = {}

    # all_min_code.csv を読み込み
    min_path = "../all_min_code.csv"
    price_path = "../all_price_code.csv"

    if os.path.exists(min_path) and os.path.exists(price_path):
        df_min = pd.read_csv(min_path)
        df_price = pd.read_csv(price_path)

        # 駅名をキーにマージ
        df_merged = pd.merge(
            df_min[['from', 'min']],
            df_price[['from', 'price']],
            on='from',
            how='inner'
        )

        for _, row in df_merged.iterrows():
            station = row['from']
            # 六本木への時間を虎ノ門への推定時間として使用（約5分の差を考慮）
            estimated_min = max(1, int(row['min']) - 5)  # 虎ノ門の方が少し近いと仮定
            price = row['price']
            fallback_data[station] = (estimated_min, price)

        print(f"フォールバックデータ読み込み: {len(fallback_data)}駅")

    return fallback_data