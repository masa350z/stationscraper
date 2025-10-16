# 路線名マッピング問題の修正実装ガイド

## 問題の概要

駅マスタ（TravelTowns）と家賃データ（SUUMO）で路線名の表記が異なるため、データマージ時に多くの駅が欠損している。

### 現状の問題
- **駅マスタ**: 2,496駅
- **家賃データ**: 2,167駅
- **正しくマージされた駅**: 約1,108駅のみ（44%）
- **欠損**: 1,388駅（56%）が家賃データとマッチしない

### 具体例
- 小田急小田原線の登戸駅が最終データ（`merged_with_coordinates.csv`）に含まれていない
  - 駅マスタ: `小田急小田原線,登戸`
  - 家賃データ: `小田急線,登戸`
  - マージ失敗により欠損

## 路線名の不一致パターン

### 1. JR路線（28路線）
駅マスタは半角「JR」、家賃データは全角「ＪＲ」

```
ＪＲ山手線 → JR山手線
ＪＲ中央線 → JR中央線
ＪＲ京浜東北線 → JR京浜東北線
ＪＲ埼京線 → JR埼京線
ＪＲ京葉線 → JR京葉線
ＪＲ南武線 → JR南武線
ＪＲ横浜線 → JR横浜線
ＪＲ根岸線 → JR根岸線
ＪＲ武蔵野線 → JR武蔵野線
ＪＲ横須賀線 → JR横須賀線
ＪＲ東海道線 → JR東海道線
ＪＲ宇都宮線 → JR宇都宮線
ＪＲ高崎線 → JR高崎線
ＪＲ常磐線 → JR常磐線
ＪＲ常磐緩行線 → JR常磐線各駅停車
ＪＲ総武線 → JR総武線快速
ＪＲ総武緩行線 → JR中央・総武線各駅停車
ＪＲ外房線 → JR外房線
ＪＲ内房線 → JR内房線
ＪＲ成田線 → JR成田線
ＪＲ鹿島線 → JR鹿島線
ＪＲ久留里線 → JR久留里線
ＪＲ鶴見線 → JR鶴見線
ＪＲ相模線 → JR相模線
ＪＲ八高線 → JR八高線
ＪＲ川越線 → JR川越線
ＪＲ日光線 → JR日光線
ＪＲ五日市線 → JR五日市線
ＪＲ青梅線 → JR青梅線
```

### 2. 小田急線の問題
家賃データでは全て「小田急線」だが、駅マスタでは3路線に分かれている：
- 小田急小田原線
- 小田急江ノ島線
- 小田急多摩線

### 3. その他の路線名不一致

```
# 地下鉄
グリーンライン → 横浜市営地下鉄グリーンライン
ブルーライン → 横浜市営地下鉄ブルーライン
シーサイドライン → 金沢シーサイドライン

# モノレール
千葉都市モノレール → 千葉モノレール1号線（または2号線）
多摩都市モノレール → 多摩モノレール

# 私鉄
伊豆箱根大雄山線 → 伊豆箱根鉄道大雄山線
北総線 → 北総鉄道北総線
埼玉高速鉄道 → 埼玉高速鉄道線
東葉高速鉄道 → 東葉高速線
江ノ島電鉄線 → 江ノ電
小湊鉄道線 → 小湊鉄道
銚子電気鉄道 → 銚子電鉄
成田スカイアクセス → 京成成田空港線
新交通ゆりかもめ → ゆりかもめ
埼玉新都市交通伊奈線 → ニューシャトル

# 特殊ケース
湘南新宿ライン宇須 → JR湘南新宿ライン（宇都宮線・横須賀線）
湘南新宿ライン高海 → JR湘南新宿ライン（高崎線・東海道線）
京王新線 → 京王線
箱根登山鉄道鋼索線 → 箱根登山鉄道

# マッピング不可（新幹線など、通常の分析では不要）
東海道新幹線 → None
東北新幹線 → None
上越新幹線 → None
北陸新幹線 → None
ユーカリが丘線 → None
```

## 実装方法

### 1. `src/pipeline/data_cleaning.py` の修正

#### Step 1: 路線名マッピング辞書を追加

```python
# ファイルの先頭付近に追加
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

    # 地下鉄
    'グリーンライン': '横浜市営地下鉄グリーンライン',
    'ブルーライン': '横浜市営地下鉄ブルーライン',
    'シーサイドライン': '金沢シーサイドライン',

    # モノレール
    '千葉都市モノレール': '千葉モノレール1号線',  # 2号線の駅は要確認
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
```

#### Step 2: 小田急線の処理用関数を追加

```python
def normalize_odakyu_line(df_price, df_station):
    """
    「小田急線」を駅マスタに基づいて正しい路線名に変換する
    """
    # 小田急線の駅を抽出
    odakyu_mask = df_price['line'] == '小田急線'
    odakyu_stations = df_price[odakyu_mask]['station'].unique()

    # 駅ごとに正しい路線名を特定
    station_to_line = {}
    for station in odakyu_stations:
        # 駅マスタから該当駅の小田急路線を検索
        matches = df_station[
            (df_station['station'] == station) &
            (df_station['line'].str.contains('小田急'))
        ]
        if len(matches) > 0:
            # 最初にマッチした小田急路線を使用
            station_to_line[station] = matches.iloc[0]['line']
        else:
            # デフォルトは小田急小田原線
            station_to_line[station] = '小田急小田原線'

    # 駅名に基づいて路線名を更新
    for idx in df_price[odakyu_mask].index:
        station = df_price.loc[idx, 'station']
        df_price.loc[idx, 'line'] = station_to_line.get(station, '小田急小田原線')

    return df_price
```

#### Step 3: merge_station_info関数を修正

```python
def merge_station_info(station_csv_path: str, price_csv_path: str, output_path: str) -> None:
    """
    駅マスタ（路線, 駅）とスクレイピングした家賃情報（路線, 駅, 賃料）をマージしてCSV出力する。
    路線名の不一致を解決するため、家賃データの路線名を駅マスタに合わせて正規化する。
    """
    df_station = pd.read_csv(station_csv_path)
    df_price = pd.read_csv(price_csv_path)

    print(f"マージ前: 駅マスタ {df_station.shape[0]}件, 家賃データ {df_price.shape[0]}件")

    # 路線名を正規化（マッピング辞書を使用）
    df_price['line'] = df_price['line'].replace(LINE_NAME_MAPPING)

    # 小田急線の特別処理
    df_price = normalize_odakyu_line(df_price, df_station)

    # 千葉モノレール2号線の処理（必要に応じて）
    # 2号線の駅リスト: 千葉、千葉公園、千城台など
    monorail2_stations = ['千葉', '千葉公園', '千城台', '千城台北', '小倉台', '桜木', '都賀', '作草部']
    df_price.loc[
        (df_price['line'] == '千葉モノレール1号線') &
        (df_price['station'].isin(monorail2_stations)),
        'line'
    ] = '千葉モノレール2号線'

    # 駅マスタをベースに左結合
    merged = pd.merge(df_station, df_price, on=['line', 'station'], how='left')

    # 重複を削除
    merged.drop_duplicates(inplace=True)

    # 結果を保存
    merged.to_csv(output_path, index=False)

    # 統計情報を出力
    price_available = merged['price'].notna().sum()
    price_missing = merged['price'].isna().sum()

    print(f"マージ完了: {output_path}")
    print(f"  総駅数: {merged.shape[0]}件")
    print(f"  家賃データあり: {price_available}件 ({price_available/merged.shape[0]*100:.1f}%)")
    print(f"  家賃データなし: {price_missing}件 ({price_missing/merged.shape[0]*100:.1f}%)")
```

### 2. 実行前の準備

既存の出力ファイルを削除（再生成のため）：

```bash
# 家賃情報マージ後のファイル
rm data/output/price_info/price_by_station_*.csv

# 経路情報ファイル
rm data/output/route_info/route_info_*.csv

# 最終マージファイル
rm data/output/merged/mergend_info_*.csv
rm data/output/merged/merged_with_coordinates.csv
```

### 3. 実行

```bash
cd src
python main.py
```

### 4. 動作確認

修正が正しく動作していることを確認：

```python
# 確認スクリプト
import pandas as pd

# マージ結果を確認
df = pd.read_csv('data/output/price_info/price_by_station_one_room.csv')
print(f"総駅数: {df.shape[0]}")  # 2,496件になるはず
print(f"家賃データあり: {df['price'].notna().sum()}")  # 大幅に増加するはず

# 登戸駅が含まれているか確認
noborito = df[df['station'] == '登戸']
print("\n登戸駅のデータ:")
print(noborito[['line', 'station', 'price']])
# 以下が出力されるはず:
# JR南武線,登戸,5.7
# 小田急小田原線,登戸,5.7

# 最終的なマージファイルも確認
final = pd.read_csv('data/output/merged/merged_with_coordinates.csv')
noborito_final = final[final['from'] == '登戸']
print(f"\n最終データに登戸駅が{len(noborito_final)}件含まれています")
```

## 期待される改善効果

### Before（現状）
- 駅マスタ2,496駅のうち、家賃データとマッチするのは約1,108駅（44%）
- 多くの重要な駅（登戸など）が欠損

### After（修正後）
- 駅マスタ2,496駅が全て出力に含まれる
- 家賃データとマッチする駅が大幅に増加（推定80%以上）
- 路線名の不一致による欠損がほぼ解消

## トラブルシューティング

### 問題: マージ後も駅数が少ない
- `LINE_NAME_MAPPING`辞書に漏れがないか確認
- 小田急線の処理が正しく動作しているか確認

### 問題: 特定の駅が依然として欠損
- その駅の路線名を両データで確認し、マッピングを追加

### デバッグ用コード

```python
# 路線名の不一致を調査
import pandas as pd

df_station = pd.read_csv('data/station_address.csv')
df_price = pd.read_csv('data/station_price/station_price_one_room.csv')

# 正規化後の不一致を確認
df_price_normalized = df_price.copy()
df_price_normalized['line'] = df_price_normalized['line'].replace(LINE_NAME_MAPPING)

station_lines = set(df_station['line'].unique())
price_lines = set(df_price_normalized['line'].unique())

print("まだマッピングされていない路線（家賃データ側）:")
for line in sorted(price_lines - station_lines):
    print(f"  {line}")
```

## 注意事項

1. **データソースの更新時**: TravelTownsやSUUMOの表記が変わった場合、マッピング辞書の更新が必要
2. **新路線の追加時**: 新しい路線が追加された場合、マッピングの追加が必要
3. **千葉モノレール**: 1号線と2号線の駅を正しく区別する必要がある
4. **複数路線を持つ駅**: 同じ駅名で複数の路線がある場合、全ての組み合わせが出力される