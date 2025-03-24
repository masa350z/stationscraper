# stationscraper

このリポジトリは関東エリアを中心とした「路線・駅情報」や「家賃相場」「目的地までの所要時間」などをスクレイピングおよびAPI連携を通じて取得し、データを加工・可視化するサンプルプロジェクトです。

## 概要

### スクレイピング処理
- TravelTowns や SUUMO を対象に、路線・駅マスタや家賃相場情報を取得します。

### API連携
- Ekispert API で駅間の所要時間・乗り換え回数を取得
- Google Maps Geocoding API で駅ごとの緯度経度を取得

### データ加工・分析
- 取得したデータをマージし、時間や家賃などの条件でフィルタや可視化を実施

## 主な機能

### 駅リストの取得
- `src/scrapers/traveltowns_scraper.py` を用いて関東エリアの路線・駅リストを取得

### 家賃相場の取得
- `src/scrapers/suumo_scraper.py` を用いて SUUMO から駅ごとの家賃相場をスクレイピング

### 所要時間の取得
- `src/apis/ekispert.py` を介して Ekispert API から駅間の所要時間・乗り換え回数を取得

### 緯度経度の取得
- `src/apis/google_maps.py` を介して Google Maps Geocoding API から駅の座標情報を取得

### データマージとフィルタ
- `src/pipeline/data_cleaning.py` で複数のCSVを結合し、所要時間や家賃に応じたデータフィルタリング処理を実行

### 簡易的な分析と可視化
- `src/pipeline/analysis.py` で条件別にCSVを分割保存
- `src/pipeline/visualization.py` で散布図を描画

## ディレクトリ構成

```
stationscraper
├── .env                  # APIキーなどを管理する環境変数ファイル(手動で作成)
├── .gitignore            # Git向けの無視リスト
├── data
│   ├── line_url.csv
│   ├── output
│   │   ├── route_info_乃木坂.csv
│   │   ├── route_info_六本木.csv
│   │   ├── ... (省略)
│   │   └── temp
├── requirements.txt      # 必要なPythonパッケージ
└── src
    ├── apis
    │   ├── analysis.py
    │   ├── ekispert.py
    │   ├── google_maps.py
    │   └── visualization.py
    ├── config.py
    ├── main.py           # メイン処理エントリーポイント
    ├── pipeline
    │   ├── analysis.py
    │   ├── data_cleaning.py
    │   └── visualization.py
    └── scrapers
        ├── suumo_scraper.py
        └── traveltowns_scraper.py
```

## 主要ファイル説明

### `src/main.py`
- 全体の実行フローをまとめたエントリーポイント

### `src/scrapers/`
- `traveltowns_scraper.py`: TravelTowns から関東の駅マスタをスクレイピング
- `suumo_scraper.py`: SUUMO から沿線別・駅別の家賃相場をスクレイピング

### `src/apis/`
- `ekispert.py`: Ekispert API で正式駅名や所要時間を取得
- `google_maps.py`: Google Maps Geocoding API で各駅の緯度経度を取得
- `analysis.py`, `visualization.py`: API連携や簡易解析（未実装 or サンプル）

### `src/pipeline/`
- `data_cleaning.py`: 駅マスタと家賃を結合、時間・家賃フィルタや徒歩時間加算などの処理
- `analysis.py`: フィルタ後のデータを条件ごとに分析・分割保存
- `visualization.py`: 散布図など可視化に関連する処理

### `src/config.py`
- 環境変数のロードやプロジェクトで利用する各種定数（APIキー、閾値など）を設定

## セットアップ

### リポジトリをクローン
```bash
git clone https://github.com/xxx/stationscraper.git
cd stationscraper
```

### Python環境の準備
仮想環境 (venv) の使用を推奨します。
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

### APIキーの設定 (.env ファイル作成)
`.env` ファイルに以下のように記載します。
```dotenv
EKISPERT_KEY=YOUR_EKISPERT_API_KEY
GOOGLE_MAPS_KEY=YOUR_GOOGLE_MAPS_API_KEY
```

### データディレクトリの確認
- プロジェクト直下に `data` ディレクトリが必要です。
- スクレイピング結果や処理済みCSVは `data/output` 以下に保存されます。

## 使い方

### メインスクリプトの実行
```bash
python src/main.py
```
- `traveltowns_scraper.py`: 路線・駅マスタ取得
- `suumo_scraper.py`: 家賃相場取得
- データマージ後、目的地までの所要時間を `ekispert.py` で取得
- 徒歩時間を加算し、CSV出力およびデータフィルタリングなどのサンプル処理実行

### パラメータ変更
- `src/config.py` の `MAX_TIME_DEFAULT` や `ROOM_TYPE` などを変更可能
- `WALK_MINUTES` を調整して目的地の駅数や徒歩時間を設定

### 拡張
- `pipeline` 以下のスクリプトを修正し、家賃以外に「築年数」や「部屋サイズ」などを追加分析可能
- `apis/visualization.py` と連携し、Folium などの地図表示ツールとの組み合わせも検討可能

## 注意事項

### API利用制限
- Ekispert API, Google Maps Geocoding API は無料枠・使用制限あり
- 本格運用の際は課金プランや上限を確認してください

### スクレイピング
- 公共データ取得を目的としたサンプルですが、対象サイトの負荷や利用規約に留意してください
