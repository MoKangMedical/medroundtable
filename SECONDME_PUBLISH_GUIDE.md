# 🚀 MedRoundTable V2.0 - Second Me 发布操作指南

## 📋 发布前准备清单

### ✅ 已完成（本地）
- [x] 代码更新：14个AI Agent已配置
- [x] Git提交：2个commit待推送
- [x] 应用清单：secondme-manifest.json已更新V2.0
- [x] 发布材料：SECONDME_PUBLISH_APPLICATION.md已准备

### ⏳ 待完成
- [ ] GitHub代码推送（等待Token）
- [ ] Second Me开发者平台提交
- [ ] 生产环境部署

---

## 🎯 Second Me 发布步骤（详细）

### Step 1: 访问开发者中心 (1分钟)
```
🔗 URL: https://app.secondme.io/developer
```
- 使用Second Me账号登录
- 如果没有账号需要先注册

### Step 2: 创建新应用 (2分钟)
点击 **"创建新应用"** 或 **"Submit New App"**

#### 基本信息
| 字段 | 填写内容 |
|------|---------|
| **应用名称** | MedRoundTable |
| **显示名称** | 临床科研圆桌会 |
| **英文名称** | MedRoundTable - Clinical Research Roundtable |
| **应用描述** | 全球首个基于A2A架构的医学科研协作平台，14位专业AI Agent实现从临床问题到科研成果的全流程自动化协作 |
| **一句话简介** | AI驱动的医学科研协作平台，让临床研究像开组会一样简单 |
| **应用分类** | 医疗健康 > 科研工具 |

#### 应用图标
- 上传路径: `frontend/assets/doctors.jpg`
- 或自定义设计一个圆形logo (512x512px)

### Step 3: 技术配置 (3分钟)

#### A2A协议配置
| 配置项 | 值 |
|--------|-----|
| **A2A版本** | 1.0 |
| **Discovery端点** | `https://medroundtable.zeabur.app/api/a2a/discovery` |
| **Messaging端点** | `https://medroundtable.zeabur.app/api/a2a/message` |
| **Task端点** | `https://medroundtable.zeabur.app/api/a2a/task` |
| **Webhook URL** | `https://medroundtable.zeabur.app/api/a2a/webhook/secondme` |
| **OAuth回调URL** | `https://medroundtable.zeabur.app/api/auth/callback` |

#### OAuth2配置
- **授权端点**: `https://go.second.me/oauth/authorize`
- **Token端点**: `https://medroundtable.zeabur.app/api/auth/token`
- **Scopes**: `profile`, `email`, `shades:read`, `softmemory:read`

### Step 4: 上传应用清单 (1分钟)
上传文件: `secondme-manifest.json`

**文件位置**: `/root/.openclaw/workspace/medroundtable/secondme-manifest.json`

**文件内容包含**:
- 14个AI Agent完整配置
- 定价方案（免费版/专业版/团队版）
- 工作流定义
- 技术端点配置

### Step 5: 填写定价信息 (2分钟)

#### 免费版
- **价格**: ¥0
- **功能**: 5次/月基础分析，标准响应速度

#### 专业版
- **价格**: ¥299/月
- **功能**: 
  - 14个Agent无限使用
  - 优先响应
  - 高级导出功能
  - 邮件支持

#### 团队版
- **价格**: ¥999/月
- **功能**:
  - 最多5人协作
  - 定制Agent
  - API访问
  - 专属客服

### Step 6: 提交审核 (1分钟)
- 点击 **"提交审核"** 或 **"Submit for Review"**
- 确认所有信息填写正确
- 等待审核通知（1-3个工作日）

---

## 📊 应用亮点展示

### 🤖 14大AI Agent阵容

#### 核心临床团队 (5个)
1. 👨‍⚕️ 资深临床主任 - 研究价值评估
2. 📚 临床博士生 - 文献检索协调
3. 📊 临床流行病学家 - 研究设计
4. 📈 数据统计专家 - CRF设计分析
5. 👩‍⚕️ 研究护士 - 数据采集质控

#### ClawBio生物信息学套件 (4个)
6. 💊 药物基因组学专家 - 个性化用药
7. 🧬 GWAS专家 - 全基因组关联
8. 🔬 单细胞测序分析师 - scRNA-seq
9. 🌌 Galaxy桥接器 - 8000+工具

#### 专业研究Agent (5个)
10. 🔬 UX研究员 - 用户体验研究
11. 🧬 AI数据工程师 - 数据管道
12. 🔭 趋势研究员 - 市场情报
13. 🧪 实验追踪员 - 实验管理
14. 🔬 模型QA专家 - AI质量保证

### 🔄 9阶段科研流程
```
临床问题 → 文献回顾 → 研究设计 → CRF设计 → 
数据收集 → 基因组分析 → 统计分析 → 结果解释 → 论文撰写
```

### 📈 平台数据
- **总Agent数**: 14个
- **技能总数**: 30+ (可扩展至997)
- **数据库**: 17个生物医学数据库
- **支持语言**: 中文、英文

---

## 🔗 相关链接

| 用途 | 链接 |
|------|------|
| **GitHub** | https://github.com/MoKangMedical/medroundtable |
| **Hackathon** | https://hackathon.second.me/projects/cmlg779kn000204kvr6jygh28 |
| **演示环境** | https://medroundtable.zeabur.app |
| **API文档** | https://medroundtable.zeabur.app/docs |

---

## ⏰ 时间规划

| 阶段 | 预计时间 | 状态 |
|------|----------|------|
| GitHub推送 | 5分钟 | ⏳ 等待Token |
| Second Me提交 | 10分钟 | ⏳ 等待执行 |
| 审核等待 | 1-3工作日 | ⏳ 待开始 |
| 上线运营 | 审核通过后 | ⏳ 待开始 |

---

## 📝 备注

**开发者**: MoKangMedical (齐天大圣)  
**提交时间**: 2026-03-16  
**版本**: V2.0.0  
**更新内容**: 新增9个专业Agent（ClawBio生物信息学套件+5个专业研究Agent）

---

*准备好后，直接访问 https://app.secondme.io/developer 开始提交！* 🚀
