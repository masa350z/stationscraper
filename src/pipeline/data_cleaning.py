import pandas as pd
import numpy as np

# 路線名マッピング辞書（家賃データ→駅マスタの表記に統一）
LINE_NAME_MAPPING = {
    # JR路線（全角→半角）
    'ＪＲ山手線': 'JR山手線',
    'ＪＲ中央線': 'JR中央線',
    'ＪＲ京浜東北線': 'JR京浜東北線',
    'ＪＲ埼京線': 'JR埼京線',
    'ＪＲ京葉線': 'JR京葉線',
    'ＪＲ南武線': 'JR南武線',
    'ＪＲ横浜線': 'JR横浜線',
    'ＪＲ根岸線': 'JR根岸線',
    'ＪＲ武蔵野線': 'JR武蔵野線',
    'ＪＲ横須賀線': 'JR横須賀線',
    'ＪＲ東海道線': 'JR東海道線',
    'ＪＲ東海道本線': 'JR東海道線',
    'ＪＲ宇都宮線': 'JR宇都宮線',
    'ＪＲ高崎線': 'JR高崎線',
    'ＪＲ常磐線': 'JR常磐線',
    'ＪＲ常磐緩行線': 'JR常磐線各駅停車',
    'ＪＲ総武線': 'JR中央・総武線各駅停車',
    'ＪＲ外房線': 'JR外房線',
    'ＪＲ内房線': 'JR内房線',
    'ＪＲ成田線': 'JR成田線',
    'ＪＲ鹿島線': 'JR鹿島線',
    'ＪＲ久留里線': 'JR久留里線',
    'ＪＲ鶴見線': 'JR鶴見線',
    'ＪＲ相模線': 'JR相模線',
    'ＪＲ八高線': 'JR八高線',
    'ＪＲ川越線': 'JR川越線',
    'ＪＲ日光線': 'JR日光線',
    'ＪＲ五日市線': 'JR五日市線',
    'ＪＲ青梅線': 'JR青梅線',
    'ＪＲ御殿場線': 'JR御殿場線',
    'ＪＲ東金線': 'JR東金線',
    'ＪＲ総武本線': 'JR総武本線',
    'ＪＲ総武線快速': 'JR総武線快速',

    # 地下鉄
    'グリーンライン': '横浜市営地下鉄グリーンライン',
    'ブルーライン': '横浜市営地下鉄ブルーライン',
    'シーサイドライン': '金沢シーサイドライン',

    # モノレール
    '千葉都市モノレール': '千葉モノレール1号線',
    '多摩都市モノレール': '多摩モノレール',

    # 私鉄
    '伊豆箱根大雄山線': '伊豆箱根鉄道大雄山線',
    '北総線': '北総鉄道北総線',
    '埼玉高速鉄道': '埼玉高速鉄道線',
    '東葉高速鉄道': '東葉高速線',
    '江ノ島電鉄線': '江ノ電',
    '小湊鉄道線': '小湊鉄道',
    '銚子電気鉄道': '銚子電鉄',
    '成田スカイアクセス': '京成成田空港線',
    '新交通ゆりかもめ': 'ゆりかもめ',
    '埼玉新都市交通伊奈線': 'ニューシャトル',

    # 特殊ケース
    '湘南新宿ライン宇須': 'JR湘南新宿ライン（宇都宮線・横須賀線）',
    '湘南新宿ライン高海': 'JR湘南新宿ライン（高崎線・東海道線）',
    '京王新線': '京王線',
    '箱根登山鉄道鋼索線': '箱根登山鉄道',
}

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


def normalize_odakyu_line(price_df: pd.DataFrame, station_df: pd.DataFrame) -> pd.DataFrame:
    """
    「小田急線」を駅マスタに基づいて正しい路線名に変換する

    家賃データでは全て「小田急線」だが、駅マスタでは3路線に分かれている：
    - 小田急小田原線
    - 小田急江ノ島線
    - 小田急多摩線

    Args:
        price_df: 家賃DataFrame (line, station, price)
        station_df: 駅マスタDataFrame (line, station, ...)

    Returns:
        路線名を修正した家賃DataFrame
    """
    # 小田急線の駅を抽出
    odakyu_mask = price_df['line'] == '小田急線'
    odakyu_stations = price_df[odakyu_mask]['station'].unique()

    # 駅ごとに正しい路線名を特定
    station_to_line = {}
    for station in odakyu_stations:
        # 駅マスタから該当駅の小田急路線を検索
        matches = station_df[
            (station_df['station'] == station) &
            (station_df['line'].str.contains('小田急', na=False))
        ]
        if len(matches) > 0:
            # 最初にマッチした小田急路線を使用
            station_to_line[station] = matches.iloc[0]['line']
        else:
            # デフォルトは小田急小田原線
            station_to_line[station] = '小田急小田原線'

    # 駅名に基づいて路線名を更新
    for idx in price_df[odakyu_mask].index:
        station = price_df.loc[idx, 'station']
        price_df.loc[idx, 'line'] = station_to_line.get(station, '小田急小田原線')

    return price_df


def normalize_line_names(price_df: pd.DataFrame, station_df: pd.DataFrame) -> pd.DataFrame:
    """
    家賃データの路線名を駅マスタに合わせて正規化する

    Args:
        price_df: 家賃DataFrame (line, station, price)
        station_df: 駅マスタDataFrame (line, station, ...)

    Returns:
        正規化された家賃DataFrame
    """
    # DataFrameをコピー（元のデータを変更しない）
    df_normalized = price_df.copy()

    # 1. LINE_NAME_MAPPINGで一括置換（JR全角→半角など）
    df_normalized['line'] = df_normalized['line'].replace(LINE_NAME_MAPPING)

    # 2. 小田急線の特別処理
    df_normalized = normalize_odakyu_line(df_normalized, station_df)

    # 3. 千葉モノレール2号線の駅を区別
    # 2号線の駅リスト: 千葉、千葉公園、千城台など
    monorail2_stations = ['千葉', '千葉公園', '千城台', '千城台北', '小倉台', '桜木', '都賀', '作草部']
    df_normalized.loc[
        (df_normalized['line'] == '千葉モノレール1号線') &
        (df_normalized['station'].isin(monorail2_stations)),
        'line'
    ] = '千葉モノレール2号線'

    return df_normalized