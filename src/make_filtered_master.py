"""
オフィスエリアフィルタリング済みマスターデータ生成スクリプト

このスクリプトは、make_frontend_master.pyで生成されたデータを
フィルタリングし、3つのオフィスエリア全てで条件を満たす駅のみを抽出する。

前提条件:
- make_frontend_master.pyが実行済みであること
- data/frontend_master/frontend_master_{office}_{ROOM_TYPE}.csv が存在すること

出力:
- data/frontend_master/filtered/filtered_master_toranomon_common_{ROOM_TYPE}.csv
"""

import pandas as pd
import os
from config import ROOM_TYPE


def filter_frontend_master(frontend_master_df, transit_min_upper, trans_num_upper, rent_price_upper):
    """
    フロントエンドマスターデータをフィルタリング

    Args:
        frontend_master_df: フロントエンドマスターデータ
        transit_min_upper: 通勤時間上限（分）
        trans_num_upper: 乗り換え回数上限
        rent_price_upper: 家賃上限（万円）

    Returns:
        DataFrame: フィルタリング済みデータ
    """
    frontend_master = frontend_master_df.copy()

    transit_min_bool = frontend_master['min'] + frontend_master['walk_min'] <= transit_min_upper
    trans_num_bool = frontend_master['trans'] <= trans_num_upper
    rent_price_bool = frontend_master['price'] <= rent_price_upper

    return frontend_master[transit_min_bool & trans_num_bool & rent_price_bool].reset_index(drop=True)


def extract_common_stations(filtered_master_toranomon, filtered_master_tokyo, filtered_master_otsuka):
    """
    3つのエリア全てで条件を満たす駅のみを抽出

    Args:
        filtered_master_toranomon: 虎ノ門エリアのフィルタ済みデータ
        filtered_master_tokyo: 東京エリアのフィルタ済みデータ
        filtered_master_otsuka: 大塚エリアのフィルタ済みデータ

    Returns:
        DataFrame: 3エリア共通駅のみを含む虎ノ門向けデータセット
    """
    # (line, from) の組み合わせをセットとして抽出
    toranomon_stations = set(zip(filtered_master_toranomon['line'], filtered_master_toranomon['from']))
    tokyo_stations = set(zip(filtered_master_tokyo['line'], filtered_master_tokyo['from']))
    otsuka_stations = set(zip(filtered_master_otsuka['line'], filtered_master_otsuka['from']))

    # 3つの集合の共通部分（積集合）
    common_stations = toranomon_stations & tokyo_stations & otsuka_stations

    # 虎ノ門マスターから共通駅のみを抽出
    filtered_master_common = filtered_master_toranomon[
        filtered_master_toranomon.apply(
            lambda row: (row['line'], row['from']) in common_stations,
            axis=1
        )
    ].reset_index(drop=True)

    return filtered_master_common


def remove_duplicate_stations(df):
    """
    駅名（from）で重複がある場合、通勤時間が最小のものを採用

    Args:
        df: DataFrameデータ

    Returns:
        DataFrame: 重複解消済みデータ
    """
    # 一時的に通勤時間合計列を追加
    temp_df = df.copy()
    temp_df['total_time'] = temp_df['min'] + temp_df['walk_min']

    # 駅ごとに通勤時間が最小の行のインデックスを取得
    min_idx = temp_df.groupby('from')['total_time'].idxmin()

    # 元のデータフレームからそのインデックスの行のみを抽出
    return df.loc[min_idx].reset_index(drop=True)


def main():
    """
    メイン処理: フィルタリング済みマスターデータを生成
    """
    data_dir = "../data"

    print("=" * 60)
    print("フィルタリング済みマスターデータ生成開始")
    print("=" * 60)

    # フィルタリング条件
    TRANSIT_MIN_UPPER_TORANOMON = 80  # 通勤時間上限（分）
    TRANSIT_MIN_UPPER_TOKYO = 80  # 通勤時間上限（分）
    TRANSIT_MIN_UPPER_OTSUKA = 60  # 通勤時間上限（分）

    TRANS_NUM_UPPER = 2     # 乗り換え回数上限
    RENT_PRICE_UPPER = 12   # 家賃上限（万円）

    # 1. フロントエンドマスターデータを読み込み
    print("\n[1/4] フロントエンドマスターデータを読み込み中...")
    frontend_master_toranomon = pd.read_csv(
        os.path.join(data_dir, 'frontend_master', f"frontend_master_toranomon_{ROOM_TYPE}.csv")
    )
    frontend_master_tokyo = pd.read_csv(
        os.path.join(data_dir, 'frontend_master', f"frontend_master_tokyo_{ROOM_TYPE}.csv")
    )
    frontend_master_otsuka = pd.read_csv(
        os.path.join(data_dir, 'frontend_master', f"frontend_master_otsuka_{ROOM_TYPE}.csv")
    )
    print(f"  - 虎ノ門: {len(frontend_master_toranomon)} 行")
    print(f"  - 東京: {len(frontend_master_tokyo)} 行")
    print(f"  - 大塚: {len(frontend_master_otsuka)} 行")

    # 2. 各エリアをフィルタリング
    print(f"\n[2/4] フィルタリング実行中...")
    filtered_master_toranomon = filter_frontend_master(
        frontend_master_toranomon, TRANSIT_MIN_UPPER_TORANOMON, TRANS_NUM_UPPER, RENT_PRICE_UPPER
    )
    filtered_master_tokyo = filter_frontend_master(
        frontend_master_tokyo, TRANSIT_MIN_UPPER_TOKYO, TRANS_NUM_UPPER, RENT_PRICE_UPPER
    )
    filtered_master_otsuka = filter_frontend_master(
        frontend_master_otsuka, TRANSIT_MIN_UPPER_OTSUKA, TRANS_NUM_UPPER, RENT_PRICE_UPPER
    )
    print(f"  - 虎ノ門: {len(filtered_master_toranomon)} 行")
    print(f"  - 東京: {len(filtered_master_tokyo)} 行")
    print(f"  - 大塚: {len(filtered_master_otsuka)} 行")

    # 3. 3エリア共通の駅のみを抽出
    print("\n[3/4] 3エリア共通の駅を抽出中...")
    filtered_master_common = extract_common_stations(
        filtered_master_toranomon, filtered_master_tokyo, filtered_master_otsuka
    )
    print(f"  - 共通駅: {len(filtered_master_common)} 行")

    # 4. 駅名の重複を解消（最短通勤時間を採用）
    print("\n[4/4] 駅名の重複を解消中...")
    filtered_master_unique = remove_duplicate_stations(filtered_master_common)
    print(f"  - 重複解消後: {len(filtered_master_unique)} 行")

    # 5. 保存
    output_dir = os.path.join(data_dir, 'frontend_master', 'filtered')
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, f"filtered_master_toranomon_common_{ROOM_TYPE}.csv")
    filtered_master_unique.to_csv(output_path, index=False)

    print("\n" + "=" * 60)
    print(f"✓ 処理完了: {output_path}")
    print("=" * 60)

    return filtered_master_unique


if __name__ == "__main__":
    main()
