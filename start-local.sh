#!/bin/bash
# MedRoundTable - 本地快速启动脚本（无需网络）
# 用法: ./start-local.sh

echo "🚀 MedRoundTable 本地启动"
echo "=========================="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未检测到 Python3，请安装 Python 3.8+"
    echo "下载地址: https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python3 已安装"

# 创建临时目录
TEMP_DIR="/tmp/medroundtable-local"
mkdir -p $TEMP_DIR

# 复制前端文件
echo "📁 准备前端文件..."
FRONTEND_DIR="$(dirname "$0")/frontend"

# 创建简单的 HTTP 服务器
cat > $TEMP_DIR/server.py << 'EOF'
#!/usr/bin/env python3
import http.server
import socketserver
import os
import sys

PORT = 8080
DIRECTORY = sys.argv[1] if len(sys.argv) > 1 else "."

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

os.chdir(DIRECTORY)

with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    print(f"🌐 服务启动成功!")
    print(f"📍 本地访问: http://localhost:{PORT}")
    print(f"📱 局域网访问: http://$(hostname -I | awk '{print $1}'):{PORT}")
    print("")
    print("按 Ctrl+C 停止服务")
    print("")
    httpd.serve_forever()
EOF

# 启动服务器
echo "🌐 启动本地服务器..."
echo ""
python3 $TEMP_DIR/server.py $FRONTEND_DIR
