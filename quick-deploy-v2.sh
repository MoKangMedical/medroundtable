#!/bin/bash
# MedRoundTable V2.0 一键部署

echo "🚀 MedRoundTable V2.0 部署脚本"
echo "================================"

# 检查环境
echo "📋 检查环境..."
python3 --version
pip3 --version

# 进入目录
cd /root/.openclaw/workspace/medroundtable

# 安装依赖
echo "📦 安装依赖..."
pip3 install -q fastapi uvicorn pydantic bcrypt PyJWT

# 设置环境变量
export SECRET_KEY="medroundtable-v2-$(date +%s)"
export ACCESS_TOKEN_EXPIRE_DAYS="7"

# 检查端口
echo "🔍 检查端口..."
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "🔄 端口8000被占用，尝试停止旧服务..."
    pkill -f "uvicorn.*main:app" 2>/dev/null
    sleep 2
fi

# 启动服务
echo "🚀 启动服务..."
nohup python3 -m uvicorn backend.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    > /tmp/medroundtable.log 2>&1 &

sleep 3

# 检查状态
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo ""
    echo "✅ 部署成功!"
    echo ""
    echo "🌐 访问地址:"
    echo "  本地: http://localhost:8000"
    echo "  远程: http://43.134.3.158:8000"
    echo ""
    echo "📚 API文档:"
    echo "  Swagger: http://43.134.3.158:8000/docs"
    echo "  ReDoc:   http://43.134.3.158:8000/redoc"
    echo ""
    echo "🔧 测试账号:"
    echo "  管理员: admin@medroundtable.com / admin123"
    echo "  研究员: researcher@medroundtable.com / research123"
else
    echo "❌ 启动失败，查看日志:"
    tail -20 /tmp/medroundtable.log
fi
