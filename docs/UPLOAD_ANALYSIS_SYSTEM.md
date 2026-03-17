# MedRoundTable - 研究方案与数据库上传分析系统

## 系统概述

实现研究方案文档和数据库文件的上传、存储、管理和分析功能。支持调用外部API进行数据分析。

## 核心功能

### 1. 研究方案管理
- 上传研究方案文档（PDF、Word、Markdown）
- 方案版本控制
- 方案审核状态追踪
- 方案与圆桌会关联

### 2. 数据库管理
- 上传数据库文件（CSV、Excel、SQLite、JSON）
- 数据库元数据管理
- 数据预览和 schema 查看
- 数据质量检查

### 3. 数据分析能力
- 调用外部API进行分析
- 本地基础统计分析
- 生成分析报告
- 可视化图表生成

## 数据库设计

```sql
-- 研究方案表
CREATE TABLE research_protocols (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    file_path VARCHAR(500),
    file_type VARCHAR(50),
    file_size BIGINT,
    version INTEGER DEFAULT 1,
    status VARCHAR(50) DEFAULT 'draft', -- draft, submitted, approved, rejected
    uploaded_by VARCHAR(100),
    roundtable_id VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON
);

-- 数据库文件表
CREATE TABLE research_databases (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    file_path VARCHAR(500),
    file_type VARCHAR(50), -- csv, xlsx, sqlite, json
    file_size BIGINT,
    schema JSON, -- 存储表结构
    row_count INTEGER,
    column_count INTEGER,
    uploaded_by VARCHAR(100),
    roundtable_id VARCHAR(36),
    protocol_id VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON
);

-- 数据分析任务表
CREATE TABLE analysis_tasks (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    database_id VARCHAR(36),
    analysis_type VARCHAR(50), -- descriptive, comparative, correlation, regression
    status VARCHAR(50) DEFAULT 'pending', -- pending, running, completed, failed
    config JSON, -- 分析配置
    result JSON, -- 分析结果
    error_message TEXT,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- 分析API调用日志表
CREATE TABLE api_call_logs (
    id VARCHAR(36) PRIMARY KEY,
    task_id VARCHAR(36),
    api_name VARCHAR(100),
    endpoint VARCHAR(255),
    request_data JSON,
    response_data JSON,
    status_code INTEGER,
    duration_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API 设计

### 研究方案 API

```python
# POST /api/protocols/upload
# 上传研究方案
{
    "file": "multipart/form-data",
    "title": "研究方案标题",
    "description": "方案描述",
    "roundtable_id": "关联的圆桌会ID"
}

# Response
{
    "id": "protocol_uuid",
    "title": "研究方案标题",
    "file_path": "/uploads/protocols/xxx.pdf",
    "status": "uploaded",
    "created_at": "2026-03-18T03:24:00Z"
}

# GET /api/protocols/{protocol_id}
# 获取研究方案详情

# GET /api/protocols
# 获取研究方案列表
# Query: roundtable_id, status, page, limit

# PUT /api/protocols/{protocol_id}
# 更新研究方案信息

# DELETE /api/protocols/{protocol_id}
# 删除研究方案

# POST /api/protocols/{protocol_id}/analyze
# AI分析研究方案
# Response: 分析结果（研究设计、终点指标、统计方法建议等）
```

### 数据库 API

```python
# POST /api/databases/upload
# 上传数据库文件
{
    "file": "multipart/form-data",
    "name": "数据库名称",
    "description": "数据库描述",
    "protocol_id": "关联的研究方案ID",
    "roundtable_id": "关联的圆桌会ID"
}

# Response
{
    "id": "db_uuid",
    "name": "数据库名称",
    "file_path": "/uploads/databases/xxx.csv",
    "schema": {
        "columns": [
            {"name": "patient_id", "type": "integer"},
            {"name": "age", "type": "integer"},
            {"name": "gender", "type": "string"}
        ]
    },
    "row_count": 1000,
    "column_count": 15,
    "created_at": "2026-03-18T03:24:00Z"
}

# GET /api/databases/{database_id}
# 获取数据库详情（包含schema预览）

# GET /api/databases/{database_id}/preview
# 获取数据预览（前100行）

# GET /api/databases/{database_id}/schema
# 获取数据库schema详情

# POST /api/databases/{database_id}/analyze
# 执行数据分析
{
    "analysis_type": "descriptive",
    "columns": ["age", "gender", "bmi"],
    "config": {
        "include_missing": true,
        "generate_charts": true
    }
}

# Response
{
    "task_id": "task_uuid",
    "status": "running",
    "estimated_duration": 30
}

# GET /api/analysis-tasks/{task_id}
# 获取分析任务状态和结果

# POST /api/databases/{database_id}/query
# SQL查询接口
{
    "sql": "SELECT * FROM data WHERE age > 50 LIMIT 100",
    "params": {}
}
```

### 外部API调用

```python
# POST /api/analysis/external
# 调用外部API进行分析
{
    "database_id": "db_uuid",
    "api_provider": "nhanes_analyzer",
    "endpoint": "/analyze",
    "parameters": {
        "variables": ["weight", "height", "bmi"],
        "analysis_type": "correlation"
    }
}

# Response
{
    "task_id": "task_uuid",
    "status": "running",
    "external_job_id": "job_123"
}

# 支持的API提供商
# - nhanes_analyzer: NHANES数据分析
# - seer_analyzer: SEER肿瘤数据分析
# - medivisual: 医学数据可视化
# - clawbio: ClawBio生物信息学分析
```

## 前端界面

### 1. 研究方案上传页面
- 拖拽上传区域
- 方案信息表单
- 版本历史展示
- AI分析按钮

### 2. 数据库上传页面
- 拖拽上传区域
- 数据预览表格
- Schema展示
- 数据质量报告

### 3. 数据分析页面
- 选择数据源
- 选择分析方法
- 配置分析参数
- 查看分析结果
- 下载报告

## 技术实现

### 后端实现文件结构

```
backend/
├── main.py                      # 主入口
├── routers/
│   ├── protocols.py            # 研究方案API
│   ├── databases.py            # 数据库API
│   └── analysis.py             # 数据分析API
├── services/
│   ├── protocol_service.py     # 研究方案服务
│   ├── database_service.py     # 数据库服务
│   ├── analysis_service.py     # 数据分析服务
│   └── external_api_service.py # 外部API调用服务
├── models/
│   ├── protocol.py             # 研究方案模型
│   ├── database.py             # 数据库模型
│   └── analysis.py             # 分析任务模型
├── utils/
│   ├── file_handler.py         # 文件处理工具
│   ├── data_parser.py          # 数据解析工具
│   └── api_client.py           # API客户端
└── database.py                 # 数据库连接
```

### 外部API配置

```python
# config/external_apis.yaml
external_apis:
  nhanes_analyzer:
    base_url: "https://nhanesanalyz-8bn77uby.manus.space/api"
    api_key: "${NHANES_API_KEY}"
    endpoints:
      analyze: "/analyze"
      visualize: "/visualize"
  
  seer_analyzer:
    base_url: "https://seertotoponcology.vip/api"
    api_key: "${SEER_API_KEY}"
    endpoints:
      survival: "/survival-analysis"
      incidence: "/incidence-analysis"
  
  medivisual:
    base_url: "https://medivisual.org/api"
    api_key: "${MEDIVISUAL_API_KEY}"
    endpoints:
      chart: "/generate-chart"
      dashboard: "/create-dashboard"
  
  clawbio:
    base_url: "https://api.clawbio.com"
    api_key: "${CLAWBIO_API_KEY}"
    endpoints:
      pharmgx: "/pharmgx-analyze"
      gwas: "/gwas-analyze"
      scrna: "/scrna-analyze"
```

## 数据流

```
┌─────────────────────────────────────────────────────────────┐
│                         用户操作                             │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
   ┌────────────┐  ┌────────────┐  ┌────────────┐
   │ 上传研究方案 │  │ 上传数据库  │  │ 执行分析   │
   └─────┬──────┘  └─────┬──────┘  └─────┬──────┘
         │               │               │
         ▼               ▼               ▼
   ┌────────────┐  ┌────────────┐  ┌────────────┐
   │ 文件存储   │  │ 数据解析   │  │ 任务队列   │
   │ (本地/S3) │  │ Schema提取 │  │            │
   └─────┬──────┘  └─────┬──────┘  └─────┬──────┘
         │               │               │
         │               ▼               ▼
         │        ┌────────────┐  ┌────────────┐
         │        │ SQLite DB  │  │ 分析引擎   │
         │        │ 数据存储   │  │ (本地/API) │
         │        └─────┬──────┘  └─────┬──────┘
         │               │               │
         └───────────────┼───────────────┘
                         ▼
                 ┌────────────┐
                 │ 分析结果   │
                 │ 报告生成   │
                 └────────────┘
```

## 安全考虑

1. **文件上传安全**
   - 文件类型白名单
   - 文件大小限制
   - 病毒扫描
   - 存储隔离

2. **数据安全**
   - 敏感数据脱敏
   - 数据访问控制
   - 传输加密
   - 审计日志

3. **API安全**
   - 认证授权
   - 限流控制
   - 输入验证
   - 错误处理

## 下一步实现计划

1. **Phase 1**: 基础上传功能
   - 研究方案上传API
   - 数据库上传API
   - 基础文件存储

2. **Phase 2**: 数据管理
   - 数据库schema解析
   - 数据预览功能
   - 基础SQL查询

3. **Phase 3**: 分析能力
   - 本地基础统计分析
   - 外部API集成
   - 分析报告生成

4. **Phase 4**: 前端界面
   - 上传页面
   - 数据管理页面
   - 分析配置页面
   - 结果展示页面
