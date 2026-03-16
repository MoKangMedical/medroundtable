# MedRoundTable V2.0 - Zeabur部署指南

## 🚀 部署步骤 (3分钟)

### 方式1: Zeabur CLI (推荐)

#### 1. 在你的本地电脑操作

```bash
# 安装 Zeabur CLI
npm install -g zeabur

# 登录 (会打开浏览器)
zeabur auth login

# 进入项目目录
cd /path/to/medroundtable

# 一键部署
zeabur deploy
```

#### 2. 配置环境变量
部署完成后，在Zeabur控制台设置：
```
SECRET_KEY=your-production-secret-key
ACCESS_TOKEN_EXPIRE_DAYS=7
```

#### 3. 绑定域名 (可选)
```bash
zeabur domain add medroundtable.zeabur.app
```

---

### 方式2: GitHub自动部署 (最简单)

#### 1. 推送代码到GitHub
```bash
git add .
git commit -m "V2.0 ready for deployment"
git push origin main
```

#### 2. 在Zeabur网站操作
```
1. 访问 https://dash.zeabur.com
2. 点击 "Create Project"
3. 选择 "Deploy from GitHub"
4. 选择 MoKangMedical/medroundtable 仓库
5. 选择 main 分支
6. 点击 Deploy
```

#### 3. 配置域名
```
Project Settings → Domains → Generate Domain
```

**会自动获得**: `https://medroundtable-xxxx.zeabur.app`

---

### 方式3: Railway (替代方案)

```
1. 访问 https://railway.app
2. New Project → Deploy from GitHub
3. 选择仓库
4. 自动部署完成
```

---

## ✅ 部署后验证

访问以下地址检查：
```
https://your-app.zeabur.app/           # 主页
https://your-app.zeabur.app/docs       # API文档
https://your-app.zeabur.app/api/v2/    # V2 API
```

---

## 🔧 环境变量配置

在Zeabur/Railway控制台设置：

| 变量 | 值 | 说明 |
|------|-----|------|
| SECRET_KEY | `随机字符串32位+` | JWT密钥 |
| ACCESS_TOKEN_EXPIRE_DAYS | `7` | Token过期天数 |
| DATABASE_URL | `sqlite:///data/medroundtable.db` | 数据库 |

---

## 🆘 故障排除

### 部署失败
```bash
# 检查日志
zeabur service logs

# 重新部署
zeabur deploy --force
```

### 端口错误
确保 `Dockerfile` 或启动命令使用 `PORT` 环境变量：
```python
# backend/main.py 中
import os
port = int(os.getenv("PORT", 8000))
```

---

## 📊 部署状态

当前代码状态: ✅ 已推送到GitHub  
配置文件: ✅ zeabur.toml 已配置  
Dockerfile: ✅ 已准备  

**只需要在Zeabur网站点击几下即可上线！**

---

**大圣选择哪种方式？紫霞可以帮你执行！** 🌸💜
