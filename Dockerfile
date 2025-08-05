# Python + ffmpeg インストール済みの環境を構築
FROM python:3.11-slim

# ffmpeg をインストール
RUN apt-get update && apt-get install -y ffmpeg

# 作業ディレクトリの作成
WORKDIR /app

# 依存ファイルのコピーとインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリのソースコードをコピー
COPY . .

# Webアプリを起動（例：FastAPI + uvicorn）
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]