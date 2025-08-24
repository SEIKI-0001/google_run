# 1. ベースイメージ
FROM python:3.9-slim

# 追加: なくても動くけど、ログ/キャッシュまわりを安定化
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# 2. 作業ディレクトリ
WORKDIR /app

# 3. 依存ファイル→アプリの順にコピー（キャッシュ効かせる）
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# 4. アプリ本体
COPY ./sample_hello.py /app/sample_hello.py

# 5. 起動コマンド（Cloud Run の $PORT を使う）
CMD ["uvicorn", "sample_hello:app", "--host", "0.0.0.0", "--port", "8080"]
