# 🚀 MedRoundTable 上线准备清单

## ✅ 当前状态

| 检查项 | 状态 | 备注 |
|--------|------|------|
| GitHub 仓库 | ✅ 已连接 | https://github.com/MoKangMedical/medroundtable |
| Docker 容器 | ✅ 运行中 | API: 8001, Web: 3001 |
| 后端服务 | ✅ 健康 | /health 端点正常 |
| A2A Discovery | ✅ 正常 | 返回5个Agent信息 |
| 最新代码 | ✅ 已推送 | commit: b91d242 |
| 必要文件 | ✅ 齐全 | manifest, config, docs |

---

## 📋 Second Me 平台上线步骤

### 第 1 步：访问开发者中心
- 网址：https://app.secondme.io/developer
- 登录你的 Second Me 账号

### 第 2 步：创建新应用
点击"创建应用"，填写信息：

| 字段 | 值 |
|------|-----|
| 应用名称 | MedRoundTable |
| 应用描述 | 全球首个A2A架构医学科研协作平台 - 五位专业AI Agent实现从临床问题到科研成果的全流程自动化协作 |
| 应用图标 | 使用 `frontend/assets/doctors.jpg` |
| 应用类型 | A2A Agent 平台 |

### 第 3 步：上传 Manifest 文件
上传 `secondme-manifest.json`，包含：
- 5个专业Agent配置
- A2A 协议端点
- OAuth 集成配置

### 第 4 步：配置 OAuth（可选）
如果你想启用 Second Me 登录：

1. 在 Second Me 开发者中心获取 Client ID 和 Client Secret
2. 编辑 `.env.production` 文件：
   ```bash
   SECONDME_CLIENT_ID=your_client_id_here
   SECONDME_CLIENT_SECRET=your_client_secret_here
   SECONDME_REDIRECT_URI=https://your-domain.com/api/auth/callback
   ```

### 第 5 步：部署到生产服务器

#### 选项 A：使用当前服务器（推荐测试）
```bash
# 当前服务已在运行
curl http://localhost:8001/health  # 检查后端
curl http://localhost:3001        # 检查前端
```

#### 选项 B：部署到新服务器
```bash
# 1. 克隆仓库
git clone https://github.com/MoKangMedical/medroundtable.git
cd medroundtable

# 2. 配置环境变量
cp .env.production .env
# 编辑 .env 填入你的配置

# 3. 一键部署
./launch.sh
```

#### 选项 C：使用 Docker Compose
```bash
# 启动生产环境
docker-compose -f docker-compose.prod.yml up -d

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

---

## 🔧 生产环境配置

### 必需配置
```bash
# .env.production
SECRET_KEY=your_random_secret_key_here
DEBUG=false

# 数据库（默认 SQLite，生产建议 PostgreSQL）
DATABASE_URL=sqlite:///./data/medroundtable.db
```

### 可选配置
```bash
# AI 模型 API Keys（至少配一个）
OPENAI_API_KEY=sk-...
GLM_API_KEY=...

# Second Me OAuth
SECONDME_CLIENT_ID=...
SECONDME_CLIENT_SECRET=...

# 邮箱通知
SMTP_SERVER=smtp.gmail.com
SMTP_USER=your@email.com
SMTP_PASSWORD=...
```

---

## 🧪 上线前测试清单

### API 测试
```bash
# 1. 健康检查
curl http://your-domain:8001/health

# 2. A2A Discovery
curl http://your-domain:8001/api/a2a/discovery

# 3. 发送消息（替换 agent_id）
curl -X POST http://your-domain:8001/api/a2a/message \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "test-user",
    "recipient": "clinical_director",
    "content": {"text": "测试消息"}
  }'
```

### 前端测试
- [ ] 首页加载正常
- [ ] Agent 列表显示
- [ ] 创建新会话
- [ ] 发送消息
- [ ] 查看历史记录

---

## 📊 监控和维护

### 查看服务状态
```bash
./status.sh
```

### 查看日志
```bash
# Docker 日志
docker logs medroundtable-api -f
docker logs medroundtable-web -f

# 系统日志
tail -f /var/log/medroundtable/*.log
```

### 自动监控
```bash
# 设置定时检查（每5分钟）
*/5 * * * * /path/to/medroundtable/monitor.sh >> /var/log/medroundtable/monitor.log 2>&1
```

---

## 📝 提交审核材料

### 必需材料
1. ✅ `secondme-manifest.json` - 应用清单
2. ✅ `docs/USER_GUIDE.md` - 用户指南
3. ✅ `docs/SECONDME_API_GUIDE.md` - API 文档
4. ✅ 演示视频（建议录制 2-3 分钟）
5. ✅ 截图（已生成 medroundtable.png）

### Hackathon 提交
- 项目页面：https://hackathon.second.me/projects/cmlg779kn000204kvr6jygh28
- 确保项目信息完整
- 添加演示链接

---

## 🚨 故障排查

### 服务无法启动
```bash
# 检查端口占用
netstat -tlnp | grep -E '8001|3001'

# 重启服务
docker-compose -f docker-compose.prod.yml restart

# 重建容器
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build
```

### API 无响应
```bash
# 检查容器状态
docker ps | grep medroundtable

# 查看错误日志
docker logs medroundtable-api --tail 50
```

---

## 📞 联系方式

- **开发者**: MoKangMedical
- **GitHub**: https://github.com/MoKangMedical/medroundtable
- **邮箱**: tony1982110@gmail.com

---

## 🎉 上线后检查

- [ ] Second Me 平台显示正常
- [ ] Agent Discovery 可访问
- [ ] OAuth 登录可用（如配置）
- [ ] 用户可以创建会话
- [ ] 消息发送正常
- [ ] 数据保存正常

---

**祝上线顺利！** 🚀

如有问题，随时找我帮忙！
