# 🚀 MedRoundTable Zeabur 部署指南

## 快速开始

### 步骤1: 运行部署脚本

```bash
cd /path/to/medroundtable
chmod +x deploy-zeabur.sh
./deploy-zeabur.sh
```

脚本会自动：
- ✅ 检查项目文件
- ✅ 创建 `zeabur.toml`
- ✅ 创建 `Dockerfile`
- ✅ 创建 `start.sh`
- ✅ 生成环境变量模板

### 步骤2: 推送到 GitHub

```bash
git add zeabur.toml Dockerfile start.sh health.py
git commit -m "chore: add Zeabur deployment config"
git push origin main
```

### 步骤3: 在 Zeabur 部署

1. 访问 [Zeabur Dashboard](https://zeabur.com)
2. 点击 "Create Project"
3. 选择 "Deploy from GitHub"
4. 选择 `MoKangMedical/medroundtable` 仓库
5. 点击 "Deploy"

### 步骤4: 获取域名并更新配置

部署完成后，Zeabur 会分配一个域名（例如：`medroundtable-xxx.zeabur.app`）

```bash
chmod +x update-domain.sh
./update-domain.sh medroundtable-xxx.zeabur.app
```

### 步骤5: 设置环境变量

在 Zeabur Dashboard > Your Project > Environment Variables 中设置：

**必需变量：**
```env
SECONDME_CLIENT_ID=your_secondme_client_id
SECONDME_CLIENT_SECRET=your_secondme_client_secret
SECRET_KEY=your_random_secret_key
```

**可选变量：**
```env
# AI API Keys
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
DEEPSEEK_API_KEY=sk-xxx

# 支付
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
```

### 步骤6: 重新部署

设置环境变量后，Zeabur 会自动重新部署。

访问你的后端地址：`https://your-domain.zeabur.app`

---

## 文件说明

| 文件 | 用途 |
|------|------|
| `zeabur.toml` | Zeabur 部署配置 |
| `Dockerfile` | 容器构建文件 |
| `start.sh` | 容器启动脚本 |
| `health.py` | 健康检查端点 |
| `update-domain.sh` | 域名更新脚本 |
| `.env.production` | 生产环境变量模板 |

---

## 故障排查

### 问题1: 部署失败

```bash
# 查看构建日志
# 在 Zeabur Dashboard > Deployments 中查看
```

### 问题2: 健康检查失败

确保 `main.py` 中注册了健康检查路由：

```python
from health import router as health_router
app.include_router(health_router)
```

### 问题3: CORS 错误

检查 `ALLOWED_ORIGINS` 环境变量是否包含前端地址。

### 问题4: 数据库连接失败

Zeabur 使用 SQLite 默认存储在 `/data` 目录，确保已创建该目录。

---

## 重要链接

- **前端地址**: https://medroundtable-v2.vercel.app
- **部署文档**: https://docs.zeabur.com
- **Second Me API**: https://api.mindverse.com/gate/lab

---

## 联系方式

部署遇到问题？
- Zeabur Discord: https://discord.gg/zeabur
- Second Me 支持: https://second.me/support
