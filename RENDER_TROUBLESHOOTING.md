# 🔧 Render 部署故障排除指南

## 当前状态

**Render 服务**: https://medroundtable-api.onrender.com
**状态**: ⏳ 启动中 / 配置检查中

---

## 常见问题排查

### 问题 1: 返回 404
**原因**: 
- 服务还在启动中（Render 首次启动需要 3-5 分钟）
- 启动命令配置不正确
- 代码路径问题

**解决**:
1. 访问 Render Dashboard: https://dashboard.render.com
2. 找到你的服务，点击 "Logs" 查看启动日志
3. 检查是否有错误信息

---

### 问题 2: 启动命令配置

在 Render Dashboard 中，确认以下配置：

**Build Command**:
```bash
pip install -r requirements.txt
```

**Start Command**:
```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

**重要**: 必须使用 `$PORT` 环境变量，Render 会动态分配端口

---

### 问题 3: 环境变量检查

在 Render Dashboard → Environment 中，确认以下变量已设置：

```
PORT=10000  (Render 会自动设置)
SECRET_KEY=0a1267066319f509476a44ea41c17798df616b97f93882b7d5e6ed88c065b475
DEBUG=false
DATABASE_URL=sqlite:///app/data/medroundtable.db
CORS_ORIGINS=https://medroundtable-v2.vercel.app
SECONDME_CLIENT_ID=19b5f08b-2256-41aa-b196-2f98491099f7
SECONDME_CLIENT_SECRET=f9f406e3d8dc4fe8e8363853865e1afea2957e7b0a33d75e96cbc5a22c4c20f3
SECONDME_REDIRECT_URI=https://medroundtable-api.onrender.com/api/auth/callback
SECONDME_API_BASE=https://api.mindverse.com/gate/lab
```

---

## 验证部署

### 测试命令

等服务启动后，运行以下测试：

```bash
# 测试根路径
curl https://medroundtable-api.onrender.com/

# 测试健康检查
curl https://medroundtable-api.onrender.com/health

# 测试 A2A Discovery
curl https://medroundtable-api.onrender.com/api/a2a/discovery
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

## 快速修复步骤

### 如果服务一直 404

1. **访问 Dashboard**: https://dashboard.render.com
2. **找到服务** → 点击 "Settings"
3. **检查 Root Directory**:
   - 确保 Root Directory 为空（不是 `./backend`）
4. **重新部署**:
   - 点击 "Manual Deploy" → "Deploy latest commit"

---

## 备选方案

如果 Render 部署有问题，可以尝试：

### 方案 A: Railway（推荐）
```
https://railway.app/new
→ Deploy from GitHub
→ 选择 MoKangMedical/medroundtable
```

### 方案 B: Zeabur
```
https://zeabur.com
→ 导入 GitHub 仓库
→ 选择 Python 模板
```

### 方案 C: Docker 本地部署
```bash
cd /root/.openclaw/workspace/medroundtable
docker-compose up -d
```

---

## 部署成功后

一旦 Render 服务正常运行，告诉我，我立即帮你：

1. ✅ 更新 Second Me 开发者平台的回调地址
2. ✅ 更新 Vercel 前端的环境变量
3. ✅ 更新 GitHub 上的配置文件
4. ✅ 完成黑客松提交

---

**请检查 Render Dashboard 的日志，告诉我有什么错误信息！** 🔧
