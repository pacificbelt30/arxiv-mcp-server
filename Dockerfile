# Python 3.11をベースイメージとして使用（pyproject.tomlの要件に合わせて）
FROM python:3.11-slim

# システム依存関係のインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# uvのコピー
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# データ永続化のディレクトリを作成
RUN mkdir -p /data/papers && chmod 777 /data/papers

# 環境変数の設定
ENV PYTHONUNBUFFERED=1 \
    ARXIV_STORAGE_PATH=/data/papers

# アプリケーションのコピー
COPY . /app
WORKDIR /app

# uvで依存関係をインストール
RUN uv sync --frozen --no-cache

# .venvディレクトリへのアクセス権を確保
RUN chmod -R 755 /app/.venv/bin

# ボリュームの設定
VOLUME ["/data/papers"]

# エントリポイントスクリプトの作成
RUN echo '#!/bin/bash\n/app/.venv/bin/python -m arxiv_mcp_server "$@"' > /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# MCPプロトコル用のエントリポイント設定
ENTRYPOINT ["/app/entrypoint.sh"]
