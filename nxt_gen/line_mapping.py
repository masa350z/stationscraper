"""
路線名の表記揺れを正規化するマッピング定義
FIX_LINE_NAME_MAPPING.mdに基づいて実装
"""

# JR路線の全角→半角変換マッピング
JR_LINE_MAPPING = {
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
    'ＪＲ宇都宮線': 'JR宇都宮線',
    'ＪＲ高崎線': 'JR高崎線',
    'ＪＲ常磐線': 'JR常磐線',
    'ＪＲ常磐緩行線': 'JR常磐線各駅停車',
    'ＪＲ総武線': 'JR総武線快速',
    'ＪＲ総武緩行線': 'JR中央・総武線各駅停車',
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
    'ＪＲ上越線': 'JR上越線',
    'ＪＲ東北線': 'JR東北線',
    'ＪＲ上野東京ライン': 'JR上野東京ライン',
    'ＪＲ中央本線': 'JR中央本線',
    'ＪＲ御殿場線': 'JR御殿場線',
    'ＪＲ東海道本線': 'JR東海道本線',
    'ＪＲ東金線': 'JR東金線',
    'ＪＲ総武本線': 'JR総武本線',
    'ＪＲ総武線快速': 'JR総武線快速',
}

# その他の路線名マッピング
OTHER_LINE_MAPPING = {
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

# 全マッピングを統合
LINE_NAME_MAPPING = {**JR_LINE_MAPPING, **OTHER_LINE_MAPPING}

# 千葉モノレール2号線の駅リスト
CHIBA_MONORAIL_2_STATIONS = [
    '千葉', '千葉公園', '千城台', '千城台北',
    '小倉台', '桜木', '都賀', '作草部'
]

def normalize_line_name(line_name):
    """
    路線名を正規化する

    Parameters:
    -----------
    line_name : str
        正規化したい路線名

    Returns:
    --------
    str : 正規化された路線名
    """
    return LINE_NAME_MAPPING.get(line_name, line_name)

def normalize_odakyu_line(df_price, df_station):
    """
    「小田急線」を駅マスタに基づいて正しい路線名に変換する

    Parameters:
    -----------
    df_price : pandas.DataFrame
        家賃データ（line, station, priceカラムを含む）
    df_station : pandas.DataFrame
        駅マスタデータ（line, stationカラムを含む）

    Returns:
    --------
    pandas.DataFrame : 小田急線が正規化されたデータフレーム
    """
    import pandas as pd

    # コピーを作成
    df_price_copy = df_price.copy()

    # 小田急線の駅を抽出
    odakyu_mask = df_price_copy['line'] == '小田急線'
    odakyu_stations = df_price_copy[odakyu_mask]['station'].unique()

    # 駅ごとに正しい路線名を特定
    station_to_line = {}
    for station in odakyu_stations:
        # 駅マスタから該当駅の小田急路線を検索
        matches = df_station[
            (df_station['station'] == station) &
            (df_station['line'].str.contains('小田急', na=False))
        ]
        if len(matches) > 0:
            # 最初にマッチした小田急路線を使用
            station_to_line[station] = matches.iloc[0]['line']
        else:
            # デフォルトは小田急小田原線
            station_to_line[station] = '小田急小田原線'

    # 駅名に基づいて路線名を更新
    for idx in df_price_copy[odakyu_mask].index:
        station = df_price_copy.loc[idx, 'station']
        df_price_copy.loc[idx, 'line'] = station_to_line.get(station, '小田急小田原線')

    return df_price_copy

def fix_chiba_monorail(df):
    """
    千葉モノレールの1号線・2号線を正しく分類する

    Parameters:
    -----------
    df : pandas.DataFrame
        路線名と駅名を含むデータフレーム

    Returns:
    --------
    pandas.DataFrame : 修正されたデータフレーム
    """
    df_copy = df.copy()

    # 千葉モノレール2号線の駅を修正
    df_copy.loc[
        (df_copy['line'] == '千葉モノレール1号線') &
        (df_copy['station'].isin(CHIBA_MONORAIL_2_STATIONS)),
        'line'
    ] = '千葉モノレール2号線'

    return df_copy

def apply_all_line_mappings(df_price, df_station):
    """
    全ての路線名マッピングを適用する

    Parameters:
    -----------
    df_price : pandas.DataFrame
        家賃データ
    df_station : pandas.DataFrame
        駅マスタデータ

    Returns:
    --------
    pandas.DataFrame : 路線名が正規化されたデータフレーム
    """
    df_result = df_price.copy()

    # 1. 通常のマッピングを適用
    df_result['line'] = df_result['line'].apply(normalize_line_name)

    # 2. 小田急線の特別処理
    df_result = normalize_odakyu_line(df_result, df_station)

    # 3. 千葉モノレールの修正
    df_result = fix_chiba_monorail(df_result)

    return df_result