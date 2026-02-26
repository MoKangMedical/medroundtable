# 🚀 MedRoundTable 国内部署 - 快速开始

## 推荐方案（按优先级排序）

---

## 方案一：Zeabur（最简单 ⭐⭐⭐）

**适合**: 快速上线，不想配置服务器
**时间**: 5 分钟
**费用**: 有免费额度

### 部署步骤

#### 1. 访问 Zeabur
打开 https://zeabur.com
用 GitHub 账号登录

#### 2. 创建项目
- 点击 **"创建项目"**
- 选择 **"从 GitHub 导入"**
- 选择 `MoKangMedical/medroundtable` 仓库
- 点击 **"导入"**

#### 3. 配置服务
Zeabur 会自动识别 Python 项目，配置如下：
- **构建命令**: `pip install -r requirements.txt`
- **启动命令**: `uvicorn backend.main:app --host 0.0.0.0 --port 8080`
- **端口**: `8080`

#### 4. 设置环境变量
在 Zeabur 控制台，点击 **"环境变量"**，添加：

| 变量名 | 值 |
|--------|-----|
| SECRET_KEY | `openssl rand -hex 32` 生成的随机字符串 |
| DEBUG | `false` |
| DATABASE_URL | `sqlite:///app/data/medroundtable.db` |
| CORS_ORIGINS | `https://medroundtable-v2.vercel.app,https://app.secondme.io` |

#### 5. 部署
点击 **"部署"**，等待 2-3 分钟

#### 6. 获取域名
- 部署完成后，点击 **"域名"**
- 自动生成域名：`https://medroundtable-api-xxx.zeabur.app`
- 或点击 **"生成域名"** 创建自定义域名

#### 7. 测试
```bash
curl https://your-domain.zeabur.app/health
curl https://your-domain.zeabur.app/api/a2a/discovery
```

---

## 方案二：阿里云函数计算 FC（国内最快 ⭐⭐）

**适合**: 追求国内访问速度
**时间**: 10 分钟
**费用**: 免费额度充足

### 部署步骤

#### 1. 准备工作
- 注册阿里云账号：https://www.aliyun.com
- 开通函数计算 FC：https://fc.console.aliyun.com

#### 2. 创建服务
- 进入 FC 控制台
- 选择地域（推荐：华东1 - 杭州）
- 创建服务：名称 `medroundtable`

#### 3. 创建函数
- 点击 **"创建函数"**
- 选择 **"使用自定义运行时"**
- 配置：
  - **函数名称**: `api`
  - **运行环境**: `Python 3.11`
  - **函数执行内存**: `512 MB`
  - **超时时间**: `60 秒`

#### 4. 上传代码
有两种方式：

**方式 A：直接上传 ZIP**
```bash
# 在服务器上打包
cd /root/.openclaw/workspace/medroundtable
zip -r deploy.zip backend/ agents/ requirements.txt
# 下载 deploy.zip 到本地，然后上传到阿里云
```

**方式 B：使用 OSS**
- 将代码上传到 OSS
- 在函数配置中选择 OSS 地址

#### 5. 配置启动命令
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 9000
```

#### 6. 设置环境变量
在函数配置的 **"环境变量"** 标签页添加：
```
SECRET_KEY=xxx
DEBUG=false
DATABASE_URL=/tmp/medroundtable.db  # FC 只能写入 /tmp
CORS_ORIGINS=https://medroundtable-v2.vercel.app
```

#### 7. 配置触发器
- 点击 **"触发器"**
- 创建触发器：
  - **触发器类型**: `HTTP`
  - **请求方法**: `ANY`
  - **认证方式**: `无需认证`

#### 8. 获取域名
- 触发器创建后会自动生成域名
- 格式：`https://xxx.cn-hangzhou.fc.aliyuncs.com`

---

## 方案三：Sealos（云原生 ⭐⭐）

**适合**: 需要更多控制权，熟悉 Kubernetes
**时间**: 10 分钟
**费用**: 按量付费

### 部署步骤

#### 1. 访问 Sealos
https://cloud.sealos.cn

#### 2. 创建应用
- 点击 **"应用管理"**
- 点击 **"创建应用"**

#### 3. 配置应用
- **应用名称**: `medroundtable-api`
- **镜像**: `python:3.11-slim`
- **启动命令**: 
  ```bash
  sh -c "pip install -r requirements.txt && uvicorn backend.main:app --host 0.0.0.0 --port 8000"
  ```
- **端口**: `8000`

#### 4. 上传代码
- 在 **"存储"** 标签页添加存储卷
- 将代码挂载到 `/app`

#### 5. 设置环境变量
同上

#### 6. 部署
点击 **"部署"**

---

## 🔄 部署后统一操作

无论选择哪个平台，部署后都需要：

### 1. 更新 Second Me Manifest
编辑 `secondme-manifest.json`，更新 API URL：
```json
{
  "interfaces": {
    "api": {
      "base_url": "https://your-new-domain.com"
    }
  }
}
```
然后提交到 GitHub，并在 Second Me 平台重新上传。

### 2. 更新 Vercel 环境变量
登录 Vercel 控制台：
```bash
NEXT_PUBLIC_API_URL=https://your-new-domain.com
```

### 3. 测试完整链路
```bash
# 测试后端
curl https://your-new-domain.com/health

# 测试 A2A
curl https://your-new-domain.com/api/a2a/discovery

# 浏览器测试前端
# 打开 https://medroundtable-v2.vercel.app
# 查看控制台是否有跨域错误
```

---

## 🆘 常见问题

### 问题 1：部署失败
- 检查 Python 版本是否为 3.11
- 检查依赖是否安装成功（查看构建日志）
- 检查端口是否冲突

### 问题 2：API 返回 404
- 确认启动命令正确
- 确认路由配置正确
- 查看应用日志

### 问题 3：跨域错误
- 确认 `CORS_ORIGINS` 包含前端域名
- 确认后端服务已重启

### 问题 4：数据库错误
- SQLite 在某些平台只能写入 `/tmp` 目录
- 修改 `DATABASE_URL=/tmp/medroundtable.db`

---

## 📞 需要帮助？

如果遇到问题：
1. 查看平台日志
2. 测试本地服务是否正常：`curl http://localhost:8001/health`
3. 随时找我帮忙！

**推荐先用 Zeabur 试试，有问题再换其他平台！** 🚀
