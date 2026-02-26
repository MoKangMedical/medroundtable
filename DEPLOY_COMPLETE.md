# 🎉 MedRoundTable 自动部署完成！

## ✅ 部署状态

| 服务 | 地址 | 状态 |
|------|------|------|
| **后端 API** | http://43.134.3.158 | ✅ 已部署 |
| **前端 (Vercel)** | https://medroundtable-v2.vercel.app | ✅ 已上线 |
| **A2A Discovery** | http://43.134.3.158/api/a2a/discovery | ✅ 正常 |

---

## 🚀 已完成配置

### Nginx 反向代理
- 监听端口：80
- 后端转发：127.0.0.1:8001
- 前端目录：/root/.openclaw/workspace/medroundtable/frontend
- CORS：已开启，允许所有来源

### Docker 容器状态
```
medroundtable-api: ✅ 运行中 (8001端口)
```

---

## 🧪 测试连接

### 1. 健康检查
```bash
curl http://43.134.3.158/health
```
预期输出：
```json
{"status":"healthy","timestamp":"2026-02-26T09:48:26.818543"}
```

### 2. A2A Discovery
```bash
curl http://43.134.3.158/api/a2a/discovery
```
预期输出：
```json
{
  "agent_system": "MedRoundTable",
  "version": "1.0.0",
  "agents": [...],
  "endpoints": {...}
}
```

### 3. 浏览器测试
访问：http://43.134.3.158

---

## 🔄 下一步操作

### 1. 更新 Second Me Manifest
编辑 `secondme-manifest.json`：
```json
{
  "interfaces": {
    "api": {
      "base_url": "http://43.134.3.158"
    }
  }
}
```
然后重新上传到 Second Me 平台。

### 2. 更新 Vercel 环境变量
登录 Vercel 控制台，设置：
```bash
NEXT_PUBLIC_API_URL=http://43.134.3.158
```

### 3. 配置 HTTPS（可选）
如果需要 HTTPS，可以：
- 使用 Cloudflare 代理
- 或使用 Sealos/Zeabur 等平台

---

## 📊 服务管理

### 查看状态
```bash
# Nginx 状态
systemctl status nginx

# Docker 容器
docker ps | grep medroundtable

# 测试 API
curl http://localhost/health
```

### 重启服务
```bash
# 重启 Nginx
/usr/sbin/nginx -s reload

# 重启后端
docker restart medroundtable-api
```

### 查看日志
```bash
# Nginx 日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Docker 日志
docker logs medroundtable-api -f
```

---

## 🌐 访问地址

| 用途 | URL |
|------|-----|
| 后端 API | http://43.134.3.158 |
| 健康检查 | http://43.134.3.158/health |
| A2A Discovery | http://43.134.3.158/api/a2a/discovery |
| 前端 (Vercel) | https://medroundtable-v2.vercel.app |

---

## ⚠️ 注意事项

1. **当前是 HTTP**：如需 HTTPS，建议使用 Cloudflare 或迁移到云平台
2. **IP 访问**：当前通过 IP 直接访问，如需域名请配置 DNS
3. **防火墙**：确保服务器防火墙开放 80 端口

---

## 🎉 部署完成！

后端 API 现在已可以通过 `http://43.134.3.158` 访问！

如需 HTTPS 或域名支持，可以：
1. 配置 Cloudflare 代理
2. 购买域名并配置 DNS
3. 迁移到 Zeabur/Sealos 等云平台

**部署成功！** 🚀
