# MedRoundTable - GitHub 部署指南

## 第一步：在 GitHub 创建仓库

1. 访问 https://github.com/new
2. 填写信息：
   - **Repository name**: `medroundtable` (或你喜欢的名字)
   - **Description**: A2A Medical Research Collaboration Platform
   - **Public** (推荐，免费用户只能部署公开仓库到 Vercel)
   - 勾选 **Add a README file** (可选)
3. 点击 **Create repository**

## 第二步：推送代码到 GitHub

在你的服务器上执行：

```bash
cd /root/.openclaw/workspace/medroundtable

# 添加远程仓库 (将 YOUR_USERNAME 替换为你的 GitHub 用户名)
git remote add origin https://github.com/YOUR_USERNAME/medroundtable.git

# 推送代码
git branch -M main
git push -u origin main
```

## 第三步：部署到 Railway (后端)

1. 访问 https://railway.app/new
2. 点击 **Deploy from GitHub repo**
3. 选择你刚创建的 `medroundtable` 仓库
4. 点击 **Deploy Now**
5. 等待部署完成 (约 2-3 分钟)
6. 点击 **Settings** → **Variables**
7. 添加环境变量：
   - `SECRET_KEY` = `your-random-secret-key-here` (随机字符串)
   - `MOONSHOT_API_KEY` = 在 Railway/VPS Secret 管理器中设置，不要提交到 Git
8. 点击 **Deploy** 重新部署
9. 记录域名：`https://medroundtable-api.up.railway.app`

## 第四步：部署到 Vercel (前端)

1. 访问 https://vercel.com/new
2. 导入你的 GitHub 仓库
3. 配置：
   - **Framework Preset**: `Other`
   - **Build Command**: (留空)
   - **Output Directory**: `frontend`
4. 点击 **Deploy**
5. 等待部署完成
6. 获得域名：`https://medroundtable.vercel.app`

## 第五步：更新 API 地址 (重要！)

1. 修改 `frontend/index.html` 第 274-283 行：
```javascript
// 修改为 Railway 的域名
const API_BASE = 'https://medroundtable-api.up.railway.app/api/v1';
```

2. 提交并推送：
```bash
git add frontend/index.html
git commit -m "Update API endpoint to Railway"
git push
```

3. Vercel 会自动重新部署

## 完成！🎉

你的永久链接：
- **前端**: https://medroundtable.vercel.app
- **后端**: https://medroundtable-api.up.railway.app

## 费用

- **Vercel**: 免费 (无限带宽)
- **Railway**: 免费 ($5/月额度，足够使用)
- **总费用**: $0

## 自定义域名 (可选)

如果你想用自己的域名：

1. **Vercel**: Settings → Domains → 添加你的域名
2. **Railway**: Settings → Domains → 添加你的域名
3. 在域名服务商添加 CNAME 记录

## 需要帮助？

如果在任何步骤遇到问题，请告诉我：
1. 你在哪一步卡住了
2. 具体的错误信息
3. 截图 (如果方便)

我会立即帮你解决！🦊
