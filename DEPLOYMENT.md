# MedRoundTable - Vercel + Railway 部署配置

## 快速部署方案

### 方案1: Vercel (前端) + Railway (后端)

#### 1. 部署前端到 Vercel

1. 访问 https://vercel.com
2. 点击 "Add New Project"
3. 导入你的 GitHub 仓库
4. 配置:
   - Framework: Other
   - Build Command: 空
   - Output Directory: frontend
   - Install Command: 空

#### 2. 部署后端到 Railway

1. 访问 https://railway.app
2. 点击 "New Project" → "Deploy from GitHub repo"
3. 选择仓库
4. 添加环境变量:
   ```
   OPENAI_API_KEY=your_key
   MOONSHOT_API_KEY=your_key
   SECRET_KEY=random_secret
   ```
5. 自动生成域名

#### 3. 配置 CORS

修改 backend/main.py 中的 CORS 配置，添加 Vercel 域名:
```python
allow_origins=["https://your-vercel-app.vercel.app"]
```

---

### 方案2: Render (推荐 - 免费且稳定)

#### 部署后端到 Render

1. 访问 https://render.com
2. 点击 "New Web Service"
3. 连接 GitHub 仓库
4. 配置:
   - Name: medroundtable-api
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. 添加环境变量
6. 免费套餐即可

#### 部署前端到 Render Static Site

1. 点击 "New Static Site"
2. 连接同一仓库
3. 配置:
   - Build Command: 空
   - Publish Directory: frontend
4. 设置环境变量指向后端 URL

---

### 方案3: Cloudflare Pages + Workers (最佳性能)

#### 前端部署到 Pages

1. 访问 https://dash.cloudflare.com
2. 进入 Pages → "Create a project"
3. 连接 GitHub
4. 构建设置:
   - Build command: 空
   - Build output: frontend

#### 后端使用 Workers

1. 创建 Worker
2. 使用 wrangler 部署 Python 后端
3. 或使用 Cloudflare Tunnel 连接现有后端

---

### 方案4: 免费服务器 (VPS) - 当前方案

使用已有的腾讯云/阿里云轻量服务器:

```bash
# 安装 PM2 进程管理器
npm install -g pm2

# 创建 PM2 配置文件
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [
    {
      name: 'medroundtable-api',
      script: 'backend/main.py',
      interpreter: 'python3',
      env: {
        PYTHONPATH: '/root/.openclaw/workspace/medroundtable',
        PORT: 8000
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M'
    },
    {
      name: 'medroundtable-web',
      script: 'python3',
      args: '-m http.server 3000',
      cwd: '/root/.openclaw/workspace/medroundtable/frontend',
      instances: 1,
      autorestart: true
    }
  ]
};
EOF

# 启动
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

---

## 当前推荐: 使用 Nginx 反向代理 + 域名

如果你有域名，最佳方案是:

1. 绑定域名到服务器
2. 配置 Nginx:

```nginx
server {
    listen 80;
    server_name medroundtable.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
    }
}
```

3. 申请 SSL 证书

---

## 立即访问方案

当前服务器已配置，可以通过以下方式访问:

1. **直接访问** (需要服务器IP):
   - http://YOUR_SERVER_IP:3000
   - http://YOUR_SERVER_IP:8000

2. **使用 Cloudflare Tunnel** (临时):
   ```bash
   cloudflared tunnel --url http://localhost:3000
   ```

3. **使用 ngrok** (推荐):
   ```bash
   # 安装 ngrok
   curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
   echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
   sudo apt update && sudo apt install ngrok
   
   # 配置 authtoken (从 https://dashboard.ngrok.com 获取)
   ngrok config add-authtoken YOUR_TOKEN
   
   # 启动
   ngrok http 3000
   ```
