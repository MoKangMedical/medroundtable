FROM python:3.11-slim

WORKDIR /app

# 安装依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY backend/ ./backend/
COPY agents/ ./agents/

# 创建 requirements.txt
RUN echo "fastapi==0.109.0\nuvicorn[standard]==0.27.0\npydantic==2.5.0\npython-multipart==0.0.6" > requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 8000

# 设置环境变量
ENV PYTHONPATH=/app
ENV PORT=8000

# 启动命令
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
