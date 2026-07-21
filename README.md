# MedRoundTable - Second Me 部署指南

🩺 **AI-powered Clinical Research Roundtable Platform**

5位专业AI专家协作平台，助力临床研究设计。

## 正式环境（唯一对外入口）

- 正式网站：[https://medroundtable.cn/](https://medroundtable.cn/)
- 全流程分析观察台：[https://medroundtable.cn/real-analysis.html](https://medroundtable.cn/real-analysis.html)
- API 健康检查：[https://medroundtable.cn/api/health](https://medroundtable.cn/api/health)
- Relay 健康检查：[https://medroundtable.cn/api/v1/relay/health](https://medroundtable.cn/api/v1/relay/health)

生产环境由腾讯云 Ubuntu + Nginx + FastAPI 承载。GitHub 用于代码留痕和部署源；不再使用第三方静态托管页面作为展示入口。详见 [DEPLOYMENT.md](DEPLOYMENT.md)。

## 🚀 快速开始

### 方式一：使用 Second Me CLI

```bash
# 1. 进入项目目录
cd medroundtable-secondme

# 2. 启动服务
bash start.sh

# 3. 访问应用
# 前端: http://localhost:3000
# 后端: http://localhost:8000
```

### 方式二：使用 Python 直接运行

```bash
# 1. 安装依赖
pip install fastapi uvicorn python-docx python-dotenv

# 2. 启动后端
cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000

# 3. 启动前端（新开终端）
cd frontend
python3 -m http.server 3000
```

## 🏗️ 系统架构

### 5位AI专家 (A2A Multi-Agent Architecture)

| 专家角色 | 职责 |
|---------|------|
| 👨‍⚕️ 临床主任 | 研究策略、终点指标、临床意义评估 |
| 👩‍🎓 博士生 | 文献检索、证据整合、研究背景 |
| 👨‍⚕️ 流行病学家 | 方案设计、偏倚控制、伦理考量 |
| 👨‍💼 统计学家 | 样本量计算、统计方法、分析计划 |
| 👩‍⚕️ 研究护士 | 访视流程、数据管理、质量控制 |

### 技术栈

- **前端**: HTML5 + Tailwind CSS + Vanilla JavaScript
- **后端**: Python FastAPI
- **AI模型**: Kimi K2.5 (Moonshot)
- **数据库**: SQLite (可扩展至PostgreSQL)
- **部署**: Python HTTP Server + Uvicorn

## 📋 功能特性

### 核心功能
- ✅ 5位AI专家实时讨论
- ✅ 用户可随时干预对话
- ✅ 上下文感知的智能回复
- ✅ 自动文献引用
- ✅ 研究方案Word导出
- ✅ 讨论思维导图可视化
- ✅ 响应式UI设计

### 高级功能
- 🔐 JWT用户认证
- 📚 会话历史管理
- 💬 SSE实时消息推送
- 🎨 专业医疗主题配色
- 📱 移动端适配

## ⚙️ 环境配置

### 必需环境变量

```bash
# Kimi API配置
export MOONSHOT_API_KEY="your-kimi-api-key"
export MOONSHOT_BASE_URL="https://api.moonshot.cn/v1"
export MOONSHOT_MODEL="moonshot-v1-32k"
```

### 配置文件 (.env)

```
MOONSHOT_API_KEY=sk-xxxxx
MOONSHOT_BASE_URL=https://api.moonshot.cn/v1
MOONSHOT_MODEL=moonshot-v1-32k
DATABASE_URL=sqlite:///./medroundtable.db
```

## 🔌 API 接口

### 核心端点

```
POST   /api/v1/roundtables          # 创建圆桌会
GET    /api/v1/roundtables/{id}     # 获取圆桌会详情
POST   /api/v1/roundtables/{id}/start    # 开始讨论
POST   /api/v1/roundtables/{id}/message  # 发送消息
GET    /api/v1/roundtables/{id}/stream   # SSE消息流
GET    /api/v1/sessions              # 获取会话列表
POST   /api/v1/auth/register        # 用户注册
POST   /api/v1/auth/login           # 用户登录
GET    /health                       # 健康检查
```

## 🌐 部署方式

### 1. 本地部署
```bash
bash start.sh
```

### 2. Cloudflare Tunnel (公网访问)
```bash
# 前端
cloudflared tunnel --url http://localhost:3000

# 后端
cloudflared tunnel --url http://localhost:8000
```

### 3. Docker 部署 (可选)
```dockerfile
# Dockerfile 待添加
```

### 4. Second Me 平台部署
```bash
# 使用 Second Me CLI
secondme deploy

# 或使用 claude 命令
claude medroundtable-secondme
```

## 📝 使用教程

### 创建研究讨论

1. 打开前端界面
2. 点击"开始新的圆桌会"
3. 填写研究标题（如：二甲双胍对2型糖尿病的疗效研究）
4. 填写临床问题（详细描述研究目标和问题）
5. 点击"开始讨论"
6. 观看5位AI专家自动讨论

### 干预讨论

- 在输入框输入您的问题或意见
- 相关专家会回应您的提问
- 讨论会继续进行

### 导出研究方案

- 讨论完成后，点击"导出方案"
- 自动生成Word文档，包含：
  - 研究设计
  - 样本量计算
  - 纳入/排除标准
  - 统计方法
  - 访视计划

## 🛠️ 开发指南

### 项目结构

```
medroundtable/
├── frontend/           # 前端代码
│   ├── index.html     # 主页面
│   ├── mindmap.js     # 思维导图
│   └── assets/        # 静态资源
├── backend/           # 后端代码
│   ├── main.py        # FastAPI应用
│   ├── models.py      # 数据模型
│   └── routes/        # API路由
├── agents/            # AI智能体
│   ├── orchestrator.py # 编排器
│   ├── llm_client.py   # LLM客户端
│   └── prompts.py      # 系统提示词
├── docs/              # 文档
└── start.sh           # 启动脚本
```

### 添加新专家

1. 在 `agents/prompts.py` 中添加系统提示词
2. 在 `backend/models.py` 的 `AgentRole` 枚举中添加角色
3. 在 `orchestrator.py` 中注册新Agent

### 自定义提示词

编辑 `agents/prompts.py` 中的系统提示词模板。

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- Kimi/Moonshot 提供AI能力
- FastAPI 提供后端框架
- Tailwind CSS 提供样式支持

---

**让AI助力临床研究，让协作创造价值！** 🚀
