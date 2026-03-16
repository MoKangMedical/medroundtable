# GitHub Pages 部署指南（国内备用访问）

## 🚀 快速部署（2分钟完成）

### 步骤 1: 进入 GitHub 仓库设置
1. 访问 https://github.com/MoKangMedical/medroundtable
2. 点击顶部 **Settings** 标签
3. 左侧菜单选择 **Pages**

### 步骤 2: 启用 GitHub Pages
1. **Source** 部分：
   - Branch: 选择 `main`
   - Folder: 选择 `/(root)`
   - 点击 **Save**

2. 等待 1-2 分钟部署完成

### 步骤 3: 访问地址
部署完成后，访问地址为：
```
https://mokangmedical.github.io/medroundtable/
```

---

## 📁 文件结构准备

GitHub Pages 需要从根目录或 `/docs` 文件夹部署。我们的前端文件在 `frontend/` 目录，需要调整。

### 方案 A: 移动文件到根目录（推荐）

```bash
# 将 frontend 内容复制到根目录
cp -r frontend/* ./
```

### 方案 B: 使用 docs 文件夹

```bash
# 创建 docs 文件夹并复制内容
mkdir -p docs
cp -r frontend/* docs/
```

然后在 Settings → Pages 中选择 `/docs` 文件夹。

---

## 🔧 配置自定义域名（可选）

如果你有国内域名，可以绑定：

1. 在仓库根目录创建 `CNAME` 文件
2. 文件内容填写你的域名，例如：
   ```
   medroundtable.yourdomain.com
   ```
3. 在域名 DNS 设置中添加 CNAME 记录指向 `mokangmedical.github.io`

---

## ✅ 部署检查清单

- [ ] 进入 Settings → Pages
- [ ] 选择 main 分支
- [ ] 点击 Save
- [ ] 等待 2 分钟
- [ ] 访问 `https://mokangmedical.github.io/medroundtable/`

---

## 🌏 国内访问优化

GitHub Pages 在国内访问可能仍不稳定，建议：

1. **使用 CDN**: 在域名 DNS 设置中使用国内 CDN（如又拍云、七牛云）
2. **Gitee 同步**: 同步到 Gitee 并使用 Gitee Pages
3. **Vercel 镜像**: 同时部署到 Vercel 作为备用

---

## 📞 帮助

如果部署遇到问题：

1. 检查 Settings → Pages 中显示的状态
2. 查看仓库的 Actions 标签页是否有错误
3. 确保 index.html 存在于部署的根目录

---

**现在就去 https://github.com/MoKangMedical/medroundtable/settings/pages 启用 GitHub Pages 吧！** 🚀
