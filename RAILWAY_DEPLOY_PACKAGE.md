# 🚀 MedRoundTable - Railway 一键部署完整包

## 📦 包含文件

| 文件 | 用途 |
|------|------|
| `deploy-railway-oneclick.sh` | 一键部署脚本 |
| `railway.toml` | Railway 配置文件 |
| `.github/workflows/deploy-railway.yml` | GitHub Actions 自动部署 |
| `RAILWAY_DEPLOY.md` | 详细部署指南 |

---

## ⚡ 快速开始（推荐）

### 方法一：一键脚本部署（2分钟）

```bash
# 1. 进入项目目录
cd /root/.openclaw/workspace/medroundtable

# 2. 给脚本执行权限
chmod +x deploy-railway-oneclick.sh

# 3. 运行一键部署
./deploy-railway-oneclick.sh
```

脚本会自动：
- ✅ 检查并安装 Railway CLI
- ✅ 登录 Railway
- ✅ 创建项目
- ✅ 配置所有环境变量
- ✅ 部署后端 API
- ✅ 获取域名

### 方法二：手动 Railway Dashboard 部署

参考 `RAILWAY_DEPLOY.md` 详细步骤

### 方法三：GitHub Actions 自动部署

1. 在 GitHub Settings → Secrets 添加 `RAILWAY_TOKEN`
2. 推送代码到 main 分支自动触发部署

---

## 🔧 部署前准备

### 1. 注册 Railway 账号
```
https://railway.app
```
使用 GitHub 账号一键登录

### 2. 获取 Railway Token（可选，用于 GitHub Actions）
```
https://railway.app/account/tokens
```
生成 Token 并保存到 GitHub Secrets

---

## 📋 部署后配置

### 1. 获取 API 地址
部署完成后，Railway 会分配域名：
```
https://medroundtable-api.up.railway.app
```

### 2. 更新 Second Me 开发者平台
访问 https://develop.second.me/ 更新：

| 配置项 | 新值 |
|--------|------|
| A2A Discovery | `https://medroundtable-api.up.railway.app/api/a2a/discovery` |
| A2A Messaging | `https://medroundtable-api.up.railway.app/api/a2a/message` |
| OAuth 回调 | `https://medroundtable-api.up.railway.app/api/auth/callback` |
| Webhook | `https://medroundtable-api.up.railway.app/api/a2a/webhook/secondme` |

### 3. 更新 Vercel 前端
在 Vercel 环境变量中添加：
```
NEXT_PUBLIC_API_URL=https://medroundtable-api.up.railway.app
```

### 4. 更新 GitHub 文档
修改以下文件中的 API 地址：
- `secondme-manifest.json`
- `HACKATHON_SUBMISSION.md`

---

## 🧪 测试部署

### 测试 API 端点
```bash
# 健康检查
curl https://medroundtable-api.up.railway.app/health

# A2A Discovery
curl https://medroundtable-api.up.railway.app/api/a2a/discovery

# 根路径
curl https://medroundtable-api.up.railway.app/
```

### 预期响应
```json
{
  "name": "MedRoundTable API",
  "version": "2.0.0",
  "status": "healthy"
}
```

---

## 🔍 故障排除

### 问题1: 部署失败
```bash
# 查看日志
railway logs

# 检查环境变量
railway variables
```

### 问题2: API 返回 404
- 检查启动命令是否正确
- 确认 `backend/main.py` 存在

### 问题3: OAuth 登录失败
- 检查 `SECONDME_CLIENT_SECRET` 是否正确
- 确认回调地址与 Second Me 平台一致

---

## 📊 费用说明

Railway 免费额度：
- $5/月 免费额度
- 512 MB RAM
- 1 GB 磁盘
- 100 GB 出站流量

足够 MedRoundTable 开发测试使用！

---

## 🎯 下一步

部署成功后：
1. ✅ 测试 API 端点
2. ✅ 更新 Second Me 配置
3. ✅ 更新 Vercel 前端
4. ✅ 完成黑客松提交

---

**准备好开始部署了吗？运行 `./deploy-railway-oneclick.sh` 即可！** 🚀
