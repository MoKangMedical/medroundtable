# Second Me 平台提交指南

> 当前提审请优先使用 [secondme-integration-manifest.json](/Users/linzhang/Desktop/%20%20%20%20%20%20OPC/medroundtable-fixes/secondme-integration-manifest.json) 和 [SECONDME_STORE_SUBMISSION.md](/Users/linzhang/Desktop/%20%20%20%20%20%20OPC/medroundtable-fixes/SECONDME_STORE_SUBMISSION.md)。
> 下面的 A2A 叙述保留为历史背景，不再作为新版 Integration 提审口径。

## 🚀 提交前检查清单

### ✅ 已完成项目

- [x] **A2A 协议集成**
  - [x] Agent Discovery 端点 (`/api/a2a/discovery`)
  - [x] Agent Messaging 端点 (`/api/a2a/message`)
  - [x] Task Management 端点 (`/api/a2a/task`)
  - [x] Webhook 支持 (`/api/a2a/webhook/secondme`)

- [x] **Second Me OAuth 登录**
  - [x] OAuth 登录入口 (`/api/auth/login`)
  - [x] OAuth 回调处理 (`/api/auth/callback`)
  - [x] 用户资料同步

- [x] **配置文件**
  - [x] `secondme-manifest.json` - 应用清单
  - [x] `a2a-config.json` - A2A 协议配置
  - [x] `SECONDME_VERIFICATION.md` - 验证文档

- [x] **部署就绪**
  - [x] Docker 容器化
  - [x] 生产环境配置
  - [x] API 文档完整

---

## 📋 提交步骤

### 1. 访问 Second Me 开发者中心

打开浏览器访问：
```
https://app.secondme.io/developer
```

### 2. 登录账号

使用 Second Me 账号登录（如果没有需要先注册）

### 3. 创建新应用

点击 **"创建新应用"** 或 **"Submit New App"**

### 4. 填写应用信息

#### 基本信息
| 字段 | 填写内容 |
|------|---------|
| **应用名称** | MedRoundTable |
| **显示名称** | 临床科研圆桌会 |
| **应用描述** | 全球首个基于A2A架构的医学科研协作平台，五位专业AI Agent实现从临床问题到科研成果的全流程自动化协作 |
| **应用图标** | 上传 `frontend/assets/doctors.jpg` 或自定义图标 |
| **应用分类** | 医疗健康 / 科研工具 |

#### 技术信息
| 字段 | 填写内容 |
|------|---------|
| **A2A 协议版本** | 1.0 |
| **Discovery 端点** | `https://your-api-domain.com/api/a2a/discovery` |
| **Messaging 端点** | `https://your-api-domain.com/api/a2a/message` |
| **Webhook URL** | `https://your-api-domain.com/api/a2a/webhook/secondme` |
| **OAuth 回调 URL** | `https://your-frontend-domain.com/api/auth/callback` |

### 5. 上传配置文件

上传 `secondme-manifest.json` 文件内容

### 6. 提交审核

点击 **"提交审核"** 或 **"Submit for Review"**

---

## 🔧 部署配置

### 后端 API 部署

**使用 Docker Compose:**
```bash
cd /root/.openclaw/workspace/medroundtable
./deploy-production.sh
```

**服务地址:**
- 后端 API: `http://your-server:8001`
- 前端页面: `http://your-server:3001`

### 环境变量配置

创建 `.env` 文件:
```bash
# Second Me OAuth
SECONDME_CLIENT_ID=your_client_id_from_secondme
SECONDME_CLIENT_SECRET=your_client_secret_from_secondme
SECONDME_REDIRECT_URI=https://your-domain.com/api/auth/callback

# Database
DATABASE_URL=sqlite:///app/data/medroundtable.db

# Security
SECRET_KEY=your_random_secret_key
```

---

## 📊 应用特性展示

### 5大AI Agent

1. **👨‍⚕️ 资深临床主任** - 临床问题识别与研究价值评估
2. **📚 临床博士生** - 文献检索与研究协调
3. **📊 临床流行病学家** - 研究设计与方案制定
4. **📈 数据统计专家** - CRF设计与统计分析
5. **👩‍⚕️ 研究护士** - 数据采集与质量控制

### A2A 协作流程

```
临床问题提出 
    ↓
圆桌讨论（5个Agent实时互动）
    ↓
研究方案设计 → 数据表格构建 → 数据采集执行 → 统计分析 → 成果产出
```

### Second Me 集成特性

- ✅ Agent 自动发现与连接
- ✅ A2A 消息通信协议
- ✅ 任务委托与执行
- ✅ AI Space 协作
- ✅ OAuth 账号登录
- ✅ 用户兴趣同步
- ✅ 软记忆数据获取

---

## 📞 联系信息

**开发者:** MoKangMedical  
**GitHub:** https://github.com/MoKangMedical/medroundtable  
**Hackathon:** https://hackathon.second.me/projects/cmlg779kn000204kvr6jygh28  
**Email:** [待填写]

---

## 🎯 审核后计划

1. **Phase 1:** Second Me 平台上线
2. **Phase 2:** 收集用户反馈
3. **Phase 3:** 添加更多医学专科Agent
4. **Phase 4:** 集成真实临床研究数据

---

## 📝 提交确认

**提交日期:** [待填写]  
**审核状态:** ⏳ 等待审核  
**预计上线:** 审核通过后 1-3 个工作日

**提交者:** 齐天大圣 (MoKangMedical)  
**提交时间:** 2026-01-26

---

## 🔗 相关链接

- **项目主页:** https://github.com/MoKangMedical/medroundtable
- **演示视频:** [待录制]
- **使用文档:** README.md
- **API文档:** docs/SECONDME_API_GUIDE.md
- **架构设计:** docs/ARCHITECTURE.md
