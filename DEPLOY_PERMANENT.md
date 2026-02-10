# MedRoundTable - 永久部署方案 (24/7 全球访问)

## 🎯 推荐架构

```
┌─────────────────┐         ┌──────────────────┐
│   Vercel        │ ──────▶ │    Railway       │
│  (前端托管)      │         │   (后端API)       │
│  全球CDN加速     │         │  + PostgreSQL    │
└─────────────────┘         └──────────────────┘
       ↑                              ↑
   自动部署                       自动部署
  GitHub推送                      GitHub推送
```

---

## 📋 部署前准备

1. **GitHub 账号** - 存储代码
2. **Vercel 账号** - 前端托管 (免费)
3. **Railway 账号** - 后端托管 (免费 $5/月额度)
4. **API Key** - Moonshot/OpenAI (用于AI功能)

---

## 🚀 第一步：准备代码

### 1. 修改前端 API 地址

编辑 `frontend/index.html`，找到 `API_BASE` 变量：

```javascript
// 第 ~145 行
// 修改为 Railway 部署后的域名
const API_BASE = 'https://medroundtable-api.up.railway.app/api/v1';
```

### 2. 创建数据库配置

创建 `backend/database.py`：

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Railway 会自动提供 DATABASE_URL
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://user:password@localhost/medroundtable"
)

# 处理 Railway 的 postgres:// 前缀
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 3. 更新后端 CORS

修改 `backend/main.py`，更新 CORS 配置：

```python
# 第 ~18 行
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://medroundtable.vercel.app",  # Vercel 域名
        "http://localhost:3000",              # 本地开发
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🚀 第二步：部署后端到 Railway

### 方式 A：通过 Railway CLI (推荐)

```bash
# 1. 安装 Railway CLI
npm install -g @railway/cli

# 2. 登录
railway login

# 3. 初始化项目
cd /root/.openclaw/workspace/medroundtable
railway init
# 选择 "Empty Project"
# 项目名称: medroundtable-api

# 4. 创建 PostgreSQL 数据库
railway add --database postgres

# 5. 设置环境变量
railway variables set SECRET_KEY="your-secret-key-here"
railway variables set MOONSHOT_API_KEY="your-moonshot-key"
railway variables set OPENAI_API_KEY="your-openai-key"

# 6. 部署
railway up

# 7. 获取域名
railway domain
# 输出类似: https://medroundtable-api.up.railway.app
```

### 方式 B：通过 Railway 网页界面

1. 访问 https://railway.app/new
2. 选择 "Deploy from GitHub repo"
3. 连接你的 GitHub 账号
4. 选择 `medroundtable` 仓库
5. 点击 "Add Variables"：
   - `SECRET_KEY` = 随机字符串
   - `MOONSHOT_API_KEY` = 你的 Moonshot API Key
   - `OPENAI_API_KEY` = 你的 OpenAI API Key (可选)
6. 点击 "Deploy"
7. 等待部署完成，记录分配的域名

---

## 🚀 第三步：部署前端到 Vercel

### 方式 A：Vercel CLI

```bash
# 1. 安装 Vercel CLI
npm install -g vercel

# 2. 登录
vercel login

# 3. 部署
cd /root/.openclaw/workspace/medroundtable
vercel --prod

# 4. 按提示操作:
# ? Set up and deploy "~/medroundtable"? [Y/n] Y
# ? Which scope do you want to deploy to? [你的账号]
# ? Link to existing project? [n]
# ? What's your project name? [medroundtable]
```

### 方式 B：Vercel 网页界面

1. 访问 https://vercel.com/new
2. 导入 GitHub 仓库
3. 配置：
   - **Framework Preset**: `Other`
   - **Build Command**: (留空)
   - **Output Directory**: `frontend`
   - **Install Command**: `pip install -r requirements.txt` (可选)
4. 点击 "Deploy"
5. 等待部署完成，获得域名如 `https://medroundtable.vercel.app`

---

## 🚀 第四步：GitHub 自动化部署

### 1. 创建 GitHub 仓库

```bash
cd /root/.openclaw/workspace/medroundtable
git init
git add .
git commit -m "Initial commit - MedRoundTable A2A Platform"
git branch -M main

# 创建 GitHub 仓库后 (在 github.com/new)
git remote add origin https://github.com/你的用户名/medroundtable.git
git push -u origin main
```

### 2. 连接 Vercel

- 访问 https://vercel.com/dashboard
- 点击 "Add New..." → "Project"
- 选择 `medroundtable` 仓库
- 点击 "Import"
- 确认配置后点击 "Deploy"

### 3. 连接 Railway

- 访问 https://railway.app/dashboard
- 点击 "New" → "Project"
- 选择 "Deploy from GitHub repo"
- 选择 `medroundtable` 仓库

---

## ✅ 部署完成检查清单

- [ ] Railway 后端运行正常 (访问 /health 检查)
- [ ] Vercel 前端可以访问
- [ ] 前端能正确调用后端 API
- [ ] 创建圆桌会功能正常
- [ ] AI Agent 可以正常交互

---

## 🔧 故障排除

### 问题1: CORS 错误

**解决**: 确保后端 `allow_origins` 包含 Vercel 域名

### 问题2: 数据库连接失败

**解决**: 
```bash
# Railway 中检查数据库状态
railway status

# 重新生成数据库 URL
railway connect postgres
```

### 问题3: 环境变量未生效

**解决**:
```bash
# Railway 中查看变量
railway variables

# 重新设置
railway variables set KEY=value
railway up
```

---

## 💰 费用说明

| 服务 | 免费额度 | 超出费用 |
|------|---------|---------|
| Vercel | 无限带宽，100GB/月 | $0.40/GB |
| Railway | $5/月，512MB RAM | 按需计费 |
| PostgreSQL | 500MB 存储 | $0.015/GB/月 |

**结论**: 小项目完全免费！

---

## 🌍 全球加速

Vercel 自动提供全球 CDN：
- 🇨🇳 亚洲：新加坡、东京、香港节点
- 🇪🇺 欧洲：伦敦、法兰克福节点  
- 🇺🇸 美洲：旧金山、纽约节点

Railway 支持多区域部署：
- 默认 US West (俄勒冈)
- 可选 EU West (爱尔兰)
- 可选 Asia Southeast (新加坡)

---

## 🔐 安全配置

1. **API Key 保护**: 只在 Railway 环境变量中存储
2. **HTTPS**: Vercel 和 Railway 自动提供 SSL
3. **CORS**: 只允许特定域名访问
4. **Rate Limiting**: 添加请求限制防止滥用

---

## 📞 需要帮助？

部署过程中遇到问题，随时告诉我！我可以：
1. 帮你检查配置
2. 查看部署日志
3. 优化性能
4. 添加监控

现在就开始部署吧！🚀
