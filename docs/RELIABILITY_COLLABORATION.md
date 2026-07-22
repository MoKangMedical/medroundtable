# MedRoundTable 可靠性协作层

## 目标

在 14 Agents 的研究方案转换成 Windows local-job 之前，增加一个可审计的运行时门禁。它不把“多数同意”当成正确，而是同时检查一致度、证据覆盖、置信度离散和少数强反证。

## 路由协议

| 分层 | 典型信号 | 系统动作 | 自动签名 local-job |
|---|---|---|---|
| Easy | 意见一致、证据充足、置信度稳定 | 汇总并做基本验证 | 允许 |
| Medium | 存在少数异议或证据不足 | 多数/少数互提反证，方法学 Agent 仲裁 | 禁止 |
| Hard | 低证据错误共识、少数强反证或置信度剧烈分化 | 盲法独立重分析 + 人工复核 | 禁止 |

## API

- `GET /api/v1/collaboration/protocol`：查看协议版本、拓扑和限制。
- `POST /api/v1/collaboration/assess`：提交 2–14 个结构化专家意见，返回分层、风险旗标、审查路由与下发门禁。
- `POST /api/v1/collaboration/assess-and-dispatch`：对意见先评估再下发。只有 Easy 会返回 `202` 并进入签名 relay 队列；Medium/Hard 返回 `409` 和完整审查路由。

请求的每个意见包含：

```json
{
  "agent_id": "statistics-agent",
  "specialty": "biostatistics",
  "conclusion": "采用预设变量 Cox 基线模型",
  "confidence": 0.78,
  "evidence_items": ["DAG v2", "simulation-report-014"],
  "uncertainties": ["比例风险假设待验证"]
}
```

## 与现有全链路的关系

```text
14 Agents 独立意见
    -> reliability /assess
       -> Easy: 允许研究方案进入签名 local-job
       -> Medium: 冲突仲裁后重新评估
       -> Hard: 独立重分析 + 人工门禁
    -> relay
    -> Windows connector
    -> 本地 DuckDB / Python / R / Ollama
    -> 结果、图表、论文草稿回传正式站
```

## 科学边界

这一实现只借鉴 MMedAgent-RL 的可靠性分层与冲突协作思路，并没有复现论文的强化学习训练、奖励设计或多模态医学基准。返回的“可靠性分层”是工作流路由信号，不是临床准确率，不允许用于自动诊断或治疗决策。

参考：[MMedAgent-RL on arXiv](https://arxiv.org/abs/2506.00555)
