# 🚀 MedRoundTable 后端云部署 - 方案对比

## 📍 当前状态

| 服务 | 地址 | 状态 |
|------|------|------|
| 前端 (Vercel) | https://medroundtable-v2.vercel.app | ✅ 已上线 |
| 后端 (当前服务器) | http://43.134.3.158:8001 | ✅ 健康运行 |
| GitHub | https://github.com/MoKangMedical/medroundtable | ✅ 最新代码已推送 |

---

## 🎯 后端部署方案（选择最适合你的）

### 方案 A：Railway（推荐 ⭐⭐⭐）
- **优点**: 最简单，自动 HTTPS，Python 原生支持
- **缺点**: 需要浏览器登录授权
- **免费额度**: 每月 $5 或 500 小时
- **适合**: 快速上线，不想维护服务器

```bash
# 步骤
npm install -g @railway/cli
railway login
./deploy-railway.sh
```

---

### 方案 B：Render（推荐 ⭐⭐）
- **优点**: 免费额度充足 (750小时)，稳定
- **缺点**: 自动休眠（15分钟无访问后休眠，首次访问需等待唤醒）
- **免费额度**: 每月 750 小时
- **适合**: 预算有限，能接受偶尔延迟

**一键部署**: 
1. 访问 https://render.com
2. 点击 "New Web Service"
3. 选择 GitHub 仓库 `MoKangMedical/medroundtable`
4. 配置:
   - Name: `medroundtable-api`
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. 添加环境变量（见下方）
6. 点击 "Create Web Service"

---

### 方案 C：Fly.io（推荐 ⭐⭐）
- **优点**: 全球边缘节点，性能优秀
- **缺点**: 配置稍复杂
- **免费额度**: 每月 $5 额度
- **适合**: 全球用户，追求性能

```bash
# 步骤
curl -L https://fly.io/install.sh | sh
fly auth login
fly launch --name medroundtable-api
fly deploy
```

---

### 方案 D：当前服务器 + Nginx + Let's Encrypt（推荐 ⭐⭐⭐）
- **优点**: 保持现有服务器，完全控制，免费
- **缺点**: 需要域名，需要手动配置
- **成本**: 仅域名费用 (~$10/年)
- **适合**: 已有域名，想完全控制

```bash
# 步骤
./setup-https.sh
# 按提示输入域名，自动申请 SSL 证书
```

---

### 方案 E：当前服务器 + Cloudflare Tunnel（推荐 ⭐⭐）
- **优点**: 保持现有服务器，免费 HTTPS，无需域名
- **缺点**: 需要 Cloudflare 账号
- **成本**: 免费
- **适合**: 不想买域名，快速获得 HTTPS

```bash
# 步骤 1: 登录 Cloudflare
cloudflared tunnel login

# 步骤 2: 运行配置脚本
./setup-cloudflare-tunnel.sh
```

---

## ⚙️ 必需环境变量

无论选择哪个平台，都需要设置以下环境变量：

```bash
# 核心配置
SECRET_KEY=your-random-secret-key-here  # 用于 JWT 加密
DEBUG=false

# 数据库（默认 SQLite）
DATABASE_URL=sqlite:///app/data/medroundtable.db

# CORS（允许的前端域名）
CORS_ORIGINS=https://medroundtable-v2.vercel.app,https://app.secondme.io

# AI API Keys（根据需要配置）
OPENAI_API_KEY=sk-...
GLM_API_KEY=...
```

---

## 🔄 部署后更新清单

### 1. 更新 Second Me Manifest
编辑 `secondme-manifest.json`：
```json
{
  "interfaces": {
    "api": {
      "base_url": "https://your-new-domain.com"
    }
  }
}
```
然后重新上传到 Second Me 平台。

### 2. 更新 Vercel 前端环境变量
在 Vercel 控制台设置：
```bash
NEXT_PUBLIC_API_URL=https://your-new-domain.com
```

### 3. 测试连接
```bash
# 测试健康检查
curl https://your-new-domain.com/health

# 测试 A2A Discovery
curl https://your-new-domain.com/api/a2a/discovery
```

---

## 💡 我的建议

| 你的情况 | 推荐方案 | 预计时间 |
|----------|----------|----------|
| 想最快上线 | **Railway** | 5 分钟 |
| 不想花一分钱 | **Render** | 10 分钟 |
| 已有域名 | **Nginx + Let's Encrypt** | 15 分钟 |
| 全球用户 | **Fly.io** | 10 分钟 |
| 不想迁移 | **Cloudflare Tunnel** | 10 分钟 |

---

## 🚀 最快上手（Railway）

```bash
# 1. 安装 CLI
npm install -g @railway/cli

# 2. 登录（需要浏览器）
railway login

# 3. 一键部署
cd /root/.openclaw/workspace/medroundtable
./deploy-railway.sh

# 4. 获取域名
railway domain
# 输出: https://medroundtable-api.up.railway.app
```

---

## 📞 需要帮助？

如果遇到问题：
1. 检查后端服务是否运行: `curl http://localhost:8001/health`
2. 查看部署日志: `railway logs` (或对应平台的日志)
3. 确认环境变量已正确设置

随时找我帮忙！🎉
