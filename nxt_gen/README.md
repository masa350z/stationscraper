# nxt_gen - 駅情報統合システム

既存の座標付き駅マスタと家賃データを活用し、経路情報を追加した完全なデータセットを作成してWeb上で可視化するシステム。

## 特徴

- **既存データ活用**: `station_address_with_coordinates.csv`を起点として利用
- **路線名正規化**: FIX_LINE_NAME_MAPPING.mdに基づく表記揺れ解決
- **シンプル設計**: KISS原則に従った最小限の実装
- **DB不要**: CSVファイル直接利用
- **Docker不要**: pip + pythonで実行可能

## システム構成

```
nxt_gen/
├── main.py              # メインパイプライン
├── config.py            # 設定ファイル
├── line_mapping.py      # 路線名マッピング
├── data_loader.py       # データ読み込み
├── route_collector.py   # 経路情報収集（Ekispert API）
├── data_processor.py    # データ処理・マージ
├── data/               # 出力データ
└── webapp/             # Webアプリケーション
    ├── app.py          # Flaskサーバー
    └── templates/
        └── index.html  # 地図表示画面
```

## セットアップ

### 1. 必要なパッケージのインストール

```bash
pip install pandas flask python-dotenv requests beautifulsoup4 numpy
```

### 2. 環境変数の設定

`.env`ファイルを作成し、Ekispert APIキーを設定:

```
EKISPERT_KEY=your_api_key_here
```

## 使い方

### データパイプラインの実行

```bash
cd nxt_gen
python main.py
```

実行すると以下の処理が行われます:

1. 既存の座標付き駅マスタを読み込み（座標なしは除外）
2. 家賃データを読み込み、路線名を正規化してマージ
3. 経路情報を収集（既存データがあれば再利用）
4. 最終データセットを生成・保存

出力ファイル:
- `data/stations_complete.csv`: 全データ
- `data/filtered_stations_complete.csv`: フィルタ済みデータ

### Webアプリの起動

```bash
cd nxt_gen/webapp
python app.py
```

ブラウザで `http://localhost:5000` にアクセス

## データフィルタリング条件

デフォルト設定（config.pyで変更可能）:
- 家賃: 10万円以下
- 通勤時間: 60分以内
- 乗換回数: 2回以下

## 入力データ

### 必須ファイル

1. **駅マスタ**: `../data/station_address_with_coordinates.csv`
   - カラム: line, station, lat, lng
   - 座標ありの駅のみ使用

2. **家賃データ**: `../data/output/price_info/price_by_station_one_room.csv`
   - カラム: line, station, price
   - 路線名の表記揺れは自動正規化

### オプション（既存データ再利用）

- `../data/output/route_info/route_info_{駅名}.csv`
  - 既に収集済みの経路情報があれば再利用

## 出力データ（フロントエンドで必要なCSV形式）

Webアプリケーション（webapp/app.py）は以下の形式のCSVファイルを読み込みます:

### ファイルパス
- `data/stations_complete.csv` - 全駅データ
- `data/filtered_stations_complete.csv` - フィルタ済みデータ

### 必須カラム

| カラム名 | 型 | 説明 | 例 |
|---------|-----|------|-----|
| `line` | string | 路線名 | `JR山手線` |
| `station` | string | 駅名 | `渋谷` |
| `lat` | float | 緯度 | `35.6581` |
| `lng` | float | 経度 | `139.7017` |

### オプションカラム（家賃情報）

| カラム名 | 型 | 説明 | 例 |
|---------|-----|------|-----|
| `price` | float | ワンルーム家賃相場（万円） | `8.5` |

### オプションカラム（経路情報）

| カラム名 | 型 | 説明 | 例 |
|---------|-----|------|-----|
| `to_station` | string | 目的地駅名 | `虎ノ門ヒルズ` |
| `total_min` | int | 総所要時間（電車+徒歩、分） | `45` |
| `trans` | int | 乗換回数 | `2` |
| `train_min` | int | 電車移動時間（分） | `40` |
| `walk_min` | int | 徒歩時間（分） | `5` |

### データ例

```csv
line,station,lat,lng,price,to_station,trans,train_min,walk_min,total_min
JR山手線,渋谷,35.6581,139.7017,12.5,虎ノ門ヒルズ,1,15,4,19
東急東横線,祐天寺,35.6319,139.6972,8.2,虎ノ門ヒルズ,2,25,4,29
```

### 注意点

- **座標データは必須**: lat/lngがない行は地図に表示されません
- **家賃・経路情報は任意**: これらがない駅も地図には表示されますが、情報が不完全になります
- **NaN/空値の扱い**:
  - `price`が空の場合、家賃情報なしとして扱われます
  - 経路情報カラムが全て空の場合、経路情報なしとして扱われます

## 注意事項

- 経路情報収集にはEkispert APIキーが必要
- APIキーがない場合、経路情報なしで動作可能
- デモ版では最初の10駅のみ経路情報を収集（main.pyの`.head(10)`を削除で全駅対象）

## トラブルシューティング

### 路線名マッチングエラー

`line_mapping.py`のマッピング辞書を確認・更新

### 経路情報が取得できない

- Ekispert APIキーを確認
- 駅名が正しく認識されているか確認

### Webアプリでデータが表示されない

- `data/stations_complete.csv`が生成されているか確認
- ブラウザのコンソールでエラーを確認