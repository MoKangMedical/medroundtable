# 🚀 MedRoundTable 后端云部署指南

将 FastAPI 后端部署到云平台，获得 HTTPS 域名。

---

## 方案一：Railway（推荐 ⭐）

Railway 是最适合 Python FastAPI 的平台，自动 HTTPS，部署简单。

### 一键部署

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template-id)

### 手动部署步骤

#### 1. 安装 Railway CLI
```bash
npm install -g @railway/cli
```

#### 2. 登录 Railway
```bash
railway login
```

#### 3. 进入项目目录
```bash
cd /root/.openclaw/workspace/medroundtable
```

#### 4. 运行部署脚本
```bash
./deploy-railway.sh
```

或手动部署：
```bash
# 初始化项目
railway init --name medroundtable-api

# 设置环境变量
railway variables set SECRET_KEY="$(openssl rand -hex 32)"
railway variables set DEBUG="false"
railway variables set DATABASE_URL="sqlite:///app/data/medroundtable.db"
railway variables set CORS_ORIGINS="https://medroundtable-v2.vercel.app,https://app.secondme.io"

# 部署
railway up
```

#### 5. 获取域名
```bash
railway domain
```

输出示例：
```
https://medroundtable-api.up.railway.app
```

### 免费额度
- 每月 500 小时运行时间
- 512 MB RAM
- 共享 CPU
- 足够测试和小型项目使用

---

## 方案二：Render

Render 是另一个优秀的 Python 托管平台。

### 一键部署

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/MoKangMedical/medroundtable)

### 手动部署步骤

#### 1. 访问 Render
https://render.com

#### 2. 创建 New Web Service
- 选择你的 GitHub 仓库
- 选择 `medroundtable`

#### 3. 配置构建
| 设置 | 值 |
|------|-----|
| Name | medroundtable-api |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn backend.main:app --host 0.0.0.0 --port $PORT` |

#### 4. 添加环境变量
```bash
SECRET_KEY=your-random-secret-key
DEBUG=false
DATABASE_URL=sqlite:///app/data/medroundtable.db
CORS_ORIGINS=https://medroundtable-v2.vercel.app,https://app.secondme.io
```

#### 5. 部署
点击 "Create Web Service"

### 免费额度
- 每月 750 小时运行时间
- 512 MB RAM
- 自动休眠（15分钟无访问后休眠）

---

## 方案三：Fly.io（容器化）

Fly.io 适合容器化部署，全球 CDN。

### 安装 Fly CLI
```bash
curl -L https://fly.io/install.sh | sh
```

### 登录并部署
```bash
fly auth login

# 进入项目目录
cd /root/.openclaw/workspace/medroundtable

# 初始化应用
fly launch --name medroundtable-api

# 部署
fly deploy
```

### 免费额度
- 每月 $5 免费额度
- 约 256MB RAM 持续运行
- 全球边缘节点

---

## 方案四：当前服务器 + Cloudflare Tunnel（最快）

如果你不想迁移，可以给当前服务器添加 HTTPS 和域名。

### 步骤

#### 1. 安装 Cloudflared
```bash
# Linux
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
dpkg -i cloudflared-linux-amd64.deb
```

#### 2. 登录 Cloudflare
```bash
cloudflared tunnel login
```

#### 3. 创建隧道
```bash
cloudflared tunnel create medroundtable-api
```

#### 4. 配置隧道
```bash
# 编辑配置文件
nano ~/.cloudflared/config.yml
```

内容：
```yaml
tunnel: your-tunnel-id
credentials-file: /root/.cloudflared/your-tunnel-id.json

ingress:
  - hostname: api.medroundtable.com
    service: http://localhost:8001
  - service: http_status:404
```

#### 5. 运行隧道
```bash
cloudflared tunnel run medroundtable-api
```

#### 6. 设置开机启动
```bash
cloudflared service install
systemctl start cloudflared
```

---

## 🔧 部署后配置

### 1. 更新 Second Me Manifest

部署完成后，获得新域名（例如 `https://medroundtable-api.up.railway.app`），更新 `secondme-manifest.json`：

```json
{
  "interfaces": {
    "api": {
      "base_url": "https://medroundtable-api.up.railway.app"
    }
  }
}
```

### 2. 更新 Vercel 前端环境变量

```bash
NEXT_PUBLIC_API_URL=https://medroundtable-api.up.railway.app
```

### 3. 测试连接

```bash
# 测试新域名
curl https://medroundtable-api.up.railway.app/health

# 测试 A2A Discovery
curl https://medroundtable-api.up.railway.app/api/a2a/discovery
```

---

## 📊 方案对比

| 平台 | 优点 | 缺点 | 推荐场景 |
|------|------|------|----------|
| **Railway** | 部署简单，自动 HTTPS，Python 原生支持 | 免费额度有限 | ⭐ 推荐首选 |
| **Render** | 免费额度充足，稳定 | 自动休眠 | 预算有限 |
| **Fly.io** | 全球 CDN，性能优秀 | 配置稍复杂 | 全球用户 |
| **Cloudflare** | 保持当前服务器，零迁移 | 需要配置隧道 | 不想迁移 |

---

## 🚀 快速开始（推荐 Railway）

```bash
# 1. 安装 CLI
npm install -g @railway/cli

# 2. 登录
railway login

# 3. 进入项目
cd /root/.openclaw/workspace/medroundtable

# 4. 一键部署
./deploy-railway.sh

# 5. 获取域名
railway domain
```

---

## 📝 注意事项

1. **数据库**：默认使用 SQLite，生产环境建议迁移到 PostgreSQL
2. **环境变量**：确保设置 `SECRET_KEY` 和 `DEBUG=false`
3. **CORS**：确保后端 `CORS_ORIGINS` 包含前端域名
4. **API Keys**：如果使用 OpenAI/GLM，设置相应的 API Key

---

**选择最适合你的方案开始部署吧！** 🎉

有问题随时找我帮忙！
