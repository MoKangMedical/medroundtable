# 🚀 Railway 后端部署指南

## 部署前准备

### 1. 注册 Railway 账号
访问: https://railway.app
使用 GitHub 账号一键登录

### 2. 创建新项目
```bash
# 方法1: 通过 Railway Dashboard
1. 登录 https://railway.app/dashboard
2. 点击 "New Project"
3. 选择 "Deploy from GitHub repo"
4. 选择 MoKangMedical/medroundtable 仓库

# 方法2: 使用 Railway CLI（可选）
npm install -g @railway/cli
railway login
railway init
```

---

## 部署步骤

### Step 1: 在 Railway Dashboard 部署

1. **访问 Railway Dashboard**
   ```
   https://railway.app/dashboard
   ```

2. **创建新项目**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 选择 `MoKangMedical/medroundtable`

3. **配置环境变量**
   在 Project Settings → Variables 中添加：

   | 变量名 | 值 |
   |--------|-----|
   | `SECRET_KEY` | `0a1267066319f509476a44ea41c17798df616b97f93882b7d5e6ed88c065b475` |
   | `DEBUG` | `false` |
   | `DATABASE_URL` | `sqlite:///app/data/medroundtable.db` |
   | `CORS_ORIGINS` | `https://medroundtable-v2.vercel.app` |
   | `SECONDME_CLIENT_ID` | `19b5f08b-2256-41aa-b196-2f98491099f7` |
   | `SECONDME_CLIENT_SECRET` | `f9f406e3d8dc4fe8e8363853865e1afea2957e7b0a33d75e96cbc5a22c4c20f3` |
   | `SECONDME_REDIRECT_URI` | `https://medroundtable-api.railway.app/api/auth/callback` |
   | `SECONDME_API_BASE` | `https://api.mindverse.com/gate/lab` |

4. **配置启动命令**
   在 Settings → Deploy 中设置：
   ```
   Start Command: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
   Healthcheck Path: /health
   ```

5. **部署**
   - 点击 "Deploy"
   - 等待部署完成（约2-3分钟）

### Step 2: 获取域名

部署完成后，Railway 会自动分配域名：
```
https://medroundtable-api.up.railway.app
```

**获取方式**:
1. 在 Dashboard 中点击你的服务
2. 找到 "Domains" 标签
3. 复制生成的域名

### Step 3: 更新前端配置

部署成功后，需要更新 Vercel 前端配置，使其调用 Railway 后端：

1. 在 Vercel 项目中添加环境变量：
   ```
   NEXT_PUBLIC_API_URL=https://medroundtable-api.up.railway.app
   ```

2. 重新部署前端

---

## 验证部署

### 测试 API 端点
```bash
# 测试健康检查
curl https://medroundtable-api.up.railway.app/health

# 测试 A2A Discovery
curl https://medroundtable-api.up.railway.app/api/a2a/discovery

# 测试根路径
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

## 更新 Second Me 配置

部署成功后，需要更新 Second Me 开发者平台的回调地址：

1. 访问: https://develop.second.me/
2. 找到 MedRoundTable 应用
3. 更新以下配置：

| 配置项 | 新值 |
|--------|------|
| **A2A Discovery** | `https://medroundtable-api.up.railway.app/api/a2a/discovery` |
| **A2A Messaging** | `https://medroundtable-api.up.railway.app/api/a2a/message` |
| **OAuth 回调** | `https://medroundtable-api.up.railway.app/api/auth/callback` |
| **Webhook** | `https://medroundtable-api.up.railway.app/api/a2a/webhook/secondme` |

---

## 更新 GitHub 配置

部署成功后，更新以下文件：

### 1. secondme-manifest.json
```json
{
  "a2a_protocol": {
    "discovery_endpoint": "https://medroundtable-api.up.railway.app/api/a2a/discovery",
    "messaging_endpoint": "https://medroundtable-api.up.railway.app/api/a2a/message"
  },
  "oauth2": {
    "redirect_uris": [
      "https://medroundtable-api.up.railway.app/api/auth/callback"
    ]
  },
  "webhooks": {
    "endpoint": "https://medroundtable-api.up.railway.app/api/a2a/webhook/secondme"
  }
}
```

### 2. HACKATHON_SUBMISSION.md
更新 Demo 链接为新的 API 地址

---

## 故障排除

### 问题1: 部署失败
**解决**: 检查环境变量是否正确设置

### 问题2: API 返回 404
**解决**: 检查启动命令是否正确：
```
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

### 问题3: CORS 错误
**解决**: 确保 `CORS_ORIGINS` 包含前端域名

---

## 费用说明

Railway 免费额度：
- 每月 $5 免费额度
- 512 MB RAM
- 1 GB 磁盘
- 100 GB 出站流量

对于 MedRoundTable 开发测试完全够用！

---

**开始部署吧！有问题随时问我！** 🚀
