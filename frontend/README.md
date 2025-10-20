# frontend - 駅情報マップ Webアプリケーション

`filtered_master_toranomon_common_2k.csv` を単一のマスターデータとして動作する、完全独立型のシンプルなWebアプリケーションです。

## 特徴

- **単一CSV依存**: `filtered_master_toranomon_common_2k.csv` だけで動作
- **完全独立**: `src/`, `nxt_gen/`, `mapapp/` とは完全に独立
- **カラム名維持**: CSVのカラム名（`from`, `to`, `min`, `walk_min` 等）をそのまま使用
- **シンプル**: Flask + pandas のみ、Docker・DB不要
- **インタラクティブ**: Leaflet.js による地図表示とフィルタリング機能

## システム構成

```
frontend/
├── app.py                  # Flaskアプリケーション本体
├── config.py               # 設定ファイル（CSVパス、デフォルト値）
├── requirements.txt        # 依存パッケージ
├── README.md              # このファイル
└── templates/
    └── index.html         # 地図表示UI
```

## セットアップ

### 1. 依存パッケージのインストール

```bash
cd frontend
pip install -r requirements.txt
```

必要なパッケージ:
- Flask: Webサーバー
- pandas: CSVデータ処理

### 2. データファイルの確認

以下のCSVファイルが存在することを確認してください:

```
data/frontend_master/filtered/filtered_master_toranomon_common_2k.csv
```

CSVの必須カラム:
- `line`: 路線名
- `from`: 出発駅
- `to`: 目的地駅
- `trans`: 乗換回数
- `min`: 電車移動時間（分）
- `lat`: 緯度
- `lng`: 経度
- `price`: 家賃相場（万円）
- `walk_min`: 徒歩時間（分）

## 使い方

### アプリケーションの起動

```bash
cd frontend
python app.py
```

起動メッセージが表示されます:

```
============================================================
frontend - 駅情報マップ Webアプリケーション起動
============================================================

データソース: ../data/frontend_master/filtered/filtered_master_toranomon_common_2k.csv

ブラウザで以下のURLにアクセスしてください:
http://localhost:5002

終了するには Ctrl+C を押してください
============================================================
```

### ブラウザでアクセス

http://localhost:5002 にアクセスすると、駅情報マップが表示されます。

### 機能

#### 1. 地図表示
- 東京都心を中心とした地図
- 各駅を色分けされたマーカーで表示
  - **緑**: 家賃 8万円以下
  - **青**: 家賃 8～10万円
  - **赤**: 家賃 10万円以上

#### 2. マーカークリック
駅マーカーをクリックすると、ポップアップで詳細情報を表示:
- 駅名
- 路線名
- 目的地
- 家賃相場
- 所要時間（電車時間+徒歩時間）
- 乗換回数

#### 3. フィルタリング
ヘッダーのコントロールでデータをフィルタリング:
- **家賃上限**: 指定金額以下の駅のみ表示
- **所要時間上限**: 指定時間以内の駅のみ表示
- **乗換回数上限**: 指定回数以下の駅のみ表示

#### 4. 統計情報
右上に以下の統計が表示されます:
- 表示中の駅数 / 全体の駅数
- 平均家賃
- 平均所要時間

## API エンドポイント

### GET `/api/stations`
駅データをJSON形式で取得

**クエリパラメータ:**
- `max_price` (float): 最大家賃（万円）
- `max_time` (int): 最大所要時間（分）
- `max_trans` (int): 最大乗換回数

**レスポンス例:**
```json
[
  {
    "line": "京成本線",
    "from": "お花茶屋",
    "to": "虎ノ門",
    "lat": 35.7475917,
    "lng": 139.8401103,
    "price": 8.4,
    "trans": 1,
    "min": 46,
    "walk_min": 4,
    "total_min": 50
  }
]
```

### GET `/api/stats`
統計情報を取得

**レスポンス例:**
```json
{
  "total": 241,
  "with_price": 241,
  "avg_price": 9.2,
  "avg_time": 38.5
}
```

## 設定のカスタマイズ

`config.py` で以下の設定を変更できます:

```python
# CSVファイルパス
CSV_PATH = "..."

# フィルタリングのデフォルト値
DEFAULT_MAX_PRICE = 12.0  # 万円
DEFAULT_MAX_TIME = 60     # 分
DEFAULT_MAX_TRANS = 2     # 回

# サーバー設定
PORT = 5002
DEBUG = True

# 地図の初期表示位置
MAP_CENTER_LAT = 35.6812
MAP_CENTER_LNG = 139.7671
MAP_ZOOM = 11
```

## データ構造

### CSV形式（そのまま使用）

```csv
line,from,to,trans,min,lat,lng,price,walk_min
京成本線,お花茶屋,虎ノ門,1,46,35.7475917,139.8401103,8.4,4
```

### アプリ内部で追加される計算フィールド

- `total_min = min + walk_min` （所要時間合計）

## トラブルシューティング

### CSVファイルが見つからない

エラーメッセージ:
```
エラー: CSVファイルが見つかりません: ...
```

**解決方法:**
1. `data/frontend_master/filtered/filtered_master_toranomon_common_2k.csv` が存在するか確認
2. `config.py` の `CSV_PATH` が正しいか確認

### ポートが使用中

エラーメッセージ:
```
Address already in use
```

**解決方法:**
1. `config.py` の `PORT` を別の番号（例: 5003）に変更
2. または、既存のプロセスを終了: `lsof -ti:5002 | xargs kill -9`

### データが表示されない

**確認事項:**
1. ブラウザのコンソール（F12）でエラーを確認
2. サーバーログで `データ読み込み完了: X駅` が表示されているか確認
3. CSVファイルの形式が正しいか確認（カラム名、データ型）

## 開発者向け情報

### ファイル構成

- **app.py**: Flaskアプリケーション本体
  - CSVデータ読み込み
  - APIエンドポイント
  - フィルタリングロジック

- **config.py**: 設定ファイル
  - パス設定
  - デフォルト値
  - サーバー設定

- **templates/index.html**: フロントエンド
  - Leaflet.js による地図表示
  - フィルタリングUI
  - 統計表示

### 技術スタック

- **バックエンド**: Flask 2.0+
- **データ処理**: pandas 1.3+
- **フロントエンド**: Leaflet.js 1.9+
- **地図タイル**: OpenStreetMap

## ライセンス

個人開発プロジェクト
