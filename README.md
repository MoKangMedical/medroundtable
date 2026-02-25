# MedRoundTable - 临床科研圆桌会

## 🎯 项目简介

MedRoundTable 是全球首个基于 A2A (Agent-to-Agent) 架构的医学科研协作平台。通过构建五位专业 AI Agent，实现从临床问题到科研成果的全流程自动化协作。

## 🤖 五大核心 Agent

1. **👨‍⚕️ 资深临床主任 Agent** - 识别科研价值、提出研究假设
2. **📚 临床博士生 Agent** - 文献检索、综述撰写、协调推进  
3. **📊 临床流行病学专家 Agent** - 研究设计、纳入排除标准
4. **📈 数据统计专家 Agent** - CRF设计、统计分析、图表生成
5. **👩‍⚕️ 研究护士 Agent** - 数据采集、质量核查、问题反馈

## 🔄 A2A 协作流程

```
临床问题提出 
    ↓
圆桌讨论（5个Agent实时互动）
    ↓
研究方案设计 → 数据表格构建 → 数据采集执行 → 统计分析 → 成果产出
```

## 💰 盈利模式

### 1. SaaS 订阅模式
- **免费版**: 5次/月基础分析
- **专业版** ¥299/月: 无限次分析 + 优先响应
- **团队版** ¥999/月: 多用户协作 + 定制Agent

### 2. 按需付费
- 单次完整研究设计: ¥99
- 数据统计分析: ¥199
- 完整论文辅助: ¥499

### 3. 企业/机构服务
- 医院科研部门定制: ¥50,000+/年
- 医学院教学系统集成: ¥100,000+/年
- 多中心研究平台: 按项目定价

### 4. 增值服务
- 专家人工审核: ¥200/次
- 英文润色服务: ¥500/篇
- 期刊投稿指导: ¥1,000/篇

## 🌉 Second Me 集成

MedRoundTable 已完整支持 [Second Me](https://secondme.io) A2A (Agent-to-Agent) 协议，可在 Second Me 平台直接运行：

- ✅ **Agent Discovery** - 自动发现和连接
- ✅ **A2A Messaging** - 标准消息通信协议
- ✅ **Task Orchestration** - 任务委托与执行
- ✅ **AI Space** - 参与 Second Me 网络协作
- ✅ **Memory Sync** - 记忆和上下文共享

**快速接入 Second Me:**
```bash
# 验证并自动集成
./secondme-integration.sh
```

**Hackathon 项目:** https://hackathon.second.me/projects/cmlg779kn000204kvr6jygh28

## 🛠 技术栈

- **前端**: React + TypeScript + TailwindCSS
- **后端**: FastAPI + Python
- **AI**: OpenAI/Claude API + 自定义Agent框架
- **A2A 协议**: Second Me 兼容
- **数据库**: PostgreSQL + Redis
- **部署**: Docker + Kubernetes

## 📁 项目结构

```
medroundtable/
├── frontend/          # React前端
├── backend/           # FastAPI后端
├── agents/            # Agent定义和逻辑
├── docs/              # 文档
└── assets/            # 静态资源
```

## 🚀 快速启动

```bash
# 1. 克隆项目
git clone https://github.com/MoKangMedical/Clinical-Research-Roundtable.git

# 2. 启动服务
cd medroundtable
docker-compose up -d

# 3. 访问 http://localhost:3000
```

## 📄 License

MIT License
