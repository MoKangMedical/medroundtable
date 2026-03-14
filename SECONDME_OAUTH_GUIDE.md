# Second Me OAuth 申请指南

## 📍 回调URL配置

**主回调地址**: `https://medroundtable.zeabur.app/api/auth/callback`

**备用回调地址** (可选): `https://medroundtable-v2.vercel.app/auth/callback`

---

## 申请步骤

### 步骤1: 访问开发者中心
1. 打开浏览器访问: https://app.secondme.io/developer
2. 使用 Second Me 账号登录
3. 点击左侧菜单「我的应用」

### 步骤2: 创建新应用
1. 点击右上角「创建应用」按钮
2. 填写应用信息:

| 字段 | 填写内容 |
|------|---------|
| 应用名称 | `MedRoundTable` |
| 应用描述 | `全球首个基于A2A架构的医学科研协作平台` |
| 应用图标 | 上传 logo.png (建议尺寸 512x512) |

3. 点击「下一步」

### 步骤3: 配置OAuth
1. 在「OAuth配置」标签页
2. 填写回调URL:
   ```
   https://medroundtable.zeabur.app/api/auth/callback
   ```
3. 选择权限范围 (Scopes):
   - ✅ `profile` - 获取用户基本信息
   - ✅ `email` - 获取用户邮箱
   - ✅ `shades:read` - 读取用户Shades信息
   - ✅ `softmemory:read` - 读取用户记忆
4. 点击「保存」

### 步骤4: 获取密钥
1. 创建完成后进入应用详情页
2. 在「凭证」标签页找到:

| 字段 | 用途 | 复制位置 |
|------|------|---------|
| Client ID | 前端OAuth流程 | `.env.production` 的 `SECONDME_CLIENT_ID` |
| Client Secret | 后端Token交换 | `.env.production` 的 `SECONDME_CLIENT_SECRET` |

3. 点击「显示」查看 Client Secret
4. 复制并保存到安全位置

### 步骤5: 提交审核（如需公开）
1. 完成应用配置后点击「提交审核」
2. 等待 Second Me 团队审核
3. 审核通过后即可被其他用户使用

---

## 🔐 权限范围说明

| Scope | 权限说明 | 必需性 |
|-------|---------|-------|
| `profile` | 获取用户ID、昵称、头像 | 必需 |
| `email` | 获取用户邮箱地址 | 推荐 |
| `shades:read` | 读取用户的AI Shades列表 | 推荐 |
| `softmemory:read` | 读取用户的SoftMemory数据 | 可选 |

---

## 🧪 测试验证方法

### 测试1: OAuth授权流程
```bash
# 1. 构造授权URL
AUTH_URL="https://go.second.me/oauth/authorize?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=https://medroundtable.zeabur.app/api/auth/callback&scope=profile email&state=test123"

echo "在浏览器中打开:"
echo $AUTH_URL
```

**预期结果**: 浏览器显示 Second Me 授权页面，用户可点击「允许」

### 测试2: 回调端点测试
```bash
# 模拟回调请求（使用无效code测试端点响应）
curl -X GET "https://medroundtable.zeabur.app/api/auth/callback?code=invalid_code&state=test123"
```

**预期结果**: 返回错误信息但不崩溃，如 `{"error": "invalid_code"}`

### 测试3: Token交换测试
```bash
# 需要有效的授权码（通过浏览器获取）
curl -X POST "https://medroundtable.zeabur.app/api/auth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "grant_type": "authorization_code",
    "code": "AUTHORIZATION_CODE_FROM_BROWSER",
    "redirect_uri": "https://medroundtable.zeabur.app/api/auth/callback",
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET"
  }'
```

**预期结果**: 返回JSON包含 `access_token` 和 `refresh_token`

### 测试4: 前端集成测试
1. 打开前端页面: https://medroundtable-v2.vercel.app
2. 点击「Second Me 登录」按钮
3. 确认跳转至 Second Me 授权页面
4. 授权后确认返回应用并已登录

---

## 🔧 常见问题

### 问题1: "redirect_uri_mismatch"
**原因**: 回调URL与配置不一致
**解决**: 检查 Zeabur 控制台中的环境变量 `SECONDME_REDIRECT_URI` 是否与 Second Me 开发者中心配置完全一致

### 问题2: "invalid_client"
**原因**: Client ID 或 Client Secret 错误
**解决**: 
1. 重新复制 Client ID 和 Secret
2. 检查是否有多余空格
3. 确认使用的是生产环境密钥而非测试密钥

### 问题3: 授权后无法获取用户信息
**原因**: Scope 未包含 `profile`
**解决**: 在 Second Me 开发者中心添加 `profile` 权限范围

### 问题4: Token 过期
**说明**: Access Token 默认有效期较短
**解决**: 使用 Refresh Token 获取新的 Access Token

---

## 📋 配置检查清单

- [ ] 已在 Second Me 开发者中心创建应用
- [ ] 已配置正确的回调URL
- [ ] 已选择所需的权限范围
- [ ] 已复制 Client ID 到环境变量
- [ ] 已复制 Client Secret 到环境变量
- [ ] 已重新部署应用使环境变量生效
- [ ] 已测试完整的OAuth登录流程

---

## 🔗 相关链接

- Second Me 开发者中心: https://app.secondme.io/developer
- OAuth 文档: https://docs.second.me/oauth
- API 参考: https://api.mindverse.com/docs
