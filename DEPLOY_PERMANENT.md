# MedRoundTable 24/7 正式部署架构

```text
GitHub main
    ↓ 发布
腾讯云 Ubuntu / Nginx / FastAPI / relay SQLite
    ↓ HTTPS
https://medroundtable.cn/
    ↕ outbound connector
Windows MedRoundTable Local / DuckDB / Ollama / 科研数据
```

## 运行边界

- 网站、14 Agents、任务状态、聚合结果和论文草稿位于正式云端。
- Windows 负责本地数据读取、DuckDB/Python/R 分析与 Ollama 推理。
- Windows 主动连接 relay；不对公网暴露 `8787`。
- 原始数据行、原始文件和 Ollama 上下文不上传。

## 生产验收门槛

1. `https://medroundtable.cn/` 和观察台返回 200；
2. `/api/health`、`/api/v1/agents`、`/api/v1/relay/health` 返回 200；
3. Windows connector 心跳和轮询持续成功；
4. 合成任务可回传森林图、KM 曲线、基线表、审计记录与论文草稿；
5. 真实数据任务仅返回去标识聚合结果。

详细发布步骤见 [DEPLOYMENT.md](DEPLOYMENT.md)。
