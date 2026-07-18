# Windows Connector 结构化结果契约 1.1

Windows connector 继续使用现有 Token 和 outbound 轮询方式，不开放本地端口。升级后从以下地址拉取任务：

```text
GET https://medroundtable.cn/api/v1/relay/local-jobs/poll?node_id=windows-medroundtable-local
```

任务新增 `research_plan`、`plan_hash`、`plan_signature`、`schema_version` 和 `result_contract`。connector 必须在调用本地分析 API 前执行 `bridge.plan_verifier.assert_executable()`。

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
