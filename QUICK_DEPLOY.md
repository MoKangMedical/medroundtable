# MedRoundTable - 快速部署指南

## 🚀 三种部署方案

### 方案一：Docker Compose（推荐，最简单）

```bash
# 1. 进入项目目录
cd /root/.openclaw/workspace/medroundtable

# 2. 使用 Docker Compose 启动
docker-compose up -d

# 3. 访问
# 前端: http://localhost:3000
# API: http://localhost:8000
```

---

### 方案二：Vercel + Railway（免费托管）

#### 前端部署到 Vercel

1. 访问 https://vercel.com/new
2. 导入 GitHub 仓库
3. 配置：
   - Framework: `Other`
   - Build Command: (空)
   - Output Directory: `frontend`
4. 部署

#### 后端部署到 Railway

1. 访问 https://railway.app/new
2. 选择 "Deploy from GitHub repo"
3. 添加环境变量：
   ```
   OPENAI_API_KEY=your_key_here
   MOONSHOT_API_KEY=your_key_here
   SECRET_KEY=random_string
   ```
4. 自动生成域名

5. 修改前端 `frontend/index.html` 中的 API 地址

---

### 方案三：Render（完全免费）

#### 部署 Web Service（后端）

1. 访问 https://dashboard.render.com/select-repo?type=web
2. 连接 GitHub 仓库
3. 填写配置：
   - **Name**: `medroundtable-api`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4. 点击 "Create Web Service"
5. 添加环境变量（在 Settings → Environment）

#### 部署 Static Site（前端）

1. 点击 "New Static Site"
2. 选择同一仓库
3. 配置：
   - **Name**: `medroundtable`
   - **Build Command**: (空)
   - **Publish Directory**: `frontend`
4. 部署

---

## 🔧 当前服务器部署

### 使用 ngrok（临时访问）

```bash
# 安装 ngrok
curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc | \
  sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && \
  echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | \
  sudo tee /etc/apt/sources.list.d/ngrok.list && \
  sudo apt update && sudo apt install ngrok

# 配置 token (从 https://dashboard.ngrok.com/get-started/your-authtoken 获取)
ngrok config add-authtoken YOUR_AUTHTOKEN

# 启动隧道
ngrok http 3000
```

访问 ngrok 提供的 HTTPS 链接即可。

---

### 使用 Nginx + 域名（生产环境）

```bash
# 安装 Nginx
sudo apt update && sudo apt install -y nginx

# 复制配置
sudo cp nginx.conf /etc/nginx/sites-available/medroundtable
sudo ln -s /etc/nginx/sites-available/medroundtable /etc/nginx/sites-enabled/

# 修改配置中的域名
sudo nano /etc/nginx/sites-available/medroundtable

# 测试并重载
sudo nginx -t
sudo systemctl reload nginx

# 申请 SSL 证书 (使用 certbot)
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 📋 环境变量说明

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `OPENAI_API_KEY` | OpenAI API Key | 可选 |
| `MOONSHOT_API_KEY` | Moonshot API Key | 可选 |
| `SECRET_KEY` | JWT 密钥 | 是 |
| `DEBUG` | 调试模式 | 否 |

---

## 🌐 访问地址

部署完成后：

- **前端界面**: 根据平台分配的域名
- **API 文档**: `{backend-url}/docs`
- **API 端点**: `{backend-url}/api/v1`

---

## 💡 提示

1. **免费额度**：
   - Vercel: 无限带宽
   - Railway: $5/月免费额度
   - Render: 免费套餐足够初期使用

2. **生产环境建议**：
   - 使用 PostgreSQL 替代内存存储
   - 配置 Redis 缓存
   - 添加监控和日志

3. **遇到问题？**
   - 查看平台日志
   - 检查环境变量配置
   - 确认 CORS 设置正确
