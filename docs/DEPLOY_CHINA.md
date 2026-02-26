# 🇨🇳 MedRoundTable 国内部署指南

针对国内网络环境优化的后端部署方案。

---

## 🎯 推荐方案（国内可用）

### 方案一：Zeabur ⭐⭐⭐（推荐）

**特点**：
- ✅ 国内访问友好
- ✅ 部署简单（类似 Railway）
- ✅ 支持 Python/FastAPI
- ✅ 自动 HTTPS
- ✅ 免费额度充足

**官网**: https://zeabur.com

#### 部署步骤

```bash
# 1. 安装 Zeabur CLI
curl -fsSL https://raw.githubusercontent.com/zeabur/cli/main/install.sh | bash
export PATH="$HOME/.zeabur/bin:$PATH"

# 2. 登录（使用 GitHub 账号）
zeabur auth login

# 3. 进入项目目录
cd /root/.openclaw/workspace/medroundtable

# 4. 一键部署
./deploy-zeabur.sh
```

或使用配置文件部署：
```bash
# 创建项目
zeabur project create medroundtable-api

# 部署
zeabur deploy
```

#### 配置环境变量
在 Zeabur 控制台设置：
```bash
SECRET_KEY=your-random-secret-key
DEBUG=false
DATABASE_URL=sqlite:///app/data/medroundtable.db
CORS_ORIGINS=https://medroundtable-v2.vercel.app,https://app.secondme.io
```

---

### 方案二：阿里云函数计算 FC ⭐⭐

**特点**：
- ✅ 国内最快访问速度
- ✅ 按量付费，成本可控
- ✅ Serverless，自动扩缩容
- ⚠️ 需要阿里云账号

**官网**: https://fc.console.aliyun.com

#### 部署步骤

1. **安装 Serverless Devs**
```bash
npm install @serverless-devs/s -g
```

2. **配置阿里云密钥**
```bash
s config add --AccessKeyID your-ak --AccessKeySecret your-sk
```

3. **创建 s.yaml**
```yaml
edition: 3.0.0
name: medroundtable-api
access: default

vars:
  region: cn-hangzhou
  service:
    name: medroundtable
    description: MedRoundTable API

resources:
  api:
    component: fc3
    props:
      region: ${vars.region}
      serviceName: ${vars.service.name}
      functionName: api
      runtime: python3.11
      code: ./backend
      handler: main.handler
      memorySize: 512
      timeout: 60
      environmentVariables:
        SECRET_KEY: ${env.SECRET_KEY}
        DEBUG: "false"
      triggers:
        - triggerName: http
          triggerType: http
          qualifier: LATEST
```

4. **部署**
```bash
s deploy
```

---

### 方案三：腾讯云云函数 SCF ⭐⭐

**特点**：
- ✅ 国内访问稳定
- ✅ 免费额度充足
- ✅ 与腾讯云生态集成
- ⚠️ 需要腾讯云账号

**官网**: https://console.cloud.tencent.com/scf

#### 部署步骤

1. **安装 Serverless Framework**
```bash
npm install -g serverless
```

2. **配置腾讯云密钥**
```bash
serverless credentials set --secret-id your-id --secret-key your-key
```

3. **创建 serverless.yml**
```yaml
component: flask
name: medroundtable-api

inputs:
  region: ap-guangzhou
  runtime: Python3.11
  entryFile: backend/main.py
  memorySize: 512
  timeout: 60
  environment:
    SECRET_KEY: ${env:SECRET_KEY}
    DEBUG: false
```

4. **部署**
```bash
serverless deploy
```

---

### 方案四：Sealos 云原生平台 ⭐⭐⭐

**特点**：
- ✅ 国内云原生平台
- ✅ Kubernetes 原生
- ✅ 支持自定义域名
- ✅ 按量付费

**官网**: https://cloud.sealos.cn

#### 部署步骤

1. **访问 Sealos 控制台**
   https://cloud.sealos.cn

2. **创建应用**
   - 选择「应用管理」→「创建应用」
   - 上传 `sealos.yaml` 或使用表单配置

3. **配置容器**
   - 镜像：选择 Python 3.11
   - 启动命令：`uvicorn backend.main:app --host 0.0.0.0 --port 8000`
   - 端口：8000

4. **添加环境变量**
   ```bash
   SECRET_KEY=xxx
   DEBUG=false
   CORS_ORIGINS=https://medroundtable-v2.vercel.app
   ```

5. **部署**
   点击「部署」等待完成

---

### 方案五：当前服务器 + 国内 CDN ⭐⭐

如果不想迁移，可以用国内 CDN 加速当前服务器。

#### 使用又拍云 CDN
```bash
# 1. 注册又拍云 https://www.upyun.com
# 2. 创建 CDN 服务
# 3. 配置回源地址：43.134.3.158:8001
# 4. 开启 HTTPS
# 5. 绑定域名（如 api.medroundtable.cn）
```

#### 使用腾讯云 CDN
```bash
# 1. 注册腾讯云
# 2. 开通 CDN 服务
# 3. 添加域名，配置回源
# 4. 申请免费 SSL 证书
# 5. 配置 CNAME
```

---

## 📊 方案对比

| 平台 | 国内速度 | 免费额度 | 部署难度 | 推荐度 |
|------|----------|----------|----------|--------|
| **Zeabur** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ 简单 | ⭐⭐⭐ 首选 |
| **阿里云 FC** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ 中等 | ⭐⭐ |
| **腾讯云 SCF** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ 中等 | ⭐⭐ |
| **Sealos** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ 中等 | ⭐⭐ |
| **当前+CDN** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ 中等 | ⭐⭐ |

---

## 🚀 最快部署（Zeabur）

```bash
# 1. 安装 CLI
curl -fsSL https://raw.githubusercontent.com/zeabur/cli/main/install.sh | bash

# 2. 登录
zeabur auth login

# 3. 一键部署
cd /root/.openclaw/workspace/medroundtable
./deploy-zeabur.sh

# 4. 获取域名（约 2 分钟）
zeabur domain list
```

预期输出：
```
https://medroundtable-api.zeabur.app
```

---

## ⚠️ 注意事项

### 1. 备案要求
- 如果使用国内域名（.cn/.com.cn 等），需要备案
- 使用海外域名（如 .app/.dev）无需备案

### 2. Vercel 前端
- Vercel 在国内访问可能较慢
- 可考虑使用 Vercel 的国内 CDN 或换用 Netlify

### 3. 环境变量
国内平台环境变量设置方式可能不同，请参考各平台文档。

---

## 📝 部署后检查清单

- [ ] API 可访问：`curl https://your-domain/health`
- [ ] A2A Discovery 正常：`curl https://your-domain/api/a2a/discovery`
- [ ] CORS 配置正确（浏览器控制台无跨域错误）
- [ ] 更新 Second Me Manifest
- [ ] 更新 Vercel 环境变量
- [ ] 国内各地访问测试

---

## 🆘 故障排查

### 问题 1：部署失败
```bash
# 检查日志
zeabur logs --project medroundtable-api
```

### 问题 2：国内访问慢
- 检查是否使用了国内平台
- 开启 CDN 加速
- 使用国内域名解析（DNSPod）

### 问题 3：API 超时
- 增加函数超时时间（建议 60 秒以上）
- 检查数据库连接
- 查看平台日志

---

**选择最适合你的方案开始部署吧！** 🎉

有问题随时找我帮忙！
