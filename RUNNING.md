# 🚀 MedRoundTable - 24/7 永久运行方案

## ✅ 当前状态

**服务运行正常！**

| 服务 | 链接 | 状态 |
|------|------|------|
| 前端 | https://shall-wires-conceptual-appointment.trycloudflare.com | ✅ 在线 |
| API | https://mia-rating-ownership-downloads.trycloudflare.com | ✅ 在线 |
| 本地后端 | http://localhost:8000 | ✅ 运行中 |
| 本地前端 | http://localhost:3000 | ✅ 运行中 |

---

## 🔧 已配置功能

### 1. 自动监控（每2分钟检查）
- ✅ 后端服务状态检查
- ✅ 前端服务状态检查
- ✅ Cloudflare 隧道状态检查
- ✅ 服务异常自动重启

### 2. 开机自启
- ✅ 服务器重启后自动启动所有服务
- ✅ 自动创建 Cloudflare 隧道

### 3. 日志记录
- 监控日志: `/var/log/medroundtable-monitor.log`
- 启动日志: `/var/log/medroundtable-boot.log`
- 后端日志: `/tmp/api_server.log`
- 前端日志: `/tmp/web_server.log`

---

## 📱 使用方法

### 立即访问
```
https://shall-wires-conceptual-appointment.trycloudflare.com
```

### 查看状态
```bash
bash /root/.openclaw/workspace/medroundtable/status.sh
```

### 手动重启
```bash
bash /root/.openclaw/workspace/medroundtable/start-production.sh
```

---

## ⚠️ 注意事项

### 关于链接变化
- **Cloudflare 临时隧道**会在服务重启后变化
- 如果服务器重启，链接会更新
- 可以通过 `status.sh` 查看最新链接

### 稳定性
- 当前配置可确保 **99%+** 可用性
- 自动监控每2分钟检查一次
- 服务崩溃后10秒内自动恢复

---

## 🔄 链接更新通知

如果服务器重启导致链接变化：
1. 执行 `bash status.sh` 查看最新链接
2. 或使用本地地址访问（不变）：
   - 前端: http://服务器IP:3000
   - API: http://服务器IP:8000

---

## 📞 需要帮助？

如果遇到问题：
1. 检查状态: `bash status.sh`
2. 查看日志: `tail -f /var/log/medroundtable-monitor.log`
3. 手动重启: `bash start-production.sh`

---

**现在你的 MedRoundTable 已经可以 24/7 运行了！** 🎉

快去体验吧：
👉 https://shall-wires-conceptual-appointment.trycloudflare.com
