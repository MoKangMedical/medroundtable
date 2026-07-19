# Windows Connector 结构化结果契约 1.1

Windows connector 继续使用现有 Token 和 outbound 轮询方式，不开放本地端口。升级后从以下地址拉取任务：

```text
GET https://medroundtable.cn/api/v1/relay/local-jobs/poll?node_id=windows-medroundtable-local
```

任务新增 `research_plan`、`plan_hash`、`plan_signature`、`schema_version` 和 `result_contract`。connector 必须在调用本地分析 API 前执行 `bridge.plan_verifier.assert_executable()`。

## 本地请求组装（必须）

relay 的 `dataset_id` 是任务顶层字段，不能仅把原始 `payload` 直接交给本地 API。Windows connector 在调用 `127.0.0.1:8787` 前必须显式合并数据集 ID：

```python
local_payload = dict(job.get("payload") or {})
local_payload["dataset_id"] = job["dataset_id"]
local_payload.setdefault("dataset", job["dataset_id"])  # 兼容旧本地端点
local_payload.setdefault("question", (job.get("research_plan") or {}).get("question", ""))

response = requests.post(
    f"{local_origin}{job['analysis_path']}",
    json=local_payload,
    timeout=analysis_timeout,
)
```

执行前应在审计日志中记录 `job_id`、`dataset_id`、`analysis_path` 和 payload 的字段名，但不记录原始数据值。若本地 API 返回 `Dataset '' not registered`，说明 connector 仍未将顶层 `dataset_id` 合并到本地请求。

完成本地分析后，使用 `bridge.result_adapter.normalize_result()` 生成聚合结果，并提交：

```text
POST https://medroundtable.cn/api/v1/relay/local-jobs/{job_id}/result
Authorization: Bearer <现有 MRT_CONNECTOR_TOKEN>
```

回传结构必须包含：

- `result.summary`：样本量、纳入记录、变量数、候选关联和证据完整度；
- `result.timeline`：签名校验、本地执行、报告生成等事件；
- `result.agent_notes`：参与复核的 Agent 意见；
- `result.charts.forest`：`label/effect/ci_low/ci_high/p_value`；
- `result.charts.km`：分组曲线点、at-risk 数量和 log-rank P；
- `result.charts.missingness`：变量与缺失率；
- `result.tables.baseline`：columns、rows、footnotes；
- `result.tables.associations`：效应量、置信区间、P 值、FDR 和状态；
- `interpretation`、`review_items`、`paper_draft` 和 `audit_id`。

禁止回传 `raw_data`、`raw_rows`、`file_content`、Ollama prompt/context 和直接身份标识。`result_adapter` 会递归剥离这些字段。

合成验收可运行：

```powershell
cd C:\MedRoundTableLocal
$env:MRT_CONNECTOR_TOKEN="<保持现有 Token>"
$env:MRT_JOB_SIGNING_SECRET=$env:MRT_CONNECTOR_TOKEN
.venv\Scripts\python.exe bridge\synthetic_connector.py
```

正式 connector 可复用同一个 adapter；只需把 `synthetic_result()` 替换为本地 8787 端点的真实聚合响应，再调用 `normalize_result()`。
