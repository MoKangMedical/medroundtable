# MedRoundTable 项目完整文件清单

**项目位置**: `/root/.openclaw/workspace/medroundtable`  
**原部署地址**: https://medroundtable-v2.vercel.app/  
**版本**: V2.0 (整合997项技能)

---

## 📁 目录结构

```
medroundtable/
├── 📂 agents/                    # Agent定义和逻辑
├── 📂 assets/                    # 静态资源
├── 📂 backend/                   # FastAPI后端
│   ├── 📂 routes/               # API路由
│   │   ├── 📂 auth/             # 认证系统 (新增)
│   │   ├── 📂 databases/        # 数据库浏览器 (新增)
│   │   ├── 📂 skills/           # 技能市场 (新增)
│   │   └── 📂 trials/           # 临床试验 (新增)
│   └── *.py                     # 后端核心模块
├── 📂 config/                    # 配置文件
├── 📂 data/                      # 数据目录
├── 📂 docs/                      # 文档目录
├── 📂 frontend/                  # 前端文件
│   └── 📂 src/components/       # React组件
├── 📂 frontend-new/              # Next.js前端 (Second Me OAuth)
├── 📂 infrastructure/            # 基础设施配置
│   ├── 📂 kubernetes/           # K8s配置
│   └── 📂 terraform/            # Terraform配置
├── 📂 scripts/                   # 部署脚本
├── 📂 skills/                    # 技能注册中心 (新增)
└── 📂 templates/                 # 模板文件
```

---

## 🔧 后端核心文件 (Python)

### API主入口
| 文件 | 说明 | 状态 |
|------|------|------|
| `backend/main.py` | FastAPI主应用 | ✅ 已更新V2 |
| `backend/models.py` | 数据模型 | ✅ |
| `backend/database.py` | 数据库操作 | ✅ |

### 业务逻辑
| 文件 | 说明 | 状态 |
|------|------|------|
| `backend/literature.py` | 文献检索逻辑 | ✅ |
| `backend/templates.py` | 模板管理 | ✅ |
| `backend/exporter.py` | 数据导出 | ✅ |
| `backend/study_design_generator.py` | 研究方案生成 | ✅ |
| `backend/citation_manager.py` | 引用管理 | ✅ |

### Agent系统
| 文件 | 说明 | 状态 |
|------|------|------|
| `agents/orchestrator.py` | Agent编排器 | ✅ |
| `agents/llm_client.py` | LLM客户端 | ✅ |
| `agents/prompts.py` | 提示词模板 | ✅ |

---

## 🆕 V2.0 新增核心文件

### 技能系统
| 文件 | 说明 | 代码行数 |
|------|------|---------|
| `skills/registry.py` | 技能注册中心 | ~250行 |
| `backend/routes/skills/marketplace.py` | 技能市场API | ~280行 |
| `frontend/src/components/SkillMarketplace/index.js` | 技能市场前端 | ~250行 |
| `frontend/src/components/SkillMarketplace/SkillMarketplace.css` | 样式 | ~180行 |

### 数据库浏览器
| 文件 | 说明 | 代码行数 |
|------|------|---------|
| `backend/routes/databases/biomedical.py` | 数据库API | ~350行 |

### 临床试验设计器
| 文件 | 说明 | 代码行数 |
|------|------|---------|
| `backend/routes/trials/designer.py` | 试验设计API | ~380行 |

### 自研认证系统 (替代Second Me)
| 文件 | 说明 | 代码行数 |
|------|------|---------|
| `backend/routes/auth/custom_auth.py` | 认证API | ~420行 |
| `backend/routes/auth/__init__.py` | 认证模块入口 | ~10行 |
| `frontend/login.html` | 登录页面 | ~400行 |

---

## 📄 文档文件 (Markdown)

### 项目文档
| 文件 | 说明 |
|------|------|
| `README.md` | 项目简介 |
| `MEDROUNDTABLE_V2_INTEGRATION_REPORT.md` | **V2整合报告** (新增) |
| `DEPLOYMENT_GUIDE.md` | **部署指南** (新增) |

### 部署文档 (原有)
| 文件 | 说明 |
|------|------|
| `DEPLOYMENT.md` | 部署说明 |
| `DEPLOY_CHECKLIST.md` | 部署清单 |
| `DEPLOY_COMPLETE.md` | 部署完成 |
| `DEPLOYMENT_COMPLETE.md` | 部署完成详情 |
| `DEPLOY_PERMANENT.md` | 永久部署 |
| `DEPLOY_TO_GITHUB.md` | GitHub部署 |
| `DEPLOY_ZEABUR.md` | Zeabur部署 |
| `QUICK_DEPLOY.md` | 快速部署 |
| `DEPLOY_BACKEND_CLOUD.md` | 后端云部署 |
| `DEPLOY_CHINA.md` | 中国部署指南 |
| `docs/ZEABUR_DEPLOY.md` | Zeabur详细 |
| `docs/QUICK_DEPLOY_CHINA.md` | 中国快速部署 |

### 环境配置
| 文件 | 说明 |
|------|------|
| `ENV_CHECKLIST.md` | 环境检查 |
| `ENV_SETUP_GUIDE.md` | 环境设置 |

### Second Me 相关 (可弃用)
| 文件 | 说明 | 状态 |
|------|------|------|
| `SECONDME_SETUP.md` | Second Me设置 | ⚠️ 可弃用 |
| `SECONDME_OAUTH_GUIDE.md` | OAuth指南 | ⚠️ 可弃用 |
| `SECONDME_SUBMISSION_GUIDE.md` | 提交指南 | ⚠️ 可弃用 |
| `SECONDME_VERIFICATION.md` | 验证清单 | ⚠️ 可弃用 |
| `SECONDME_SUBMISSION_SUMMARY.txt` | 提交摘要 | ⚠️ 可弃用 |
| `secondme-manifest.json` | 应用清单 | ⚠️ 可弃用 |
| `secondme-integration.sh` | 集成脚本 | ⚠️ 可弃用 |

### 用户指南
| 文件 | 说明 |
|------|------|
| `docs/USER_GUIDE.md` | 用户指南 |
| `docs/SECONDME_API_GUIDE.md` | API指南 |
| `docs/API_CONNECTION_GUIDE.md` | API连接指南 |
| `docs/ARCHITECTURE.md` | 架构文档 |

### 其他文档
| 文件 | 说明 |
|------|------|
| `PROGRESS.md` | 进度记录 |
| `PROGRESS_NEW.md` | 新进度 |
| `IMPROVEMENT.md` | 改进建议 |
| `LAUNCH_CHECKLIST.md` | 上线清单 |
| `LAUNCH_FINAL_CHECKLIST.md` | 最终上线清单 |
| `FEEDBACK_COLLECTION.md` | 反馈收集 |
| `RUNNING.md` | 运行说明 |

---

## 🎨 前端文件

### HTML页面
| 文件 | 说明 | 状态 |
|------|------|------|
| `frontend/index.html` | 主页面 | ✅ |
| `frontend/login.html` | **登录页面** (新增) | ✅ |
| `frontend/feedback.html` | 反馈页面 | ✅ |
| `frontend/feedback-v2.html` | 反馈V2 | ✅ |
| `frontend/quick-feedback.html` | 快速反馈 | ✅ |
| `frontend/index-mobile.html` | 移动端 | ✅ |
| `frontend/index-old.html` | 旧版 | ✅ |
| `frontend/test.html` | 测试页 | ✅ |
| `v2-demo.html` | **V2演示页** (新增) | ✅ |

### JavaScript
| 文件 | 说明 |
|------|------|
| `frontend/mindmap.js` | 思维导图 |
| `frontend/user-system.js` | 用户系统 |

### React组件
| 文件 | 说明 | 状态 |
|------|------|------|
| `frontend/src/components/SkillMarketplace/index.js` | **技能市场** (新增) | ✅ |
| `frontend/src/components/SkillMarketplace/SkillMarketplace.css` | **样式** (新增) | ✅ |

### Next.js前端 (Second Me)
| 文件 | 说明 | 状态 |
|------|------|------|
| `frontend-new/README.md` | 说明 | ⚠️ 可弃用 |

---

## ⚙️ 配置文件

### Docker
| 文件 | 说明 |
|------|------|
| `Dockerfile` | Docker构建 |
| `docker-compose.yml` | 本地编排 |
| `docker-compose.prod.yml` | 生产编排 |

### 部署配置
| 文件 | 说明 | 平台 |
|------|------|------|
| `vercel.json` | Vercel配置 | Vercel |
| `railway.json` | Railway配置 | Railway |
| `railway.toml` | Railway TOML | Railway |
| `render.yaml` | Render配置 | Render |
| `sealos.yaml` | Sealos配置 | Sealos |
| `zeabur.json` | Zeabur配置 | Zeabur |
| `zeabur.toml` | Zeabur TOML | Zeabur |
| `nginx.conf` | Nginx配置 | Nginx |

### 环境变量
| 文件 | 说明 |
|------|------|
| `.env` | 环境变量 |
| `.env.example` | 示例 |
| `.env.production` | 生产环境 |

### 其他配置
| 文件 | 说明 |
|------|------|
| `a2a-config.json` | A2A配置 |
| `config/agents_config.json` | Agent配置 |
| `cors_config.py` | CORS配置 |
| `requirements.txt` | Python依赖 |
| `package.json` | Node依赖 |

---

## 🔧 脚本文件 (Shell)

### 部署脚本
| 文件 | 说明 |
|------|------|
| `launch.sh` | 一键启动 |
| `start.sh` | 启动服务 |
| `start-production.sh` | 生产启动 |
| `quick-launch.sh` | 快速启动 |
| `auto-deploy.sh` | 自动部署 |
| `deploy-auto.sh` | 自动部署2 |
| `deploy-production.sh` | 生产部署 |
| `deploy-railway.sh` | Railway部署 |
| `deploy-zeabur.sh` | Zeabur部署 |
| `deploy-pm2.sh` | PM2部署 |
| `prepare-zeabur.sh` | Zeabur准备 |
| `update-after-zeabur.sh` | Zeabur更新 |
| `update-domain.sh` | 域名更新 |
| `verify-deployment.sh` | 验证部署 |

### 维护脚本
| 文件 | 说明 |
|------|------|
| `keepalive.sh` | 保活脚本 |
| `monitor.sh` | 监控脚本 |
| `status.sh` | 状态检查 |
| `push-to-github.sh` | 推送到GitHub |
| `improve_with_stepfun.py` | 阶跃星辰优化 |

### 测试脚本 (新增)
| 文件 | 说明 |
|------|------|
| `test-v2-api.sh` | **V2 API测试** |
| `start-and-test.sh` | **启动并测试** |

### 工具脚本
| 文件 | 说明 |
|------|------|
| `setup-https.sh` | HTTPS设置 |
| `setup-https-cloudflare.sh` | Cloudflare HTTPS |
| `setup-cloudflare-tunnel.sh` | Cloudflare隧道 |
| `quick-tunnel.sh` | 快速隧道 |

---

## 📊 文件统计

| 类型 | 数量 | 说明 |
|------|------|------|
| Python文件 | 20+ | 后端核心 |
| HTML文件 | 10+ | 前端页面 |
| JS文件 | 5+ | JavaScript逻辑 |
| Markdown文档 | 30+ | 项目文档 |
| Shell脚本 | 25+ | 部署脚本 |
| 配置文件 | 15+ | 各种配置 |
| **总计** | **100+** | - |

---

## 🆚 文件变更对比

### V1.0 → V2.0 新增文件

#### 核心功能 (必看)
```
backend/routes/auth/custom_auth.py          # 自研认证 ⭐
backend/routes/auth/__init__.py
backend/routes/databases/biomedical.py      # 数据库浏览器 ⭐
backend/routes/skills/marketplace.py        # 技能市场 ⭐
backend/routes/trials/designer.py           # 临床试验 ⭐
skills/registry.py                          # 技能注册中心 ⭐
frontend/login.html                         # 登录页面 ⭐
frontend/src/components/SkillMarketplace/   # 技能市场组件 ⭐
```

#### 文档和脚本
```
MEDROUNDTABLE_V2_INTEGRATION_REPORT.md      # V2整合报告 ⭐
DEPLOYMENT_GUIDE.md                         # 部署指南 ⭐
docs/MIGRATION_TO_CUSTOM_AUTH.md            # 认证迁移 ⭐
test-v2-api.sh                              # 测试脚本 ⭐
start-and-test.sh                           # 启动脚本 ⭐
v2-demo.html                                # 演示页面 ⭐
```

### 可清理的文件 (Second Me相关)
```
frontend-new/                               # Next.js前端 ⚠️
secondme-manifest.json                      # Second Me清单 ⚠️
secondme-integration.sh                     # Second Me脚本 ⚠️
SECONDME_*.md                               # Second Me文档 ⚠️
```

---

## 🎯 关键文件推荐查看

### 想了解V2新功能？
1. `MEDROUNDTABLE_V2_INTEGRATION_REPORT.md` - V2整合报告
2. `skills/registry.py` - 技能注册中心
3. `backend/routes/skills/marketplace.py` - 技能市场API

### 想了解自研认证？
1. `docs/MIGRATION_TO_CUSTOM_AUTH.md` - 迁移指南
2. `backend/routes/auth/custom_auth.py` - 认证API
3. `frontend/login.html` - 登录页面

### 想部署上线？
1. `DEPLOYMENT_GUIDE.md` - 部署指南
2. `vercel.json` - Vercel配置
3. `test-v2-api.sh` - 测试脚本

---

## 📌 文件路径速查

```
# V2核心文件
~/medroundtable/skills/registry.py
~/medroundtable/backend/routes/skills/marketplace.py
~/medroundtable/backend/routes/databases/biomedical.py
~/medroundtable/backend/routes/trials/designer.py
~/medroundtable/backend/routes/auth/custom_auth.py
~/medroundtable/frontend/login.html
~/medroundtable/frontend/src/components/SkillMarketplace/

# 文档
~/medroundtable/MEDROUNDTABLE_V2_INTEGRATION_REPORT.md
~/medroundtable/docs/MIGRATION_TO_CUSTOM_AUTH.md
~/medroundtable/DEPLOYMENT_GUIDE.md

# 测试脚本
~/medroundtable/test-v2-api.sh
~/medroundtable/start-and-test.sh
```

---

*文件清单生成时间: 2026-03-14*  
*为大圣整理 🌸💜*
