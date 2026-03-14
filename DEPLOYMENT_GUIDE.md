# MedRoundTable V2.0 - 部署与访问指南

## 🌐 之前的部署

**原地址**: https://medroundtable-v2.vercel.app/ (Vercel部署)

**当前状态**: 需要重新部署以包含V2.0新功能

---

## 🚀 当前服务状态

### 本地服务
- **状态**: ✅ 运行中
- **进程**: uvicorn backend.main:app --host 0.0.0.0 --port 8000
- **本地访问**: http://localhost:8000/

### API端点可用性
```
✅ /api/v2/           - V2 API概览
✅ /api/v2/stats      - 平台统计
✅ /api/v2/skills/*   - 技能市场 (8个端点)
✅ /api/v2/databases/* - 数据库浏览器 (6个端点)
✅ /api/v2/trials/*   - 临床试验设计 (5个端点)
✅ /api/v2/auth/*     - 自研认证系统 (9个端点)
```

---

## 📦 部署方案

### 方案1: 重新部署到 Vercel (推荐)

#### 1. 更新代码
```bash
cd /root/.openclaw/workspace/medroundtable
git add .
git commit -m "V2.0: 整合997项技能 + 自研认证系统"
git push origin main
```

#### 2. Vercel 自动部署
- 连接 GitHub 仓库
- Vercel 自动检测到更新并部署
- 新地址: https://medroundtable-v2.vercel.app/

#### 3. 配置环境变量
在 Vercel Dashboard 设置:
```
SECRET_KEY=your-production-secret-key
DATABASE_URL=your-database-url
```

---

### 方案2: 使用 Zeabur (Railway替代)

#### 1. 登录 Zeabur
```bash
# 安装 Zeabur CLI
npm install -g zeabur

# 登录
zeabur login
```

#### 2. 部署
```bash
# 在项目目录
cd /root/.openclaw/workspace/medroundtable

# 部署
zeabur deploy
```

#### 3. 绑定域名
```bash
zeabur domain add medroundtable.zeabur.app
```

---

### 方案3: 使用 Cloudflare Tunnel (开发测试)

#### 1. 安装 cloudflared
```bash
# 下载安装
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/
```

#### 2. 创建隧道
```bash
# 登录
cloudflared tunnel login

# 创建隧道
cloudflared tunnel create medroundtable

# 配置隧道 (创建 ~/.cloudflared/config.yml)
cat > ~/.cloudflared/config.yml << 'EOF'
tunnel: <tunnel-id>
credentials-file: /root/.cloudflared/<tunnel-id>.json

ingress:
  - hostname: medroundtable.yourdomain.com
    service: http://localhost:8000
  - service: http_status:404
EOF

# 运行隧道
cloudflared tunnel run medroundtable
```

#### 3. 访问
```
https://medroundtable.yourdomain.com
```

---

### 方案4: 本地开发访问 (当前可用)

#### 启动服务
```bash
cd /root/.openclaw/workspace/medroundtable

# 确保服务运行
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 本地访问
```
http://localhost:8000/docs      # Swagger API文档
http://localhost:8000/redoc     # ReDoc文档
http://localhost:8000/api/v2/   # V2 API根
```

#### 使用 SSH 隧道 (远程访问本地)
```bash
# 在本地机器运行
ssh -L 8000:localhost:8000 root@43.134.3.158

# 然后访问本地 http://localhost:8000
```

---

## 🧪 当前可测试功能

### 1. API文档 (Swagger)
```
http://localhost:8000/docs
```

### 2. 测试命令
```bash
# V2 API概览
curl http://localhost:8000/api/v2/

# 平台统计
curl http://localhost:8000/api/v2/stats

# 技能列表
curl http://localhost:8000/api/v2/skills/

# 注册测试用户
curl -X POST http://localhost:8000/api/v2/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "role": "researcher"
  }'

# 登录
curl -X POST http://localhost:8000/api/v2/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@medroundtable.com",
    "password": "admin123"
  }'
```

---

## 📝 部署检查清单

### 后端部署
- [ ] 更新 requirements.txt (添加 bcrypt, PyJWT)
- [ ] 配置生产环境密钥 (SECRET_KEY)
- [ ] 配置数据库连接
- [ ] 配置 CORS 允许域名
- [ ] 配置日志记录

### 前端部署
- [ ] 构建前端 (npm run build)
- [ ] 配置 API 基础 URL
- [ ] 部署静态文件

### 环境配置
- [ ] 设置环境变量
- [ ] 配置域名
- [ ] 启用 HTTPS
- [ ] 配置数据库迁移

---

## 🎯 推荐下一步

1. **短期**: 使用 Cloudflare Tunnel 快速获得可访问的URL进行测试
2. **中期**: 重新部署到 Vercel 或 Zeabur
3. **长期**: 配置自定义域名 + HTTPS

---

## 📞 需要我帮你

1. **配置 Cloudflare Tunnel** → 5分钟获得可访问链接
2. **准备 Vercel 部署** → 更新配置并推送代码
3. **配置 Zeabur** → Railway替代方案
4. **本地测试** → 运行测试脚本验证所有API

告诉我你想用哪种方案！🌸💜
