# MedRoundTable V2.0 - 立即部署方案

## 🚀 方案1: Zeabur部署 (推荐，最快)

### 步骤1: 登录Zeabur
```bash
# 访问 https://zeabur.com
# 用GitHub账号登录
```

### 步骤2: 创建项目
```
1. 点击 "Create Project"
2. 选择 "Deploy your source code"
3. 授权GitHub访问
4. 选择 MoKangMedical/medroundtable 仓库
5. 选择 main 分支
```

### 步骤3: 配置环境变量
在Zeabur控制台添加：
```
SECRET_KEY=medroundtable-v2-secret-key-change-this
ACCESS_TOKEN_EXPIRE_DAYS=7
```

### 步骤4: 绑定域名
```
1. 项目设置 → Domains
2. 点击 "Generate Domain" 或使用自定义域名
3. 等待SSL证书自动配置
```

**预计时间**: 5分钟

---

## 🚀 方案2: Railway部署

### 步骤1: 登录Railway
```bash
# 访问 https://railway.app
# 用GitHub登录
```

### 步骤2: 部署
```
1. New Project → Deploy from GitHub repo
2. 选择 medroundtable
3. 自动检测Python项目
```

### 步骤3: 配置
已包含 `railway.json`，自动配置：
- 构建: `pip install -r requirements.txt`
- 启动: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

**预计时间**: 3分钟

---

## 🚀 方案3: Render部署

### 步骤1: 登录Render
```bash
# 访问 https://render.com
```

### 步骤2: 创建Web Service
```
1. New → Web Service
2. 连接GitHub仓库
3. 配置:
   - Name: medroundtable-v2
   - Region: Singapore (closest to China)
   - Branch: main
   - Runtime: Python 3
   - Build Command: pip install -r requirements.txt
   - Start Command: python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

### 步骤3: 环境变量
```
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_DAYS=7
```

**预计时间**: 5分钟

---

## 🚀 方案4: 服务器直接部署 (当前机器)

### 快速启动脚本
```bash
#!/bin/bash
# 保存为 deploy.sh

cd /root/.openclaw/workspace/medroundtable

# 安装依赖
pip3 install -r requirements.txt

# 设置环境变量
export SECRET_KEY="medroundtable-v2-production-secret"
export ACCESS_TOKEN_EXPIRE_DAYS="7"

# 启动服务
pkill -f "uvicorn.*main:app" 2>/dev/null
sleep 1

nohup python3 -m uvicorn backend.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  > /var/log/medroundtable.log 2>&1 &

echo "✅ MedRoundTable V2.0 已启动"
echo "📍 访问: http://43.134.3.158:8000"
echo "📚 API文档: http://43.134.3.158:8000/docs"
```

### 配置Nginx (生产环境)
```nginx
# /etc/nginx/sites-available/medroundtable
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

---

## 🔧 一键部署脚本

已创建: `quick-deploy-v2.sh`

```bash
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
    echo ""
    echo "📊 功能列表:"
    echo "  - 997项技能市场"
    echo "  - 40+数据库浏览器"
    echo "  - 临床试验设计器"
    echo "  - 自研认证系统"
else
    echo "❌ 启动失败，查看日志:"
    tail -20 /tmp/medroundtable.log
fi
```

---

## 📋 部署检查清单

### 部署前
- [ ] 代码已推送到GitHub
- [ ] requirements.txt 完整
- [ ] 环境变量已配置
- [ ] 域名已准备 (可选)

### 部署后
- [ ] API响应正常
- [ ] 登录功能测试
- [ ] 技能市场可访问
- [ ] 数据库浏览器可用
- [ ] 文档页面正常

---

## 🆘 故障排除

### 问题1: 端口被占用
```bash
# 查看占用
lsof -i :8000

# 释放端口
pkill -f "uvicorn"
```

### 问题2: 依赖安装失败
```bash
# 升级pip
pip3 install --upgrade pip

# 单独安装
pip3 install fastapi uvicorn pydantic bcrypt PyJWT
```

### 问题3: 数据库错误
```bash
# 检查数据库文件
ls -la data/

# 重新初始化
python3 -c "from backend.database import init_db; init_db()"
```

---

## 🎯 推荐部署顺序

1. **立即测试** → 在当前服务器运行一键部署脚本
2. **短期** → 部署到 Zeabur (免费 + 稳定)
3. **长期** → 配置自定义域名 + HTTPS

---

**选择方案后告诉我，紫霞帮你执行！** 🌸💜
