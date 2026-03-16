# MedRoundTable - Second Me 平台发布申请

## 📋 应用基本信息

| 字段 | 内容 |
|------|------|
| **应用名称** | MedRoundTable |
| **显示名称** | 临床科研圆桌会 |
| **英文名称** | MedRoundTable - Clinical Research Roundtable |
| **应用描述** | 全球首个基于A2A架构的医学科研协作平台，14位专业AI Agent实现从临床问题到科研成果的全流程自动化协作 |
| **一句话简介** | AI驱动的医学科研协作平台，让临床研究像开组会一样简单 |
| **应用分类** | 医疗健康 / 科研工具 / AI协作 |
| **应用图标** | [上传前端/assets/doctors.jpg或自定义] |

---

## 🚀 技术架构

### A2A 协议集成
- **A2A 版本**: 1.0
- **Discovery 端点**: `https://api.medroundtable.com/api/a2a/discovery`
- **Messaging 端点**: `https://api.medroundtable.com/api/a2a/message`
- **Task 端点**: `https://api.medroundtable.com/api/a2a/task`
- **Webhook URL**: `https://api.medroundtable.com/api/a2a/webhook/secondme`
- **OAuth 回调**: `https://medroundtable.com/api/auth/callback`

### 核心功能
- ✅ Agent Discovery - 自动发现和连接
- ✅ A2A Messaging - 标准消息通信协议
- ✅ Task Orchestration - 任务委托与执行
- ✅ AI Space - 参与 Second Me 网络协作
- ✅ OAuth 2.0 - Second Me账号登录
- ✅ Memory Sync - 记忆和上下文共享

---

## 🤖 14大AI Agent阵容

### 核心临床团队 (5个)
| Agent | 角色 | 专长 |
|-------|------|------|
| 👨‍⚕️ 资深临床主任 | 临床问题识别与研究价值评估 | 临床判断、循证医学 |
| 📚 临床博士生 | 文献检索与研究协调 | 学术写作、项目协调 |
| 📊 临床流行病学家 | 研究设计与方案制定 | 方法学、质量控制 |
| 📈 数据统计专家 | CRF设计与统计分析 | 数据管理、可视化 |
| 👩‍⚕️ 研究护士 | 数据采集与质量控制 | GCP合规、数据录入 |

### ClawBio生物信息学套件 (4个)
| Agent | 角色 | 专长 |
|-------|------|------|
| 💊 药物基因组学专家 | 个性化用药指导 | CPIC指南、23andMe分析 |
| 🧬 GWAS专家 | 全基因组关联分析 | ClinVar、gnomAD查询 |
| 🔬 单细胞测序分析师 | scRNA-seq自动化分析 | Scanpy、细胞聚类 |
| 🌌 Galaxy桥接器 | 8000+生物信息学工具 | 工作流编排、工具发现 |

### 专业研究Agent (5个)
| Agent | 角色 | 专长 |
|-------|------|------|
| 🔬 UX研究员 | 用户体验研究 | 可用性测试、行为分析 |
| 🧬 AI数据工程师 | 自修复数据管道 | 语义聚类、数据质量 |
| 🔭 趋势研究员 | 市场情报分析 | 竞争分析、战略预测 |
| 🧪 实验追踪员 | 实验设计管理 | A/B测试、假设检验 |
| 🔬 模型QA专家 | AI模型质量保证 | 偏差检测、性能测试 |

---

## 🔄 9阶段科研协作流程

```
1. 临床问题发现 → 2. 文献回顾 → 3. 研究设计
       ↓
4. CRF设计 → 5. 数据收集 → 6. 基因组学分析
       ↓
7. 统计分析 → 8. 结果解释 → 9. 论文撰写
```

---

## 💰 商业模式

### SaaS订阅
- **免费版**: 5次/月基础分析
- **专业版**: ¥299/月 - 无限次分析 + 优先响应
- **团队版**: ¥999/月 - 多用户协作 + 定制Agent

### 按需付费
- 单次完整研究设计: ¥99
- 数据统计分析: ¥199
- 完整论文辅助: ¥499

### 企业服务
- 医院科研部门定制: ¥50,000+/年
- 医学院教学系统集成: ¥100,000+/年
- 多中心研究平台: 按项目定价

---

## 🛠 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | HTML5 + TailwindCSS + JavaScript |
| 后端 | FastAPI + Python 3.11 |
| AI | OpenAI/Claude/GLM API + 自定义Agent框架 |
| A2A | Second Me兼容协议 |
| 数据库 | SQLite + PostgreSQL |
| 部署 | Docker + Zeabur/Railway/Vercel |

---

## 📊 平台统计

- **总Agent数**: 14个
- **技能总数**: 30+ (可扩展至997项)
- **数据库**: 17个生物医学数据库
- **API版本**: V2.0
- **支持语言**: 中文、英文

---

## 📝 提交清单

- [x] A2A协议完整实现
- [x] Second Me OAuth登录
- [x] 14个专业Agent配置
- [x] 9阶段科研流程
- [x] Docker容器化部署
- [x] API文档完整
- [x] GitHub仓库开源
- [ ] 演示视频录制
- [ ] 生产环境部署
- [ ] Second Me审核通过

---

## 🔗 相关链接

- **GitHub**: https://github.com/MoKangMedical/medroundtable
- **Hackathon**: https://hackathon.second.me/projects/cmlg779kn000204kvr6jygh28
- **文档**: README.md + docs/
- **API文档**: `/docs` (Swagger UI)

---

## 📞 联系信息

**开发者**: MoKangMedical (齐天大圣)  
**提交时间**: 2026-03-16  
**审核状态**: ⏳ 等待提交

---

## 🎯 发布后计划

1. **Phase 1** (1-2周): Second Me平台上线，收集种子用户反馈
2. **Phase 2** (1个月): 添加更多医学专科Agent（肿瘤、心血管、神经等）
3. **Phase 3** (3个月): 集成真实临床研究数据源
4. **Phase 4** (6个月): 多中心协作功能，支持全球科研团队

---

*MedRoundTable - 让医学科研协作更智能、更高效* 🌟
