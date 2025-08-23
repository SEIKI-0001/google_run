# 1. ベースイメージとしてPython 3.9（または任意のバージョン）を使用
FROM python:3.9-slim

# 2. 作業ディレクトリを設定
WORKDIR /app

# 3. ローカルのファイルをコンテナにコピー
COPY ./requirements.txt /app/requirements.txt
COPY ./sample_hello.py /app/sample_hello.py

# 4. 依存パッケージのインストール
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# 5. UvicornでFastAPIを実行
CMD ["uvicorn", "sample_hello:app", "--host", "0.0.0.0", "--port", "8080"]
