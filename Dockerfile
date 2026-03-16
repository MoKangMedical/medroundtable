FROM python:3.11-slim

WORKDIR /app

# 安装依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY backend/ ./backend/
COPY agents/ ./agents/
COPY skills/ ./skills/
COPY config/ ./config/

# 复制依赖文件
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 创建数据目录
RUN mkdir -p /app/data

# 暴露端口
EXPOSE 8000

# 设置环境变量
ENV PYTHONPATH=/app
ENV PORT=8000
ENV HOST=0.0.0.0
ENV DEBUG=false
ENV DATABASE_URL=sqlite:///app/data/medroundtable.db
ENV SECRET_KEY=0a1267066319f509476a44ea41c17798df616b97f93882b7d5e6ed88c065b475
ENV SECONDME_CLIENT_ID=19b5f08b-2256-41aa-b196-2f98491099f7
ENV SECONDME_CLIENT_SECRET=f9f406e3d8dc4fe8e8363853865e1afea2957e7b0a33d75e96cbc5a22c4c20f3
ENV SECONDME_REDIRECT_URI=http://localhost:8000/api/auth/callback
ENV SECONDME_API_BASE=https://api.mindverse.com/gate/lab
ENV CORS_ORIGINS=*

# 启动命令
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
