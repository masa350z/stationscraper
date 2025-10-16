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