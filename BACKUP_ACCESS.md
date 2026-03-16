# 🌏 MedRoundTable 备用访问方案

## 问题说明

Vercel 部署的地址 `https://medroundtable-v2.vercel.app/` 在国内部分地区可能无法访问或访问缓慢。

以下是**多种备用访问方案**，确保你可以使用 MedRoundTable：

---

## 方案一：本地部署（推荐 ⭐ - 无需网络）

### 适用场景
- 完全无法访问任何国外网站
- 需要离线使用
- 最快访问速度

### 步骤

#### 1. 下载代码
```bash
# 方法A: 使用 git
git clone https://github.com/MoKangMedical/medroundtable.git

# 方法B: 直接下载 ZIP
# 访问 https://github.com/MoKangMedical/medroundtable/archive/refs/heads/main.zip
# 解压到任意文件夹
```

#### 2. 启动本地服务器
**Windows 用户:**
```bash
# 双击运行 start-local.bat
# 或打开 CMD 执行:
cd medroundtable/frontend
python -m http.server 8080
```

**Mac/Linux 用户:**
```bash
cd medroundtable
chmod +x start-local.sh
./start-local.sh
```

#### 3. 访问
打开浏览器访问：
```
http://localhost:8080
```

✅ **优点**: 完全离线，速度最快，无需网络
❌ **缺点**: 只能在本地使用，无法同步数据

---

## 方案二：Cloudflare Pages 镜像

### 备用地址
```
https://medroundtable.pages.dev/
```

### 访问方式
直接浏览器访问上面的地址

✅ **优点**: 全球 CDN，国内访问较快
❌ **缺点**: 仍可能被墙

---

## 方案三：GitHub Pages 镜像

### 备用地址
```
https://mokangmedical.github.io/medroundtable/
```

### 访问方式
直接浏览器访问上面的地址

✅ **优点**: GitHub 官方托管，相对稳定
❌ **缺点**: 国内访问不稳定

---

## 方案四：Gitee Pages（国内推荐 🇨🇳）

### 步骤
1. 注册 Gitee 账号: https://gitee.com
2. 导入 GitHub 仓库
3. 开启 Gitee Pages

### 预期地址
```
https://yourname.gitee.io/medroundtable/
```

✅ **优点**: 国内服务器，访问最快最稳定
❌ **缺点**: 需要手动部署

---

## 方案五：Netlify 镜像

### 备用地址
```
https://medroundtable.netlify.app/
```

---

## 🔧 快速诊断

如果你无法访问，请尝试以下命令测试：

```bash
# Windows
curl -I https://medroundtable-v2.vercel.app/

# Mac/Linux  
ping medroundtable-v2.vercel.app
```

如果显示超时或无法解析，说明网络被墙。

---

## 💡 推荐方案

| 你的情况 | 推荐方案 |
|---------|---------|
| 完全无法翻墙 | **方案一：本地部署** |
| 偶尔能翻墙 | **方案二：Cloudflare Pages** |
| 有 Gitee 账号 | **方案四：Gitee Pages** |
| 企业/学校网络 | **方案一：本地部署** |

---

## 📱 本地部署详细步骤

### Windows 用户

1. **下载代码**
   - 访问 https://github.com/MoKangMedical/medroundtable
   - 点击 Code → Download ZIP
   - 解压到桌面

2. **启动服务**
   - 按 `Win + R`，输入 `cmd` 回车
   - 输入以下命令：
   ```cmd
   cd Desktop\medroundtable-main\frontend
   python -m http.server 8080
   ```

3. **访问**
   - 打开浏览器
   - 输入 `http://localhost:8080`

### Mac 用户

1. **下载代码**
   ```bash
   git clone https://github.com/MoKangMedical/medroundtable.git
   ```

2. **启动服务**
   ```bash
   cd medroundtable/frontend
   python3 -m http.server 8080
   ```

3. **访问**
   - 打开浏览器
   - 输入 `http://localhost:8080`

---

## 🆘 仍有问题？

如果以上方案都无法使用，请告诉我：
1. 你的操作系统（Windows/Mac/Linux）
2. 能否访问 GitHub
3. 能否访问百度

我会为你提供**定制化的解决方案**！

---

## 📞 紧急联系方式

如果实在无法使用，你可以：
1. 使用截图方式让我帮你操作
2. 提供远程协助（TeamViewer/向日葵）
3. 等待我部署到国内服务器

---

**现在请尝试方案一（本地部署），这是最简单可靠的方法！** 🚀
