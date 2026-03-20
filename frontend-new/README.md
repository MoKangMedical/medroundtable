# Second Me OAuth + MCP 集成指南

## 概述

此目录包含 MedRoundTable 与 Second Me 平台的 OAuth 登录集成，以及用于 OpenClaw / SecondMe Integration 的最小 MCP endpoint。

## 文件结构

```
frontend-new/
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   └── auth/
│   │   │       ├── route.ts          # OAuth 登录入口
│   │   │       └── callback/
│   │   │           └── route.ts      # OAuth 回调处理
│   │   ├── mcp/
│   │   │   └── route.ts              # MCP endpoint
│   │   ├── layout.tsx                # 根布局
│   │   └── page.tsx                  # 登录页面
│   └── lib/
│       ├── medroundtable-mcp.ts      # MCP 工具定义
│       └── secondme.ts               # SecondMe 协作配置
├── .env.example                      # 环境变量模板
└── README.md                         # 本文件
```

## 配置步骤

### 1. 创建 Second Me 应用

1. 访问 https://app.secondme.io/developer
2. 创建新应用
3. 获取 Client ID 和 Client Secret
4. 设置回调 URL:
   - 本地开发：`http://localhost:3000/api/auth/callback`
   - 生产演示：`https://medroundtable-secondme.vercel.app/api/auth/callback`

### 2. 配置环境变量

```bash
cp .env.example .env.local
# 编辑 .env.local，填入你的 Second Me 凭证
```

### 3. 安装依赖

```bash
npm install
# 或
yarn install
```

### 4. 初始化数据库

```bash
npx prisma init
npx prisma db push
```

### 5. 运行开发服务器

```bash
npm run dev
```

## OAuth 流程

```
用户点击登录
    ↓
GET /api/auth/login
    ↓
重定向到 Second Me OAuth 页面
    ↓
用户授权
    ↓
重定向到 /api/auth/callback?code=xxx&state=xxx
    ↓
验证 state
    ↓
用 code 换 access token
    ↓
获取用户信息
    ↓
保存到数据库
    ↓
设置 session cookie
    ↓
重定向到 /role-select
```

## API 端点

### GET /api/auth/login

初始化 OAuth 流程，重定向到 Second Me 授权页面。

### GET /api/auth/callback

处理 OAuth 回调：
- 验证 state 防止 CSRF
- 交换 code 获取 access token
- 获取用户信息
- 设置 session

### GET /api/mcp

返回当前 MCP 端点的 server info、工具摘要、support/privacy 链接。
当前实现会公开返回 MCP server info，但真正的 `tools/call` 必须带 `Authorization: Bearer <token>`，并且 token 会用于解析当前 SecondMe 用户身份。

### POST /api/mcp

支持最小 JSON-RPC / MCP 工作流：
- `initialize`
- `tools/list`
- `tools/call`
- `ping`

当前可用工具：
- `triage_research_question`
- `build_roundtable_plan`
- `list_agent_roster`
- `search_public_databases`
- `get_platform_snapshot`

MCP endpoint 会返回 `authMode: bearer_token`，并明确 `authRequiredForToolCalls: true`，这样更贴近 SecondMe Integration 的 user-scoped bearer 模式。

## 环境变量说明

| 变量名 | 说明 | 获取方式 |
|--------|------|----------|
| SECONDME_CLIENT_ID | Second Me 应用 ID | 开发者后台创建应用 |
| SECONDME_CLIENT_SECRET | Second Me 应用密钥 | 开发者后台查看 |
| SECONDME_REDIRECT_URI | 回调 URL | 必须与后台配置一致 |
| SECONDME_PROFILE_ENDPOINT | 用户信息接口 | 默认指向 SecondMe 用户信息 API |
| MEDROUNDTABLE_WEB_URL | 正式站地址 | 用于生成 handoff URL |
| DATABASE_URL | 数据库连接字符串 | 本地开发使用 SQLite |
| NEXTAUTH_SECRET | 加密密钥 | 随机生成 |

## 故障排除

### "invalid_state" 错误
- 检查 cookies 是否被浏览器阻止
- 确认 state cookie 在 10 分钟内有效

### "Token exchange failed" 错误
- 检查 Client ID 和 Client Secret 是否正确
- 确认回调 URL 与 Second Me 后台配置一致

### 用户信息获取失败
- 确认 access token 未过期
- 检查 Second Me API 是否正常

### MCP endpoint 返回 404 或空工具
- 确认部署的是 `frontend-new` 项目，而不是纯静态 GitHub Pages 根站
- 确认 `https://medroundtable-secondme.vercel.app/api/mcp` 可直接访问
- 确认 Vercel 环境变量中已设置 `MEDROUNDTABLE_WEB_URL`

## 安全建议

1. 始终验证 state 参数
2. 使用 httpOnly cookies 存储 session
3. 在生产环境使用 HTTPS
4. 定期刷新 access token
5. 不要在客户端暴露 Client Secret
6. 如果把 MCP Integration 提交到 SecondMe，优先提供 support/privacy 页面，降低审核摩擦

## 相关链接

- SecondMe Developer Skill: https://develop.second.me/skill.md
- SecondMe 开发者文档: https://develop-docs.second.me/zh/docs
- OAuth 2.0 规范: https://oauth.net/2/
- Next.js 文档: https://nextjs.org/docs
