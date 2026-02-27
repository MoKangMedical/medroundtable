#!/bin/bash
# Zeabur 部署一键准备脚本
# 运行后，你只需复制粘贴到 Zeabur

echo "🚀 准备 Zeabur 部署配置..."

# 创建 zeabur 部署配置目录
mkdir -p .zeabur

# 创建完整的 zeabur.json
cat > zeabur.json << 'EOF'
{
  "build": {
    "type": "python"
  },
  "start": {
    "cmd": "uvicorn backend.main:app --host 0.0.0.0 --port 8080"
  },
  "env": {
    "PYTHON_VERSION": "3.11"
  }
}
EOF

# 创建启动脚本
cat > start.sh << 'EOF'
#!/bin/bash
# 确保数据目录存在
mkdir -p data
# 启动应用
uvicorn backend.main:app --host 0.0.0.0 --port 8080
EOF
chmod +x start.sh

echo "✅ 配置完成！"
echo ""
echo "📋 请按以下步骤操作："
echo ""
echo "1. 打开 https://zeabur.com"
echo "2. 用 GitHub 登录"
echo "3. 创建项目 → 从 GitHub 导入 → 选择 medroundtable"
echo "4. 环境变量设置（复制以下）："
echo ""
echo "   SECRET_KEY=medroundtable-secret-key-2026"
echo "   DEBUG=false"
echo "   DATABASE_URL=sqlite:///app/data/medroundtable.db"
echo "   CORS_ORIGINS=https://medroundtable-v2.vercel.app,https://app.secondme.io,https://www.secondme.io"
echo ""
echo "5. 点击部署，等待 2-3 分钟"
echo "6. 部署成功后，在'域名'页面复制你的域名"
echo ""
echo "7. 把域名发给我，我会自动更新所有配置！"
