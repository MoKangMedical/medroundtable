# MedRoundTable Zeabur 部署按钮

[![Deploy on Zeabur](https://zeabur.com/button.svg)](https://zeabur.com/templates/XXXXXXXX)

## 手动部署步骤

### 1. 访问 Zeabur
打开 https://zeabur.com

### 2. 创建项目
- 点击 "创建项目"
- 选择 "从 GitHub 导入"
- 选择 `MoKangMedical/medroundtable` 仓库

### 3. 配置服务
- **类型**: Python
- **启动命令**: `uvicorn backend.main:app --host 0.0.0.0 --port 8080`
- **端口**: 8080

### 4. 设置环境变量
```
SECRET_KEY=your-random-secret-key-here
DEBUG=false
DATABASE_URL=sqlite:///app/data/medroundtable.db
CORS_ORIGINS=https://medroundtable-v2.vercel.app,https://app.secondme.io
```

### 5. 部署
点击 "部署" 按钮，等待 2-3 分钟

### 6. 绑定域名（可选）
- 在控制台点击 "域名"
- 可以生成免费域名或绑定自己的域名

## 部署后测试

```bash
# 测试健康检查
curl https://your-domain.zeabur.app/health

# 测试 A2A Discovery
curl https://your-domain.zeabur.app/api/a2a/discovery
```

## 更新 Second Me Manifest

获得 Zeabur 域名后，更新 `secondme-manifest.json`：
```json
{
  "interfaces": {
    "api": {
      "base_url": "https://your-domain.zeabur.app"
    }
  }
}
```
