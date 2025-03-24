# Python公式イメージをベースにする
FROM python:3.9

# 作業ディレクトリ設定
WORKDIR /app

# 依存パッケージ
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ソースコードをコピー
COPY . .

# コンテナ起動時のポート設定（Flaskは5000を使う）
EXPOSE 5000

# Docker Compose で "command" 指定するため、CMDは省略してもOK
