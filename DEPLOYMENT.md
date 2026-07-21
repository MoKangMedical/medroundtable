# MedRoundTable 正式站部署指南

## 生产环境基线

MedRoundTable 只有一个对外展示入口：

- 正式网站：`https://medroundtable.cn/`
- 分析观察台：`https://medroundtable.cn/real-analysis.html`
- 正式 API：`https://medroundtable.cn/api/v1`
- Windows relay：`https://medroundtable.cn/api/v1/relay`

代码仓库为 `MoKangMedical/medroundtable`，生产运行环境为腾讯云 Ubuntu、Nginx 和 FastAPI。GitHub 不存储 Windows 上的原始科研数据。

## 系统路由

```text
用户浏览器
  → https://medroundtable.cn/
  → Nginx
      ├─ frontend/*.html
      └─ /api/* → FastAPI 127.0.0.1:8010
                         ↓
                    relay SQLite
                         ↕ HTTPS outbound
                    Windows connector
                         ↓
                 127.0.0.1:8787 + Ollama
```

## GitHub 更新

```bash
gh auth status
git status -sb
git add <本次文件>
git commit -m "Describe the production change"
git push origin main
```

禁止在 remote URL、脚本或文档中写入 GitHub Token、connector Token 或 API Key。

## 正式服务器更新

服务器上保留现有 `.env`、relay SQLite 和审计日志，不覆盖密钥与运行数据。

```bash
cd /var/www/medroundtable
git fetch origin main
git pull --ff-only origin main
python3 -m py_compile backend/main.py backend/local_jobs.py backend/relay_router.py
sudo nginx -t
```

按服务器当前的进程托管方式重启 FastAPI，然后执行验收。若日后配置 systemd，应将唯一的重启命令写入服务器运维文档，而不在仓库中硬编码凭据。

## 上线验收

```bash
curl -fsS https://medroundtable.cn/api/health
curl -fsS https://medroundtable.cn/api/v1/agents
curl -fsS https://medroundtable.cn/api/v1/relay/health
curl -fsS 'https://medroundtable.cn/api/v1/local-jobs?limit=1'
curl -fsSI https://medroundtable.cn/real-analysis.html
```

同时确认：

1. 首页存在“打开全流程分析观察台”入口；
2. relay 健康状态为 `ok`；
3. `windows-medroundtable-local` 持续心跳和轮询；
4. 合成任务可完成签名、执行、图表与论文回传；
5. 真实数据任务仅回传聚合结果。

## 回滚

上线前保留被替换文件的时间戳备份。出现故障时仅回滚本次修改的明确文件，不删除 `.env`、`data/local_relay.db` 或 Windows 本地数据。
