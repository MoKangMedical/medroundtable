# 🚀 GitHub Pages 自动部署配置指南

## 自动配置完成！

已为您创建 GitHub Actions 工作流，实现自动部署。

---

## 📦 已创建的文件

```
.github/workflows/pages.yml      # GitHub Actions 工作流
enable-github-pages.sh           # 自动启用脚本（可选）
```

---

## ⚡ 快速启用（推荐）

### 方法一：GitHub 网页界面（最简单）

1. **访问设置页**
   ```
   https://github.com/MoKangMedical/medroundtable/settings/pages
   ```

2. **选择部署源**
   - Source: `GitHub Actions`

3. **点击 Save**

4. **完成！**
   - 访问 https://mokangmedical.github.io/medroundtable/

### 方法二：命令行脚本

```bash
# 1. 进入仓库
cd /root/.openclaw/workspace/medroundtable

# 2. 运行启用脚本（可选）
chmod +x enable-github-pages.sh
./enable-github-pages.sh

# 3. 提交工作流文件
git add .github/workflows/pages.yml
git commit -m "ci: Add GitHub Pages deployment workflow"
git push origin main
```

---

## 🔄 自动部署机制

启用后，以下操作将自动触发部署：

| 操作 | 触发结果 |
|------|----------|
| `git push origin main` | 自动部署最新版本 |
| 修改 `docs/` 目录 | 自动重新构建 |
| 手动点击 "Run workflow" | 强制重新部署 |

---

## 🌐 部署地址

启用后可通过以下地址访问：

```
https://mokangmedical.github.io/medroundtable/
```

---

## 📁 网站文件结构

```
docs/
├── index.html      # 首页
├── skills.html     # AI技能矩阵
├── agents.html     # 完整工具生态（14个Agent）
├── workflow.html   # 工作流程
├── tech.html       # 技术支撑
└── benefits.html   # 效益优势
```

---

## 🛠️ 故障排查

### 部署失败？

1. **检查 Actions 日志**
   - 访问: https://github.com/MoKangMedical/medroundtable/actions

2. **常见错误**
   - ❌ "Pages not enabled": 需要在设置中启用 Pages
   - ❌ "Permission denied": 检查仓库权限
   - ❌ "Build failed": 检查 HTML 文件是否有语法错误

3. **手动触发部署**
   ```bash
   gh workflow run pages.yml
   ```

---

## 📝 更新网站内容

```bash
# 1. 修改文件
vim docs/agents.html

# 2. 提交到 GitHub
git add docs/
git commit -m "feat: Update agent showcase"
git push origin main

# 3. 自动部署（约 1-2 分钟）
# 访问 https://mokangmedical.github.io/medroundtable/ 查看最新版本
```

---

## 🎯 下一步操作

请立即访问以下链接启用 GitHub Pages：

👉 **[点击启用 GitHub Pages](https://github.com/MoKangMedical/medroundtable/settings/pages)**

然后选择 **GitHub Actions** 作为部署源，点击 Save 即可。

---

## ✅ 完成清单

- [x] GitHub Actions 工作流已创建
- [x] 展示页面已提交到 docs/ 目录
- [x] 自动部署配置已完成
- [ ] 在 GitHub 设置中启用 Pages（需要您手动操作）

---

**配置时间**: 2026-03-18  
**工作流文件**: `.github/workflows/pages.yml`