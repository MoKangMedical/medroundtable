# 🚀 Zeabur 一键部署指南（无需 Token）

## 快速部署（2分钟）

### Step 1: 访问 Zeabur
```
https://zeabur.com
```

### Step 2: 部署项目
1. 登录 Zeabur（用 GitHub 账号）
2. 点击 **"创建项目"**
3. 选择 **"从 GitHub 导入"**
4. 选择 `MoKangMedical/medroundtable`
5. 选择 **Python** 模板

### Step 3: 配置环境变量
在 Zeabur 控制台 → 环境变量，添加：

```
PORT=8000
HOST=0.0.0.0
DEBUG=false
SECRET_KEY=0a1267066319f509476a44ea41c17798df616b97f93882b7d5e6ed88c065b475
DATABASE_URL=sqlite:///app/data/medroundtable.db
CORS_ORIGINS=https://medroundtable-v2.vercel.app
SECONDME_CLIENT_ID=19b5f08b-2256-41aa-b196-2f98491099f7
SECONDME_CLIENT_SECRET=f9f406e3d8dc4fe8e8363853865e1afea2957e7b0a33d75e96cbc5a22c4c20f3
SECONDME_REDIRECT_URI=https://medroundtable-api.zeabur.app/api/auth/callback
SECONDME_API_BASE=https://api.mindverse.com/gate/lab
```

### Step 4: 配置启动命令
在服务设置中：
```
Start Command: uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Step 5: 部署
点击 "部署"，等待完成

---

## 📋 部署后

Zeabur 会自动分配域名：
```
https://medroundtable-api.zeabur.app
```

复制这个域名给我，我帮你更新配置！
