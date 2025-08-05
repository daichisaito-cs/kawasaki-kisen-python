FROM python:3.11.10
USER root

WORKDIR /app
COPY . /app

RUN pip install --upgrade -r /app/requirements.txt # pythonのライブラリはrequirements.txtに記述します。

RUN apt-get update # ffmpegをビルド済みバイナリでinstallします。
RUN apt-get install -y ffmpeg

# Webアプリを起動（例：FastAPI + uvicorn）
CMD ["python", "main.py"]