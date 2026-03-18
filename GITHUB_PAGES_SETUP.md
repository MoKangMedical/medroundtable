# GitHub Pages 部署说明

## 🚀 自动部署已配置

所有展示页面已提交到 `docs/` 目录，可以启用 GitHub Pages 自动部署。

## 📋 启用步骤

### 1. 进入仓库设置
访问: https://github.com/MoKangMedical/medroundtable/settings/pages

### 2. 配置 GitHub Pages
- **Source**: Deploy from a branch
- **Branch**: main / docs
- **Folder**: / (root)

### 3. 保存设置
点击 "Save" 按钮

## 🌐 访问地址

启用后，网站将通过以下地址访问：
```
https://mokangmedical.github.io/medroundtable/
```

## 📁 文件结构

```
docs/
├── index.html      # 首页
├── skills.html     # AI技能矩阵
├── agents.html     # 完整工具生态 (14个Agent)
├── workflow.html   # 工作流程
├── tech.html       # 技术支撑
└── benefits.html   # 效益优势
```

## 🔄 自动更新

一旦启用 GitHub Pages，任何推送到 `main` 分支的变更都会自动部署：

1. 修改 HTML 文件
2. 提交到 GitHub: `git push origin main`
3. GitHub Pages 自动更新（约 1-2 分钟）

## 📱 页面列表

| 页面 | 路径 | 说明 |
|------|------|------|
| 首页 | /index.html | 平台概览 |
| AI技能矩阵 | /skills.html | 997项技能展示 |
| 完整工具生态 | /agents.html | 14个Agent详细展示 |
| 工作流程 | /workflow.html | 9阶段科研流程 |
| 技术支撑 | /tech.html | 四大技术支柱 |
| 效益优势 | /benefits.html | ROI与成本分析 |

## ✅ 已提交的内容

### 代码更新
- ✅ 14个A2A Agent完整实现
- ✅ AgentRole枚举扩展
- ✅ /discovery端点更新
- ✅ 9阶段讨论流程

### 展示网站
- ✅ 6个HTML页面
- ✅ 移动端响应式设计
- ✅ 完整的导航链接
- ✅ 14个Agent卡片展示

---

**提交时间**: 2026-03-18
**提交ID**: 3b75f8e