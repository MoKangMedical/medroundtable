# 🔌 MedRoundTable API 连接配置指南

## 📍 当前部署状态

| 服务 | 地址 | 状态 |
|------|------|------|
| 前端 (Vercel) | https://medroundtable-v2.vercel.app | ✅ 已上线 |
| 后端 (API) | http://43.134.3.158:8001 | ✅ 运行中 |

---

## ⚙️ 前端配置

### Vercel 环境变量配置

在 Vercel 控制台设置以下环境变量：

```bash
# API 基础地址
NEXT_PUBLIC_API_URL=http://43.134.3.158:8001

# 或者使用本地开发
# NEXT_PUBLIC_API_URL=http://localhost:8001
```

### 配置步骤

1. 登录 Vercel 控制台：https://vercel.com/dashboard
2. 选择 `medroundtable-v2` 项目
3. 进入 **Settings** → **Environment Variables**
4. 添加变量：
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `http://43.134.3.158:8001`
5. 点击 **Save**
6. 重新部署项目（Vercel 会自动重新部署）

---

## 🔄 API 端点列表

### A2A 协议端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/a2a/discovery` | GET | Agent 发现 |
| `/api/a2a/message` | POST | 发送消息 |
| `/api/a2a/task` | POST | 任务管理 |
| `/api/a2a/webhook/secondme` | POST | Second Me Webhook |

### 核心功能端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/api/roundtables` | GET/POST | 圆桌会话列表/创建 |
| `/api/roundtables/{id}` | GET/PUT/DELETE | 会话详情/更新/删除 |
| `/api/roundtables/{id}/messages` | GET/POST | 消息列表/发送 |
| `/api/roundtables/{id}/export` | POST | 导出结果 |
| `/api/literature/search` | POST | 文献检索 |
| `/api/study-design/generate` | POST | 生成研究设计 |
| `/api/crf/generate` | POST | 生成 CRF 表单 |
| `/api/analysis-plan/generate` | POST | 生成分析计划 |
| `/api/auth/login` | GET | Second Me OAuth 登录 |
| `/api/auth/callback` | GET | OAuth 回调处理 |

---

## 🧪 测试连接

### 1. 健康检查
```bash
curl http://43.134.3.158:8001/health
```

预期响应：
```json
{"status": "healthy", "timestamp": "2026-02-26T01:19:55.568177"}
```

### 2. A2A Discovery
```bash
curl http://43.134.3.158:8001/api/a2a/discovery
```

预期响应：
```json
{
  "agent_system": "MedRoundTable",
  "version": "1.0.0",
  "agents": [...],
  "endpoints": {...}
}
```

### 3. 从 Vercel 前端测试
在浏览器控制台执行：
```javascript
fetch('http://43.134.3.158:8001/api/a2a/discovery')
  .then(r => r.json())
  .then(data => console.log(data))
  .catch(e => console.error(e))
```

---

## 🔒 安全考虑

### 当前配置
- ✅ 后端 CORS 已开启 (`allow_origins=["*"]`)
- ⚠️ 允许所有来源（开发环境）

### 生产环境建议

#### 1. 限制 CORS 来源
修改 `backend/main.py`：
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://medroundtable-v2.vercel.app",
        "https://app.secondme.io",  # Second Me 平台
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 2. 使用 HTTPS
- 为后端配置 SSL 证书
- 使用 Nginx 反向代理
- 或者使用 Cloudflare Tunnel

#### 3. API 认证
- 实现 API Key 验证
- 或使用 JWT Token

---

## 🚀 部署方案选项

### 方案 A：当前配置（开发/测试）
- 前端：Vercel (全球 CDN)
- 后端：当前服务器 (43.134.3.158)
- 优点：快速上线，成本低
- 缺点：后端单点，无 HTTPS

### 方案 B：Vercel + Serverless（推荐）
将后端转换为 Vercel Serverless Functions：
1. 创建 `api/` 目录
2. 将 FastAPI 路由转换为 Serverless Functions
3. 使用 Vercel Postgres 或 Neon 数据库

### 方案 C：完整云部署
- 前端：Vercel
- 后端：AWS/GCP/Azure ECS 或 EC2
- 数据库：RDS / Cloud SQL
- 优点：高可用，自动扩缩容
- 缺点：成本较高

---

## 📋 Second Me 集成配置

### Manifest 已更新
文件：`secondme-manifest.json`

```json
{
  "interfaces": {
    "web": {
      "url": "https://medroundtable-v2.vercel.app"
    },
    "api": {
      "base_url": "http://43.134.3.158:8001"
    }
  }
}
```

### 更新 Second Me 平台
1. 访问：https://app.secondme.io/developer
2. 找到 MedRoundTable 应用
3. 重新上传 `secondme-manifest.json`
4. 验证 A2A Discovery 端点

---

## 🐛 故障排查

### 问题 1：前端无法连接后端
**症状**：浏览器控制台显示 CORS 错误

**解决**：
1. 确认后端运行：`curl http://43.134.3.158:8001/health`
2. 检查防火墙：`sudo ufw status` 或 `iptables -L`
3. 确认 CORS 配置正确

### 问题 2：API 返回 404
**症状**：某些端点返回 404

**解决**：
1. 确认 URL 路径正确
2. 检查后路由是否已注册
3. 查看后端日志：`docker logs medroundtable-api`

### 问题 3：Second Me 无法发现 Agent
**症状**：Second Me 平台显示连接失败

**解决**：
1. 确认 `/api/a2a/discovery` 可访问
2. 检查 manifest 中的 endpoints 配置
3. 验证网络连通性

---

## 📝 更新记录

| 日期 | 更新内容 |
|------|----------|
| 2026-02-26 | 更新 manifest 生产环境 URL |
| 2026-02-26 | 创建 API 连接配置文档 |

---

**如有问题，随时联系！** 🚀
