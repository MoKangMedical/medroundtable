# 🚀 MedRoundTable 本地部署完整指南

## 📥 步骤 1：下载代码

### 方法 A：Git 克隆（推荐）
```bash
git clone https://github.com/MoKangMedical/medroundtable.git
```

### 方法 B：直接下载 ZIP
1. 访问：https://github.com/MoKangMedical/medroundtable
2. 点击绿色 **"Code"** 按钮
3. 点击 **"Download ZIP"**
4. 解压到任意文件夹（建议桌面）

---

## 🖥️ 步骤 2：启动本地服务器

### Windows 用户

#### 方式 1：使用批处理文件（最简单）
1. 进入解压后的文件夹
2. 双击运行 `start-local.bat`
3. 看到 "服务启动成功" 后，不要关闭黑窗口
4. 打开浏览器访问：`http://localhost:8080`

#### 方式 2：命令行启动
1. 按 `Win + R`，输入 `cmd`，回车
2. 输入以下命令：
```cmd
cd C:\Users\你的用户名\Desktop\medroundtable-main\frontend
python -m http.server 8080
```
3. 看到 "Serving HTTP on :: port 8080" 表示成功
4. 浏览器访问：`http://localhost:8080`

---

### Mac 用户

1. 打开 **终端**（Terminal）
2. 输入以下命令：
```bash
cd ~/Desktop/medroundtable-main/frontend
python3 -m http.server 8080
```
3. 看到 "Serving HTTP on :: port 8080" 表示成功
4. 浏览器访问：`http://localhost:8080`

---

## ✅ 步骤 3：验证14位专家

打开浏览器访问 `http://localhost:8080` 后，检查：

### 1. 页面标题
应该是：
```
MedRoundTable V2.0 - 14位AI专家医学科研协作平台
```

### 2. 向下滚动查看专家
应该看到三个分组：

**第一组 - 核心临床团队（5位）**
- 👨‍⚕️ 临床主任
- 📚 博士生
- 📊 流行病学家
- 📈 统计学家
- 👩‍⚕️ 研究护士

**第二组 - ClawBio生物信息学套件（4位）**
- 💊 药物基因组学专家
- 🧬 GWAS专家
- 🔬 单细胞测序分析师
- 🌌 Galaxy桥接器

**第三组 - 专业研究支持团队（5位）**
- 🔬 UX研究员
- 🧬 AI数据工程师
- 🔭 趋势研究员
- 🧪 实验追踪员
- 🔬 模型QA专家

---

## 🔧 常见问题

### 问题 1：提示 "python" 不是内部或外部命令

**解决**：安装 Python
1. 访问 https://www.python.org/downloads/
2. 下载 Python 3.11+
3. 安装时勾选 **"Add Python to PATH"**
4. 重新打开 CMD 再试

### 问题 2：端口 8080 被占用

**解决**：更换端口
```bash
# 使用 8081 端口
python -m http.server 8081

# 然后访问 http://localhost:8081
```

### 问题 3：页面显示 "无法访问此网站"

**解决**：
1. 确认黑窗口（CMD/终端）没有关闭
2. 确认输入的地址正确：`http://localhost:8080`
3. 尝试刷新页面（Ctrl + F5）

### 问题 4：还是只看到5位专家

**解决**：
1. 确认下载的是最新代码（重新下载 ZIP）
2. 确认访问的是 `http://localhost:8080`
3. 清除浏览器缓存（Ctrl + Shift + Delete）

---

## 📱 访问地址

启动成功后，在浏览器输入：
```
http://localhost:8080
```

或

```
http://127.0.0.1:8080
```

---

## 🛑 关闭服务器

使用完毕后：
- **Windows**：关闭 CMD 黑窗口
- **Mac**：在终端按 `Ctrl + C`

---

## 🎯 下一步

本地部署成功后：
1. ✅ 创建圆桌会
2. ✅ 测试14位专家回复
3. ✅ 体验完整功能

有问题随时问我！

---

**现在开始下载并部署吧！** 🚀
