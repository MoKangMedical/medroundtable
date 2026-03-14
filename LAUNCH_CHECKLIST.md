# MedRoundTable 上线检查清单

## 📋 部署前检查项

### 代码与配置
- [ ] 最新代码已推送到GitHub仓库
- [ ] `.env.production` 文件已创建并配置
- [ ] `SECRET_KEY` 已重新生成（非默认值）
- [ ] 所有敏感信息已从代码中移除
- [ ] GitHub仓库为公开或Second Me已授权访问

### 必需环境变量确认
```bash
# 检查以下变量是否已设置
grep -E "^(PORT|HOST|DEBUG|SECRET_KEY|DATABASE_URL|ALLOWED_ORIGINS)" .env.production
```

| 变量 | 检查命令 |
|------|---------|
| PORT | `grep "^PORT=" .env.production` |
| SECRET_KEY | `grep "^SECRET_KEY=" .env.production` 确保不是默认值 |
| DATABASE_URL | `grep "^DATABASE_URL=" .env.production` |
| ALLOWED_ORIGINS | 确认包含生产前端域名 |

### Second Me OAuth 配置
- [ ] 已在 Second Me 开发者中心创建应用
- [ ] Client ID 已复制到环境变量
- [ ] Client Secret 已复制到环境变量
- [ ] 回调URL已配置为生产域名
- [ ] 所需权限范围已勾选

### AI API Keys（至少配置一个）
- [ ] OpenAI API Key 或
- [ ] Moonshot API Key 或
- [ ] Zhipu API Key 或
- [ ] DeepSeek API Key 或
- [ ] 其他支持的AI提供商

### 域名与SSL
- [ ] 生产域名已解析到服务器
- [ ] SSL证书已配置（Zeabur自动提供）
- [ ] HTTPS强制跳转已启用

---

## 🚀 部署中步骤

### Zeabur 部署流程

1. **登录 Zeabur 控制台**
   ```bash
   访问: https://zeabur.com/dashboard
   ```

2. **创建新项目**
   - 点击「Create Project」
   - 选择「Deploy from GitHub」
   - 选择 `MoKangMedical/medroundtable` 仓库

3. **配置环境变量**
   - 进入项目 → Environment Variables
   - 逐个添加 `.env.production` 中的变量
   - 确认所有必需变量已添加

4. **等待部署完成**
   - 观察 Build Logs
   - 确认显示 Build Successful
   - 记录分配的域名

5. **更新域名配置**（如使用自定义域名）
   ```bash
   ./update-domain.sh your-domain.zeabur.app
   ```

6. **验证部署**
   ```bash
   curl https://your-domain.zeabur.app/health
   ```

### 其他平台部署

#### Railway 部署
```bash
# 1. 连接GitHub仓库到Railway
# 2. 在Variables中设置环境变量
# 3. 自动生成域名，或使用自定义域名
```

#### 自建服务器部署
```bash
# 1. 拉取代码
git clone https://github.com/MoKangMedical/medroundtable.git
cd medroundtable

# 2. 配置环境
cp .env.production .env
# 编辑 .env 填入生产配置

# 3. 启动服务
docker-compose -f docker-compose.prod.yml up -d

# 4. 检查状态
docker-compose -f docker-compose.prod.yml ps
```

---

## ✅ 部署后验证

### 基础功能验证
```bash
# 运行自动验证脚本
chmod +x verify-deployment.sh
./verify-deployment.sh your-domain.zeabur.app
```

### 手动检查清单

| 检查项 | 验证方法 | 预期结果 |
|--------|---------|---------|
| 首页访问 | 浏览器访问域名 | 显示API信息或Swagger文档 |
| 健康检查 | `curl /health` | 返回 `{"status":"healthy"}` |
| A2A Discovery | `curl /api/a2a/discovery` | 返回5个Agent信息 |
| A2A Status | `curl /api/a2a/status` | 返回系统状态 |
| Agent列表 | `curl /api/v1/agents` | 返回Agent列表 |
| CORS配置 | 预检请求测试 | 返回200或204 |

### Second Me OAuth 验证
1. 访问前端页面
2. 点击「Second Me 登录」
3. 确认跳转至 Second Me 授权页
4. 完成授权后返回应用
5. 确认用户已登录

### A2A 协议验证
```bash
# 1. Discovery 端点
curl https://your-domain.zeabur.app/api/a2a/discovery | jq

# 2. 发送测试消息
curl -X POST https://your-domain.zeabur.app/api/a2a/message \
  -H "Content-Type: application/json" \
  -d '{
    "sender": {"agent_id": "test", "agent_name": "Test"},
    "recipient": {"agent_id": "clinical_director", "agent_name": "临床主任"},
    "message_type": "question",
    "content": "测试消息"
  }'

# 3. 查询状态
curl https://your-domain.zeabur.app/api/a2a/status
```

### 数据库验证
- [ ] 可创建新会话
- [ ] 可保存用户数据
- [ ] 历史记录可查询
- [ ] 数据持久化正常

---

## 🔄 回滚方案

### Zeabur 回滚
1. 进入 Zeabur Dashboard
2. 选择 Deployments 标签
3. 找到上一个成功的部署
4. 点击「Rollback」

### Git 回滚
```bash
# 1. 查看历史提交
git log --oneline -10

# 2. 回滚到指定版本
git reset --hard <commit-hash>

# 3. 强制推送
git push origin main --force

# 4. Zeabur自动重新部署
```

### Docker 回滚
```bash
# 1. 停止当前容器
docker-compose -f docker-compose.prod.yml down

# 2. 切换到上一个镜像版本
docker-compose -f docker-compose.prod.yml up -d --build

# 3. 查看日志确认
docker-compose -f docker-compose.prod.yml logs -f
```

### 数据库回滚
```bash
# SQLite备份恢复
cp data/medroundtable.db.backup data/medroundtable.db

# PostgreSQL回滚（如使用）
pg_restore -d medroundtable backup.sql
```

### 紧急回滚检查清单
- [ ] 确认备份数据可用
- [ ] 停止当前服务
- [ ] 恢复上一版本代码
- [ ] 恢复数据库（如需要）
- [ ] 验证服务正常
- [ ] 更新DNS/CDN缓存（如需要）

---

## 📊 监控与告警

### 健康监控
```bash
# 设置定时健康检查（crontab）
*/5 * * * * curl -s https://your-domain.zeabur.app/health > /dev/null || echo "ALERT: $(date)" >> /var/log/medroundtable/alerts.log
```

### 关键指标监控
| 指标 | 检查频率 | 告警阈值 |
|------|---------|---------|
| 服务可用性 | 每5分钟 | HTTP 非200 |
| 响应时间 | 每5分钟 | > 5秒 |
| 错误率 | 实时监控 | > 5% |
| 磁盘空间 | 每小时 | < 80% |

---

## 📞 联系方式

| 角色 | 联系方式 | 职责 |
|------|---------|------|
| 技术负责人 | tony1982110@gmail.com | 技术问题处理 |
| Second Me 支持 | https://second.me/support | OAuth/API问题 |
| Zeabur 支持 | https://discord.gg/zeabur | 部署问题 |

---

## 🎉 上线完成确认

- [ ] 所有检查项通过
- [ ] 自动化验证脚本执行成功
- [ ] 手动功能测试完成
- [ ] Second Me OAuth 登录正常
- [ ] A2A Discovery 可访问
- [ ] 监控告警已配置
- [ ] 回滚方案已准备
- [ ] 团队已通知上线完成

**上线日期**: _______________
**负责人**: _______________
**备注**: _______________
