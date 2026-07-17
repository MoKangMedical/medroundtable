# 网站真实数据任务 API

## 页面

`/real-analysis.html` 提供项目创建、状态轮询、脱敏结果摘要和论文草稿承载区。

## 接口合同

```text
POST /api/v1/local-jobs
GET  /api/v1/local-jobs
GET  /api/v1/local-jobs/{job_id}
POST /api/v1/local-jobs/{job_id}/result
POST /api/v1/local-jobs/{job_id}/failed
```

创建请求只允许提交 `title`、`dataset_id`、`analysis_path`、`payload` 和 `requested_by`。生产部署时，创建和结果接口必须接入已认证的 relay 队列；不要把当前的进程内 `_jobs` 存储直接用于多进程生产环境。

结果只能包含聚合值、schema 摘要、报告路径和审计 ID，不得包含原始行、文件内容或 Ollama 上下文。
