# Second Me API 集成完整指南

基于官方文档: https://develop-docs.second.me/zh/docs/api-reference/secondme

## Base URL

```
https://api.mindverse.com/gate/lab
```

## OAuth 2.0 流程

### 1. 授权端点

```
https://go.second.me/oauth/
```

参数:
- `client_id` - 应用 ID
- `redirect_uri` - 回调 URL
- `response_type` - 固定值 `code`
- `state` - 防 CSRF 随机字符串
- `prompt` - 可选，`consent` 强制显示授权页面

### 2. Token 交换端点

```
POST https://api.mindverse.com/gate/lab/api/oauth/token/code
```

参数:
- `grant_type` - 固定值 `authorization_code`
- `code` - 授权码
- `redirect_uri` - 回调 URL
- `client_id` - 应用 ID
- `client_secret` - 应用密钥

## 用户 API

### 获取用户信息

```http
GET /api/secondme/user/info
Authorization: Bearer {access_token}
```

**权限**: `user.info`

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "userId": "12345678",
    "name": "用户名",
    "email": "user@example.com",
    "avatar": "https://cdn.example.com/avatar.jpg",
    "bio": "个人简介",
    "selfIntroduction": "自我介绍内容",
    "profileCompleteness": 85,
    "route": "username"
  }
}
```

**字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| userId | string | 用户 ID |
| name | string | 用户姓名 |
| email | string | 用户邮箱 |
| avatar | string | 头像 URL |
| bio | string | 个人简介 |
| selfIntroduction | string | 自我介绍 |
| profileCompleteness | number | 资料完整度 (0-100) |
| route | string | 用户主页路由 |

### 获取用户兴趣标签

```http
GET /api/secondme/user/shades
Authorization: Bearer {access_token}
```

**权限**: `user.info.shades`

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "shades": [
      {
        "id": 123,
        "shadeName": "科技爱好者",
        "shadeIcon": "https://cdn.example.com/icon.png",
        "confidenceLevel": "HIGH",
        "shadeDescription": "热爱科技",
        "shadeDescriptionThirdView": "他/她热爱科技",
        "hasPublicContent": true
      }
    ]
  }
}
```

**置信度等级**:
- `VERY_HIGH` - 极高
- `HIGH` - 高
- `MEDIUM` - 中
- `LOW` - 低
- `VERY_LOW` - 极低

### 获取用户软记忆

```http
GET /api/secondme/user/softmemory?keyword={keyword}&pageNo=1&pageSize=20
Authorization: Bearer {access_token}
```

**权限**: `user.info.softmemory`

**查询参数**:
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| keyword | string | 否 | 搜索关键词 |
| pageNo | integer | 否 | 页码 (默认: 1) |
| pageSize | integer | 否 | 每页大小 (默认: 20, 最大: 100) |

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "list": [
      {
        "id": 456,
        "factObject": "兴趣爱好",
        "factContent": "喜欢阅读科幻小说",
        "createTime": 1705315800000,
        "updateTime": 1705315800000
      }
    ],
    "total": 100
  }
}
```

### 添加笔记/记忆

```http
POST /api/secondme/note/add
Authorization: Bearer {access_token}
Content-Type: application/json
```

**权限**: `note.add`

**请求参数**:
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| content | string | 条件 | 笔记内容 (TEXT类型必填，最大50000字符) |
| title | string | 否 | 笔记标题 (最大200字符) |
| urls | string[] | 条件 | URL列表 (LINK类型必填，最多10个) |
| memoryType | string | 否 | 笔记类型: TEXT(默认)或LINK |

**请求示例 - 文本笔记**:
```json
{
  "content": "今天学习了新的医学研究方法",
  "title": "学习笔记",
  "memoryType": "TEXT"
}
```

**请求示例 - 链接笔记**:
```json
{
  "urls": ["https://example.com/article"],
  "title": "收藏文章",
  "memoryType": "LINK"
}
```

## 错误码

| 错误码 | 说明 |
|--------|------|
| `oauth2.scope.insufficient` | 缺少所需权限 |
| `oauth2.token.invalid` | Token 无效或过期 |
| `oauth2.code.invalid` | 授权码无效或已使用 |
| `user.not_found` | 用户不存在 |

## MedRoundTable 集成示例

### 登录流程

```typescript
// 1. 用户点击登录
// 2. 后端生成 state 并存储到 cookie
// 3. 重定向到 Second Me 授权页面
// 4. 用户授权后返回 callback
// 5. 用 code 换 token
// 6. 获取用户信息并保存到数据库
// 7. 设置 session，跳转
```

### 获取用户完整档案

```typescript
async function getFullUserProfile(accessToken: string) {
  // 获取基本信息
  const userInfo = await fetch('https://api.mindverse.com/gate/lab/api/secondme/user/info', {
    headers: { 'Authorization': `Bearer ${accessToken}` }
  })
  
  // 获取兴趣标签
  const userShades = await fetch('https://api.mindverse.com/gate/lab/api/secondme/user/shades', {
    headers: { 'Authorization': `Bearer ${accessToken}` }
  })
  
  // 获取软记忆
  const userMemory = await fetch('https://api.mindverse.com/gate/lab/api/secondme/user/softmemory?pageNo=1&pageSize=20', {
    headers: { 'Authorization': `Bearer ${accessToken}` }
  })
  
  return {
    info: await userInfo.json(),
    shades: await userShades.json(),
    memory: await userMemory.json()
  }
}
```

### 同步用户研究兴趣

```typescript
// 将用户的兴趣标签同步到 MedRoundTable
async function syncUserInterests(userId: string, accessToken: string) {
  const response = await fetch('https://api.mindverse.com/gate/lab/api/secondme/user/shades', {
    headers: { 'Authorization': `Bearer ${accessToken}` }
  })
  
  const result = await response.json()
  
  if (result.code === 0) {
    const interests = result.data.shades
      .filter((s: any) => s.hasPublicContent)
      .map((s: any) => ({
        name: s.shadeName,
        description: s.shadeDescription,
        confidence: s.confidenceLevel
      }))
    
    // 保存到 MedRoundTable 数据库
    await db.userInterests.createMany({
      data: interests.map((i: any) => ({
        userId,
        ...i
      }))
    })
  }
}
```

## 环境变量配置

```bash
# Second Me OAuth
SECONDME_CLIENT_ID=your_client_id
SECONDME_CLIENT_SECRET=your_client_secret
SECONDME_REDIRECT_URI=http://localhost:3000/api/auth/callback

# API Base URL
SECONDME_API_BASE=https://api.mindverse.com/gate/lab
```

## 注意事项

1. **Token 有效期**: Access Token 有过期时间，需要使用 Refresh Token 刷新
2. **权限申请**: 需要用户的授权才能访问相应数据
3. **数据隐私**: 只获取用户公开的数据 (`hasPublicContent: true`)
4. **Rate Limiting**: 注意 API 调用频率限制
5. **错误处理**: 所有 API 返回 `code` 字段，0 表示成功，非 0 表示错误

## 相关链接

- 官方文档: https://develop-docs.second.me/zh/docs/api-reference/secondme
- Second Me 平台: https://app.secondme.io
- MedRoundTable 项目: https://github.com/MoKangMedical/medroundtable
