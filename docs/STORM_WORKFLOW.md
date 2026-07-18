# MedRoundTable STORM 工作流

MedRoundTable 保留原产品名称，并将 STORM 作为“多视角证据研究”工作流接入现有 14 agents、ScientistOne、ARS 和 local-job 链路。

## 四阶段

1. **多视角扫描**：实践者、学者、怀疑者、经济学家、历史学家分别输出核心立场、证据和独有提醒。
2. **矛盾地图**：标记直接冲突、证据强弱、跨视角共识、共同盲点和可消除最大不确定性的关键问题。
3. **研究简报**：生成 60 秒摘要、五项按可靠性排序的发现、隐藏关联、面向用户角色的行动建议和前沿问题。
4. **同行评审**：对每条结论给出置信度、证据类型、最弱环节、遗漏视角和审计状态。

## 页面入口

本地原型入口：`frontend/phase2-comparison.html#storm`。

页面上的“生成签名 local-job”会向：

```text
POST /api/v1/local-jobs/from-research-plan
```

发送包含 `method: STORM`、四阶段产物和研究问题的研究方案。后端成功后，返回 `job_id`、`plan_hash` 与 `plan_signature`，供 relay/Windows connector 继续处理。

## 设计边界

- STORM 负责研究问题、证据综合和审计，不替代统计分析。
- local-job 只接收结构化研究方案，不接收原始文件内容。
- 真实数据运行前仍需完成数据集登记、变量映射和本地执行策略确认。
- 页面中的示例发现是演示模板，必须由实际文献或本地结果替换后才能进入论文草稿。
