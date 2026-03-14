# MedRoundTable 上线最终检查清单

> 📋 **本文档目标**：确保 MedRoundTable 生产环境部署前的所有检查项都已完成，降低上线风险。

---

## 📊 清单概览

| 阶段 | 检查项数量 | 预计时间 |
|------|----------|---------|
| [一、部署前检查](#一部署前检查-20项) | 20 项 | 30分钟 |
| [二、部署中监控](#二部署中监控-10项) | 10 项 | 10分钟 |
| [三、部署后验证](#三部署后验证-15项) | 15 项 | 20分钟 |
| [四、应急预案](#四应急预案-5项) | 5 项 | - |
| **总计** | **50 项** | **约60分钟** |

---

## 一、部署前检查（20项）

### 1.1 代码与仓库 ✅

| # | 检查项 | 检查方法 | 通过标准 |
|---|-------|---------|---------|
| 1 | 代码已推送到 main 分支 | `git log --oneline -1` | 显示最新提交 |
| 2 | 没有未提交的更改 | `git status` | 显示 "nothing to commit" |
| 3 | 远程仓库配置正确 | `git remote -v` | 显示 GitHub 仓库地址 |
| 4 | 分支保护已启用 | GitHub → Settings → Branches | main 分支需要 PR 合并 |
| 5 | .gitignore 配置完整 | `cat .gitignore` | 包含 .env、__pycache__ 等 |

**快速检查命令：**
```bash
# 检查 Git 状态
./scripts/zeabur-deploy.sh check
```

---

### 1.2 配置文件 ✅

| # | 检查项 | 检查方法 | 通过标准 |
|---|-------|---------|---------|
| 6 | Dockerfile 存在 | `ls Dockerfile` | 文件存在 |
| 7 | zeabur.toml 配置正确 | `cat zeabur.toml` | 包含正确配置 |
| 8 | start.sh 可执行 | `ls -la start.sh` | 显示 -rwxr-xr-x |
| 9 | .env.production 存在 | `ls .env.production` | 文件存在（不提交到 Git） |
| 10 | zeabur.json 配置正确 | `cat zeabur.json` | 包含正确配置 |

**配置文件清单：**
```bash
echo "=== 检查部署文件 ==="
for file in Dockerfile zeabur.toml start.sh zeabur.json; do
    if [ -f "$file" ]; then
        echo "✓ $file 存在"
    else
        echo "✗ $file 缺失"
    fi
done
```

---

### 1.3 环境变量 ✅

| # | 检查项 | 变量名 | 检查命令 |
|---|-------|--------|---------|
| 11 | 端口配置 | PORT | `grep "^PORT=" .env.production` |
| 12 | 主机配置 | HOST | `grep "^HOST=" .env.production` |
| 13 | 调试模式关闭 | DEBUG | 值应为 `false` |
| 14 | JWT 密钥 | SECRET_KEY | 应为 64 位随机字符串 |
| 15 | 数据库连接 | DATABASE_URL | 应为 SQLite 路径 |
| 16 | CORS 白名单 | ALLOWED_ORIGINS | 包含所有前端域名 |
| 17 | Second Me Client ID | SECONDME_CLIENT_ID | 已配置 |
| 18 | Second Me Client Secret | SECONDME_CLIENT_SECRET | 已配置 |
| 19 | Second Me 回调 URL | SECONDME_REDIRECT_URI | 格式正确 |
| 20 | AI API Key | OPENAI/MOONSHOT/ZHIPU | 至少配置一个 |

**环境变量检查脚本：**
```bash
#!/bin/bash
echo "=== 环境变量检查 ==="

REQUIRED_VARS=(
    "PORT:8000"
    "HOST:0.0.0.0"
    "DEBUG:false"
    "SECRET_KEY"
    "DATABASE_URL:sqlite:///data"
    "ALLOWED_ORIGINS"
    "CORS_ORIGINS"
    "SECONDME_API_BASE:https://api.mindverse.com"
    "SECONDME_CLIENT_ID"
    "SECONDME_CLIENT_SECRET"
    "SECONDME_REDIRECT_URI"
)

for var in "${REQUIRED_VARS[@]}"; do
    key=$(echo "$var" | cut -d: -f1)
    if grep -q "^${key}=" .env.production 2>/dev/null; then
        value=$(grep "^${key}=" .env.production | cut -d= -f2)
        if [ -n "$value" ] && [ "$value" != "your_"* ] && [ "$value" != "从"* ]; then
            echo "✓ $key 已配置"
        else
            echo "✗ $key 值为空或无效"
        fi
    else
        echo "✗ $key 未配置"
    fi
done
```

---

## 二、部署中监控（10项）

### 2.1 Zeabur 部署监控

| # | 检查项 | 监控方法 | 通过标准 |
|---|-------|---------|---------|
| 21 | 部署已触发 | Zeabur Dashboard | 显示 "Deploying" |
| 22 | 构建日志无错误 | Console 标签页 | 无 ERROR 日志 |
| 23 | 依赖安装成功 | Build Log | 显示 "Successfully installed" |
| 24 | 数据库目录创建 | 构建日志 | 显示创建 /data 目录 |
| 25 | 服务启动成功 | Build Log | 显示 "Server started" |

**监控命令：**
```bash
# 查看部署状态
./scripts/zeabur-deploy.sh logs
```

---

### 2.2 启动过程监控

| # | 检查项 | 监控方法 | 通过标准 |
|---|-------|---------|---------|
| 26 | 端口绑定成功 | Console 日志 | Listening on 0.0.0.0:8000 |
| 27 | 数据库连接成功 | Console 日志 | Database connected |
| 28 | API 路由注册成功 | Console 日志 | Routes registered |
| 29 | CORS 中间件加载 | Console 日志 | CORS enabled |
| 30 | 服务状态 Running | Dashboard | 状态变为 Running |

---

## 三、部署后验证（15项）

### 3.1 基础功能验证

| # | 检查项 | 验证方法 | 命令/URL |
|---|-------|---------|---------|
| 31 | 首页访问 | 浏览器访问 | `https://你的域名/` |
| 32 | 健康检查 | curl 测试 | `curl /health` |
| 33 | API 文档 | Swagger UI | `https://你的域名/docs` |
| 34 | OpenAPI 规范 | JSON 访问 | `https://你的域名/openapi.json` |
| 35 | CORS 预检 | OPTIONS 请求 | `curl -X OPTIONS /api/v1/agents` |

**自动验证脚本：**
```bash
#!/bin/bash
DOMAIN="${1:-$(cat .zeabur_domain 2>/dev/null)}"

if [ -z "$DOMAIN" ]; then
    echo "请提供域名参数"
    exit 1
fi

BASE_URL="https://$DOMAIN"

echo "=== 部署验证 ==="
echo "目标域名: $DOMAIN"
echo ""

# 1. 健康检查
echo "1. 健康检查..."
health=$(curl -s "$BASE_URL/health" 2>/dev/null)
if echo "$health" | grep -q "healthy"; then
    echo "✓ 健康检查通过"
else
    echo "✗ 健康检查失败: $health"
fi

# 2. A2A Discovery
echo "2. A2A Discovery..."
discovery=$(curl -s "$BASE_URL/api/a2a/discovery" 2>/dev/null)
if echo "$discovery" | grep -q "agent_id"; then
    echo "✓ A2A Discovery 正常"
else
    echo "✗ A2A Discovery 异常"
fi

# 3. Agent 列表
echo "3. Agent 列表..."
agents=$(curl -s "$BASE_URL/api/v1/agents" 2>/dev/null)
if echo "$agents" | grep -q "\["; then
    echo "✓ Agent 列表正常"
else
    echo "✗ Agent 列表异常"
fi

# 4. A2A 状态
echo "4. A2A 状态..."
status=$(curl -s "$BASE_URL/api/a2a/status" 2>/dev/null)
if [ -n "$status" ]; then
    echo "✓ A2A 状态正常"
else
    echo "✗ A2A 状态异常"
fi

echo ""
echo "=== 验证完成 ==="
```

---

### 3.2 A2A 协议验证

| # | 检查项 | 验证方法 | 预期结果 |
|---|-------|---------|---------|
| 36 | Discovery 端点 | `GET /api/a2a/discovery` | 返回 5 个 Agent |
| 37 | Agent 技能查询 | `GET /api/a2a/agents/{id}/skills` | 返回技能列表 |
| 38 | 消息发送 | `POST /api/a2a/message` | 返回消息响应 |
| 39 | 状态查询 | `GET /api/a2a/status` | 返回系统状态 |

---

### 3.3 Second Me OAuth 验证

| # | 检查项 | 验证方法 | 预期结果 |
|---|-------|---------|---------|
| 40 | OAuth 登录入口 | `GET /api/auth/login` | 302 重定向 |
| 41 | 回调端点响应 | `GET /api/auth/callback` | 正确处理错误 |
| 42 | 完整登录流程 | 浏览器测试 | 成功登录并返回 |
| 43 | 用户信息获取 | 登录后检查 | 显示用户信息 |

---

### 3.4 前端集成验证

| # | 检查项 | 验证方法 | 预期结果 |
|---|-------|---------|---------|
| 44 | 前端访问后端 | 浏览器 DevTools | 无 CORS 错误 |
| 45 | Second Me 按钮 | 点击测试 | 跳转授权页面 |
| 46 | 登录状态保持 | 刷新页面 | 保持登录状态 |
| 47 | 数据加载正常 | 页面功能测试 | 数据正确显示 |

---

## 四、应急预案（5项）

### 4.1 回滚准备

| # | 检查项 | 准备内容 | 执行命令 |
|---|-------|---------|---------|
| 48 | 数据库备份 | 备份当前数据库 | `./scripts/db-backup.sh backup` |
| 49 | 回滚脚本就绪 | 确认脚本可用 | `./scripts/zeabur-deploy.sh rollback` |
| 50 | 紧急联系人 | 确认联系方式 | 记录到文档 |

**回滚流程：**
```bash
# 方案 1：Zeabur Dashboard 回滚
# 1. 登录 https://zeabur.com/dashboard
# 2. 进入项目 → Deployments
# 3. 找到上一个成功的部署
# 4. 点击 "Rollback"

# 方案 2：Git 回滚
./scripts/zeabur-deploy.sh rollback

# 方案 3：手动回滚
git log --oneline -10          # 查看历史
git revert HEAD                # 撤销最新提交
git push origin main           # 推送触发重新部署
```

---

### 4.2 故障排查指南

#### 故障 1：服务无法启动

**症状：** Zeabur 状态显示 Error 或反复重启

**排查步骤：**
1. 查看 Console 日志中的错误信息
2. 检查环境变量是否完整
3. 确认数据库目录有写权限
4. 检查端口是否冲突

**解决：**
```bash
# 检查日志
./scripts/zeabur-deploy.sh logs

# 重新部署
./scripts/zeabur-deploy.sh deploy
```

---

#### 故障 2：CORS 错误

**症状：** 前端报 "CORS policy" 错误

**排查步骤：**
1. 检查 `ALLOWED_ORIGINS` 是否包含前端域名
2. 确认协议一致（http/https）
3. 检查域名拼写

**解决：**
```bash
# 更新环境变量
# 在 Zeabur Dashboard → Variables 中修改
# 重新部署
```

---

#### 故障 3：OAuth 登录失败

**症状：** Second Me 登录后报错或无法返回

**排查步骤：**
1. 检查 `SECONDME_REDIRECT_URI` 是否与 Second Me 配置一致
2. 确认 Client ID 和 Secret 正确
3. 检查回调 URL 是否可访问

**解决：**
```bash
# 验证 OAuth 配置
curl "https://你的域名/api/auth/callback?code=test&state=test"
```

---

#### 故障 4：数据库连接失败

**症状：** 无法保存数据或查询失败

**排查步骤：**
1. 检查 `DATABASE_URL` 格式
2. 确认 `/data` 目录存在
3. 检查磁盘空间

**解决：**
```bash
# 恢复数据库备份
./scripts/db-backup.sh restore <备份文件>
```

---

#### 故障 5：AI 功能异常

**症状：** 无法获取 AI 回复

**排查步骤：**
1. 检查 API Key 是否配置
2. 确认 API Key 余额充足
3. 检查 API 调用日志

**解决：**
```bash
# 检查环境变量
grep -E "(OPENAI|MOONSHOT|ZHIPU)" .env.production
```

---

## 五、上线完成确认

### 最终检查表

请由负责人在上线前逐一确认：

| 阶段 | 负责人 | 完成时间 | 签名 |
|------|-------|---------|------|
| 代码审查 | ______ | ________ | ______ |
| 环境配置 | ______ | ________ | ______ |
| 部署执行 | ______ | ________ | ______ |
| 功能验证 | ______ | ________ | ______ |
| 监控确认 | ______ | ________ | ______ |

### 上线后监控项

上线后 24 小时内需要特别关注：

- [ ] 服务可用性（每 15 分钟检查一次）
- [ ] 错误日志（每小时检查一次）
- [ ] 响应时间（监控是否超过阈值）
- [ ] 用户反馈（收集问题报告）
- [ ] 数据库增长（监控存储空间）

### 联系方式

| 角色 | 姓名 | 联系方式 | 职责 |
|------|-----|---------|------|
| 项目负责人 | ______ | ________ | 整体协调 |
| 技术负责人 | ______ | ________ | 技术问题处理 |
| 运维负责人 | ______ | ________ | 部署和监控 |
| 产品负责人 | ______ | ________ | 用户反馈处理 |

---

## 六、附录：快速命令参考

### 部署相关

```bash
# 部署前检查
./scripts/zeabur-deploy.sh check

# 执行部署
./scripts/zeabur-deploy.sh deploy

# 完整流程（检查+部署+验证）
./scripts/zeabur-deploy.sh full

# 查看日志
./scripts/zeabur-deploy.sh logs

# 回滚
./scripts/zeabur-deploy.sh rollback
```

### 数据库相关

```bash
# 备份数据库
./scripts/db-backup.sh backup

# 备份到云存储
./scripts/db-backup.sh backup --cloud oss

# 恢复数据库
./scripts/db-backup.sh restore <备份文件>

# 查看备份列表
./scripts/db-backup.sh list

# 清理旧备份
./scripts/db-backup.sh clean --keep 7
```

### 监控相关

```bash
# 单次健康检查
./scripts/monitor-health.sh check

# 持续监控（守护模式）
./scripts/monitor-health.sh daemon

# 生成健康报告
./scripts/monitor-health.sh report

# 查看历史记录
./scripts/monitor-health.sh history

# 测试告警
./scripts/monitor-health.sh test-alert
```

### 验证相关

```bash
# 完整部署验证
./scripts/zeabur-deploy.sh health <域名>

# 手动验证命令
curl https://<域名>/health
curl https://<域名>/api/a2a/discovery
curl https://<域名>/api/v1/agents
```

---

## ✅ 上线检查清单汇总

**请打印此页，由负责人逐一勾选：**

### 部署前（20项）
- [ ] 1. 代码已推送到 main 分支
- [ ] 2. 没有未提交的更改
- [ ] 3. 远程仓库配置正确
- [ ] 4. 分支保护已启用
- [ ] 5. .gitignore 配置完整
- [ ] 6. Dockerfile 存在
- [ ] 7. zeabur.toml 配置正确
- [ ] 8. start.sh 可执行
- [ ] 9. .env.production 存在
- [ ] 10. zeabur.json 配置正确
- [ ] 11. PORT 配置正确
- [ ] 12. HOST 配置正确
- [ ] 13. DEBUG 设为 false
- [ ] 14. SECRET_KEY 已配置
- [ ] 15. DATABASE_URL 已配置
- [ ] 16. ALLOWED_ORIGINS 已配置
- [ ] 17. SECONDME_CLIENT_ID 已配置
- [ ] 18. SECONDME_CLIENT_SECRET 已配置
- [ ] 19. SECONDME_REDIRECT_URI 已配置
- [ ] 20. AI API Key 已配置

### 部署中（10项）
- [ ] 21. 部署已触发
- [ ] 22. 构建日志无错误
- [ ] 23. 依赖安装成功
- [ ] 24. 数据库目录创建
- [ ] 25. 服务启动成功
- [ ] 26. 端口绑定成功
- [ ] 27. 数据库连接成功
- [ ] 28. API 路由注册成功
- [ ] 29. CORS 中间件加载
- [ ] 30. 服务状态 Running

### 部署后（15项）
- [ ] 31. 首页访问正常
- [ ] 32. 健康检查通过
- [ ] 33. API 文档可访问
- [ ] 34. OpenAPI 规范可访问
- [ ] 35. CORS 预检正常
- [ ] 36. A2A Discovery 正常
- [ ] 37. Agent 技能查询正常
- [ ] 38. 消息发送正常
- [ ] 39. 状态查询正常
- [ ] 40. OAuth 登录入口正常
- [ ] 41. 回调端点响应正常
- [ ] 42. 完整登录流程正常
- [ ] 43. 用户信息获取正常
- [ ] 44. 前端访问后端正常
- [ ] 45. Second Me 按钮工作正常
- [ ] 46. 登录状态保持正常
- [ ] 47. 数据加载正常

### 应急预案（5项）
- [ ] 48. 数据库已备份
- [ ] 49. 回滚脚本就绪
- [ ] 50. 紧急联系人已确认

**总计 50 项，全部勾选后方可上线！**

---

**上线日期**: _______________  
**上线时间**: _______________  
**上线负责人**: _______________  
**确认签字**: _______________

---

**文档版本**: 1.0  
**最后更新**: 2025-02-27  
**适用项目**: MedRoundTable  
**下次审查日期**: _______________
