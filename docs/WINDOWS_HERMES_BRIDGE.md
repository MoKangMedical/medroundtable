# Windows Hermes ↔ MedRoundTable Local Bridge

这份文档给 Windows Hermes 使用。目标是让 `https://medroundtable.cn/` 负责圆桌讨论和结果展示，让 Windows 上的 `C:\MedRoundTableLocal` 负责本地数据读取、Ollama 推理和白名单分析。

## 已核对的地址

| 用途 | 地址 |
| --- | --- |
| 正式网站 | `https://medroundtable.cn/` |
| 正式网站 API 根 | `https://medroundtable.cn/api/v1` |
| 正式网站健康检查 | `https://medroundtable.cn/api/health` |
| 正式网站 Agent 列表 | `https://medroundtable.cn/api/v1/agents` |
| 正式网站圆桌列表 | `https://medroundtable.cn/api/v1/roundtables` |
| 本地 MedRoundTable Local | `http://127.0.0.1:8787` |
| 本地健康检查 | `http://127.0.0.1:8787/api/health` |
| 本地分析 | `http://127.0.0.1:8787/api/analyze/hybrid` |

正式网站当前已存在圆桌 API，但尚未提供 Windows 节点任务队列。因此，不能让公网页面直接访问 `E:\` 或把 `8787` 端口暴露到公网；需要先由服务器端 Hermes 增加一个很薄的 relay，再启动 Windows 端 outbound connector。

## MVP 数据边界

Windows 端只回传以下内容：

- 数据集 ID、schema 摘要、行数、缺失率和分析任务状态；
- 经本地分析引擎生成的聚合结果、置信区间、图表或报告文件；
- 错误信息和运行审计 ID。

不回传原始行、原始文件、`E:\` 目录内容、Ollama 私有上下文或 API Key。分析仍然调用现有白名单端点，默认使用 `read-only` 模式。

## 服务器端 relay 合同

在 `https://medroundtable.cn/api/v1` 下增加以下端点：

```text
POST /local-nodes/register
POST /local-nodes/{node_id}/heartbeat
GET  /local-jobs/poll
POST /local-jobs/{job_id}/result
POST /local-jobs/{job_id}/failed
```

所有请求使用短期 connector token；队列中只保存任务规格，不保存原始数据。`/local-jobs/poll` 返回的任务至少包含：

```json
{
  "job_id": "uuid",
  "dataset_id": "gutMGene",
  "analysis_path": "/api/analyze/hybrid",
  "payload": {},
  "requested_by": "roundtable-id"
}
```

Windows connector 将 `payload` 原样交给 `http://127.0.0.1:8787` 的现有端点，再把结果 POST 回 relay。relay 不接受任意路径，只允许登记过的本地分析路径。

## Windows Hermes 预检命令

```powershell
$ErrorActionPreference = "Stop"

$env:MRT_PUBLIC_ORIGIN = "https://medroundtable.cn"
$env:MRT_PUBLIC_API = "$env:MRT_PUBLIC_ORIGIN/api/v1"
$env:MRT_LOCAL_ORIGIN = "http://127.0.0.1:8787"
$env:MRT_LOCAL_DATA_ROOT = "E:\"
$env:MRT_CONNECTOR_ID = "windows-medroundtable-local"
$env:MRT_CONNECTOR_TOKEN = "SET_IN_WINDOWS_SECRET_STORE"

Invoke-RestMethod "$env:MRT_PUBLIC_ORIGIN/api/health"
Invoke-RestMethod "$env:MRT_PUBLIC_API/agents"
Invoke-RestMethod "$env:MRT_LOCAL_ORIGIN/api/health"
Invoke-RestMethod "$env:MRT_LOCAL_ORIGIN/openapi.json" | Out-Null

Write-Host "Public site, public API, and local API are reachable."
```

## 交给 Windows Hermes 的实施任务

```text
在 Windows 上为 MedRoundTable Local 实现 outbound connector：

1. 读取环境变量 MRT_PUBLIC_API、MRT_LOCAL_ORIGIN、MRT_CONNECTOR_ID、MRT_CONNECTOR_TOKEN；不要读取或上传 MRT_LOCAL_DATA_ROOT 下的原始文件。
2. 启动前先检查 GET https://medroundtable.cn/api/health、GET https://medroundtable.cn/api/v1/agents、GET http://127.0.0.1:8787/api/health 和 GET http://127.0.0.1:8787/openapi.json。
3. 若 GET /api/v1/local-jobs/poll 尚不存在，停止 connector，报告“服务器 relay 尚未部署”，不要自行开放 8787 端口。
4. relay 可用后，以 HTTPS 长轮询方式获取任务；只接受 dataset_id、analysis_path、payload 三个字段，并将任务转给本机现有白名单分析端点。
5. 允许的本地路径先限制为 /api/inspect、/api/search、/api/explore/tables、/api/explore/sql、/api/analyze/quick、/api/analyze/auto、/api/analyze/hybrid、/api/export。
6. 仅回传聚合结果、schema 摘要、运行状态、报告路径和审计 ID；不回传原始行、不上传 E:\、不把 Ollama 端口暴露到公网。
7. 给每次运行生成 job_id、started_at、finished_at、dataset_id、analysis_path、status、error 字段，并写入本地审计日志。
8. 用一份合成数据完成端到端测试：网站创建任务 → Windows 本地执行 → 网站显示结果。真实科研数据测试前先停在人工确认点。
```

## Phase 2 前端发布检查

当前 `frontend/phase2-comparison.html` 是静态文件。服务器操作者需要把它放入现有 Nginx `root` 目录，并确认：

```text
https://medroundtable.cn/phase2-comparison.html
```

页面加载后，浏览器再调用 relay API；它不直接调用 Windows 的 `127.0.0.1:8787`。

## Git 与上线关系

GitHub 用于版本留痕和触发部署；它不会自动把本地科研数据上传。发布顺序应是：

1. 提交前清除所有真实 API Key，只保留环境变量占位符；
2. 将前端、后端 relay 和本文件提交到 GitHub；
3. 由正式服务器的部署账号拉取指定 commit 或执行 CI；
4. 在网站上验证静态页面、relay 健康检查和合成数据链路；
5. 最后再开放真实数据集的人工确认测试。
