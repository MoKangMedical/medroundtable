# MedRoundTable - 一键部署到 GitHub

## ✅ 代码已准备好！

项目位置：`/root/.openclaw/workspace/medroundtable`

---

## 第一步：在 GitHub 创建仓库

1. 访问 https://github.com/new
2. 填写：
   - **Repository name**: `medroundtable`
   - **Description**: A2A Medical Research Collaboration Platform
   - 选择 **Public**
   - 勾选 **Add a README file**
3. 点击 **Create repository**

---

## 第二步：获取 GitHub Token

1. 访问 https://github.com/settings/tokens
2. 点击 **Generate new token (classic)**
3. 勾选权限：
   - ✅ `repo` (完整仓库权限)
4. 点击 **Generate token**
5. **复制保存 Token** (只显示一次！)

---

## 第三步：推送代码

在服务器上执行：

```bash
cd /root/.openclaw/workspace/medroundtable

# 配置 Git
git config user.name "MoKangMedical"
git config user.email "smartresearch2026@163.com"

# 添加远程仓库 (将 YOUR_TOKEN 替换为你的 Token)
git remote add origin https://MoKangMedical:YOUR_TOKEN@github.com/MoKangMedical/medroundtable.git

# 推送代码
git branch -M main
git push -u origin main --force
```

如果成功，会显示：
```
Enumerating objects: 45, done.
Writing objects: 100% (45/45), 45.23 KiB | 15.08 MiB/s, done.
To https://github.com/MoKangMedical/medroundtable.git
 * [new branch]      main -> main
```

---

## 第四步：部署到 Railway (后端)

1. 访问 https://railway.app/new
2. 点击 **Deploy from GitHub repo**
3. 选择 `MoKangMedical/medroundtable`
4. 点击 **Deploy Now**
5. 等待部署完成 (2-3分钟)
6. 点击 **Variables** → **New Variable**:
   - Name: `SECRET_KEY`
   - Value: `medroundtable-secret-key-2024` (随机字符串)
7. 再次点击 **New Variable**:
   - Name: `MOONSHOT_API_KEY`
   - Value: `sk-JRT2t7Pnqq7Cm2wh6nw1G2QcK9OxNBAFujR3zhD2GzqkbFbz`
8. 点击 **Deploy** 重新部署
9. 等待完成，记录域名：
   - 点击 **Settings** → **Domain**
   - 例如：`medroundtable-api.up.railway.app`

---

## 第五步：更新前端 API 地址

1. 在服务器上修改文件：
```bash
cd /root/.openclaw/workspace/medroundtable
nano frontend/index.html
```

2. 找到第 274-283 行，修改为：
```javascript
const API_BASE = 'https://medroundtable-api.up.railway.app/api/v1';
```
(将域名替换为 Railway 实际分配的域名)

3. 保存并推送：
```bash
git add frontend/index.html
git commit -m "Update API endpoint"
git push
```

---

## 第六步：部署到 Vercel (前端)

1. 访问 https://vercel.com/new
2. 点击 **Import Git Repository**
3. 选择 `MoKangMedical/medroundtable`
4. 配置：
   - **Framework Preset**: `Other`
   - **Build Command**: (留空)
   - **Output Directory**: `frontend`
5. 点击 **Deploy**
6. 等待完成，获得永久域名：
   - 例如：`medroundtable.vercel.app`

---

## 🎉 完成！

你的永久链接：
- **前端**: https://medroundtable.vercel.app
- **后端**: https://medroundtable-api.up.railway.app

---

## 测试

1. 访问 https://medroundtable.vercel.app
2. 点击 "Agent 介绍"
3. 如果能看到5位专家，说明部署成功！
4. 创建圆桌会测试功能

---

## 遇到问题？

如果在任何步骤卡住，请告诉我：
1. 你在哪一步
2. 具体的错误信息
3. 截图 (如果方便)

我会立即帮你解决！🦊
