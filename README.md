# MedRoundTable - 临床科研圆桌会

## 🎯 项目简介

MedRoundTable 是全球首个基于 A2A (Agent-to-Agent) 架构的医学科研协作平台。通过构建 **14位专业 AI Agent**，实现从临床问题到科研成果的全流程自动化协作。

## 🤖 14位核心 Agent

### 🏥 核心临床团队 (5位)
1. **👨‍⚕️ 资深临床主任 Agent** - 识别科研价值、提出研究假设
2. **📚 临床博士生 Agent** - 文献检索、综述撰写、协调推进  
3. **📊 临床流行病学专家 Agent** - 研究设计、纳入排除标准
4. **📈 数据统计专家 Agent** - CRF设计、统计分析、图表生成
5. **👩‍⚕️ 研究护士 Agent** - 数据采集、质量核查、问题反馈

### 🧬 ClawBio 生物信息学套件 (4位)
6. **💊 药物基因组学专家 Agent** - 个性化用药、基因型分析
7. **🧬 GWAS 专家 Agent** - 全基因组关联分析、变异查询
8. **🔬 单细胞测序分析师 Agent** - scRNA-seq分析、细胞聚类
9. **🌌 Galaxy 桥接器 Agent** - 8000+生信工具编排

### 🔬 专业研究支持团队 (5位)
10. **🔬 UX 研究员 Agent** - 用户体验研究、可用性测试
11. **🧬 AI 数据工程师 Agent** - 数据管道修复、质量优化
12. **🔭 趋势研究员 Agent** - 市场情报分析、竞争研究
13. **🧪 实验追踪员 Agent** - A/B测试设计、假设验证
14. **🔬 模型 QA 专家 Agent** - AI模型测试、偏差检测

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

## 🚀 快速访问

### 🌐 在线访问
- **主域名**: https://medroundtable.vip (配置中)
- **Vercel**: https://medroundtable-v2.vercel.app
- **GitHub Pages**: https://mokangmedical.github.io/medroundtable

### 💻 本地启动
```bash
# 1. 克隆项目
git clone https://github.com/MoKangMedical/medroundtable.git

# 2. 进入目录
cd medroundtable/frontend

# 3. 启动本地服务器
python3 -m http.server 8080

# 4. 访问 http://localhost:8080
```

### 🐳 Docker 部署
```bash
cd medroundtable
docker-compose up -d
```

## 📐 理论基础

### Harness 理论

在AI领域，Harness（环境设计）比模型本身更重要。优秀的Harness设计（工具链+信息格式+上下文管理+失败恢复+结果验证）能使性能提升64%。

MedRoundTable 的 A2A 多Agent协作架构正是 Harness 理论的体现：14位专业 Agent 的价值不在于单个模型的强弱，而在于协作流程设计、上下文传递机制、结果交叉验证的整体 Harness 质量。

### 红杉论点

> 下一代万亿美元公司是伪装成服务公司的软件公司。从卖工具到卖结果。

MedRoundTable 从科研协作工具进化为科研结果交付平台——用户提出临床问题，平台直接产出研究方案、数据分析和论文初稿，实现"从卖工具到卖结果"的转变。

### 理论宪法

本项目遵循理论宪法四卷八章统一框架，将医学科研协作的全流程建立在可验证、可复现、可扩展的理论根基之上。

## 📄 License

MIT License
