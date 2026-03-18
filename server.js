const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');

const app = express();
const PORT = process.env.PORT || 3001;

// 中间件
app.use(cors());
app.use(express.json());
app.use(express.static('public'));
app.use('/uploads', express.static('uploads'));

// 确保上传目录存在
const uploadsDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadsDir)) {
    fs.mkdirSync(uploadsDir, { recursive: true });
}

// 文件上传配置
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        const roundtableDir = path.join(uploadsDir, req.params.roundtableId || 'general');
        if (!fs.existsSync(roundtableDir)) {
            fs.mkdirSync(roundtableDir, { recursive: true });
        }
        cb(null, roundtableDir);
    },
    filename: (req, file, cb) => {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, uniqueSuffix + '-' + file.originalname);
    }
});

const upload = multer({ 
    storage: storage,
    limits: { fileSize: 50 * 1024 * 1024 } // 50MB限制
});

// ===== API 路由 =====

// 健康检查
app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// 文件上传
app.post('/api/upload/:roundtableId', upload.single('file'), (req, res) => {
    if (!req.file) {
        return res.status(400).json({ error: 'No file uploaded' });
    }
    res.json({
        success: true,
        file: {
            name: req.file.originalname,
            size: req.file.size,
            path: req.file.path,
            url: `/uploads/${req.params.roundtableId}/${req.file.filename}`
        }
    });
});

// 获取文件列表
app.get('/api/files/:roundtableId', (req, res) => {
    const roundtableDir = path.join(uploadsDir, req.params.roundtableId);
    if (!fs.existsSync(roundtableDir)) {
        return res.json({ files: [] });
    }
    
    const files = fs.readdirSync(roundtableDir).map(filename => {
        const stats = fs.statSync(path.join(roundtableDir, filename));
        return {
            name: filename.split('-').slice(1).join('-'), // 移除时间戳前缀
            originalName: filename,
            size: (stats.size / 1024).toFixed(1) + ' KB',
            uploadedAt: stats.mtime,
            url: `/uploads/${req.params.roundtableId}/${filename}`
        };
    });
    
    res.json({ files });
});

// 删除文件
app.delete('/api/files/:roundtableId/:filename', (req, res) => {
    const filePath = path.join(uploadsDir, req.params.roundtableId, req.params.filename);
    if (fs.existsSync(filePath)) {
        fs.unlinkSync(filePath);
        res.json({ success: true });
    } else {
        res.status(404).json({ error: 'File not found' });
    }
});

// 数据分析 - Python执行
app.post('/api/analysis/python', (req, res) => {
    const { code, dataFile } = req.body;
    
    // 创建临时Python脚本
    const scriptId = Date.now();
    const scriptPath = path.join(__dirname, 'temp', `analysis_${scriptId}.py`);
    
    const pythonCode = `
import pandas as pd
import numpy as np
import json
import sys

# 读取数据
try:
    df = pd.read_csv('${dataFile}')
    
    # 执行分析
    result = {
        "rows": len(df),
        "columns": len(df.columns),
        "summary": df.describe().to_dict(),
        "columns_info": [{"name": col, "type": str(df[col].dtype)} for col in df.columns]
    }
    
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({"error": str(e)}))
`;
    
    fs.mkdirSync(path.dirname(scriptPath), { recursive: true });
    fs.writeFileSync(scriptPath, pythonCode);
    
    // 执行Python脚本
    exec(`python3 ${scriptPath}`, (error, stdout, stderr) => {
        // 清理临时文件
        fs.unlinkSync(scriptPath);
        
        if (error) {
            return res.status(500).json({ error: error.message, stderr });
        }
        
        try {
            const result = JSON.parse(stdout);
            res.json({ success: true, result });
        } catch (e) {
            res.json({ success: true, output: stdout });
        }
    });
});

// 数据分析 - R执行
app.post('/api/analysis/r', (req, res) => {
    const { code, dataFile } = req.body;
    
    const scriptId = Date.now();
    const scriptPath = path.join(__dirname, 'temp', `analysis_${scriptId}.R`);
    
    const rCode = `
library(jsonlite)
data <- read.csv('${dataFile}')
result <- list(
    rows = nrow(data),
    columns = ncol(data),
    summary = summary(data)
)
cat(toJSON(result))
`;
    
    fs.mkdirSync(path.dirname(scriptPath), { recursive: true });
    fs.writeFileSync(scriptPath, rCode);
    
    exec(`Rscript ${scriptPath}`, (error, stdout, stderr) => {
        fs.unlinkSync(scriptPath);
        
        if (error) {
            return res.status(500).json({ error: error.message, stderr });
        }
        
        res.json({ success: true, output: stdout });
    });
});

// 生成研究方案草稿
app.post('/api/generate-draft', (req, res) => {
    const { title, researchQuestion, studyType } = req.body;
    
    const draft = `# ${title || '研究方案'}

## 1. 研究背景与意义
${researchQuestion || '[待填写]'}

### 1.1 研究背景
[描述研究的临床背景和现状]

### 1.2 研究意义
- 理论意义：
- 实践意义：

## 2. 研究目的
### 2.1 主要目的
${studyType || '[待填写]'}

### 2.2 次要目的
1. 
2. 

## 3. 研究方法
### 3.1 研究设计
- 研究类型：${studyType || '[观察性研究/随机对照试验/队列研究等]'}
- 研究场所：
- 研究时间：

### 3.2 研究对象
#### 纳入标准
1. 年龄18-75岁
2. 符合疾病诊断标准
3. 知情同意

#### 排除标准
1. 合并严重心肝肾疾病
2. 妊娠期或哺乳期女性
3. 无法完成随访

### 3.3 样本量计算
- 计算公式：
- 参数设置：
- 最终样本量：

### 3.4 统计学方法
- 描述性统计：
- 推断性统计：
- 显著性水平：α=0.05

## 4. 研究流程
### 4.1 筛选期 (Day -7 to Day 0)
- 知情同意
- 基线评估

### 4.2 干预期
- 

### 4.3 随访期
- 

## 5. 数据管理
### 5.1 数据采集
- 使用电子数据采集系统(EDC)
- 病例报告表(CRF)

### 5.2 数据质控
- 双录入核查
- 逻辑检查

## 6. 伦理考虑
- 伦理委员会批准
- 知情同意
- 隐私保护

## 7. 预期成果
### 7.1 主要终点

### 7.2 次要终点

## 8. 研究时间表
| 阶段 | 时间 | 任务 |
|------|------|------|
| 准备期 | Month 1-2 | 伦理审批、系统搭建 |
| 入组期 | Month 3-8 | 患者招募、数据采集 |
| 随访期 | Month 9-14 | 完成随访、数据清理 |
| 分析期 | Month 15-16 | 统计分析、论文撰写 |

## 9. 参考文献
[自动生成相关文献]

---
生成时间：${new Date().toLocaleString()}
生成工具：MedRoundTable AI科研协作平台
`;

    res.json({ success: true, draft });
});

// 启动服务器
app.listen(PORT, () => {
    console.log(`MedRoundTable API Server running on port ${PORT}`);
    console.log(`Health check: http://localhost:${PORT}/api/health`);
});

module.exports = app;