#!/bin/bash
# MedRoundTable V2.0 快速测试脚本
# 一键测试所有新API

echo "======================================"
echo "🚀 MedRoundTable V2.0 API 测试"
echo "======================================"
echo ""

BASE_URL="http://localhost:8000"

echo "1️⃣ 测试 V2 API 概览..."
echo "--------------------------------------"
curl -s "$BASE_URL/api/v2/" | python3 -m json.tool
echo ""

echo "2️⃣ 查看平台统计..."
echo "--------------------------------------"
curl -s "$BASE_URL/api/v2/stats" | python3 -m json.tool
echo ""

echo "3️⃣ 获取技能分类..."
echo "--------------------------------------"
curl -s "$BASE_URL/api/v2/skills/categories" | python3 -m json.tool
echo ""

echo "4️⃣ 获取技能列表 (前5个)..."
echo "--------------------------------------"
curl -s "$BASE_URL/api/v2/skills/?enabled_only=true" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d[:5], indent=2, ensure_ascii=False))"
echo ""

echo "5️⃣ 搜索 PubMed 相关技能..."
echo "--------------------------------------"
curl -s "$BASE_URL/api/v2/skills/search?q=pubmed" | python3 -m json.tool
echo ""

echo "6️⃣ 获取数据库列表..."
echo "--------------------------------------"
curl -s "$BASE_URL/api/v2/databases/" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'共 {len(d)} 个数据库:'); [print(f'  - {x[\"name\"]} ({x[\"category\"]})') for x in d[:10]]"
echo ""

echo "7️⃣ 高级 PubMed 搜索测试..."
echo "--------------------------------------"
curl -s "$BASE_URL/api/v2/databases/pubmed/advanced?query=diabetes&year_from=2023" | python3 -m json.tool
echo ""

echo "8️⃣ 临床试验设计测试..."
echo "--------------------------------------"
curl -s -X POST "$BASE_URL/api/v2/trials/design" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "糖尿病新药III期试验",
    "disease": "2型糖尿病",
    "intervention": "GLP-1受体激动剂",
    "study_type": "RCT",
    "phase": "PHASE_III",
    "primary_endpoint": "HbA1c较基线变化"
  }' | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'✅ 试验ID: {data[\"trial_id\"]}')
print(f'📋 方案摘要: {data[\"protocol_summary\"][:100]}...')
print(f'🎯 研究设计: {data[\"study_design\"][\"type\"]}')
print(f'📊 样本量: {data[\"statistical_plan\"][\"sample_size\"][\"total\"]}')
print(f'💡 建议数量: {len(data[\"recommendations\"])} 条')
"
echo ""

echo "9️⃣ 患者入排评估测试..."
echo "--------------------------------------"
curl -s -X POST "$BASE_URL/api/v2/trials/eligibility" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_data": {"age": 55, "diagnosis": "糖尿病", "hba1c": 8.5},
    "trial_criteria": {
      "inclusion": ["年龄18-75", "确诊糖尿病", "HbA1c>7.5"],
      "exclusion": ["严重肾功能不全", "怀孕"]
    }
  }' | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'✅ 是否符合: {\"是\" if data[\"eligible\"] else \"否\"}')
print(f'📊 匹配分数: {data[\"score\"]:.1%}')
print(f'📋 匹配标准: {len(data[\"matching_criteria\"])} 项')
print(f'⚠️  排除因素: {len(data[\"exclusion_flags\"])} 项')
"
echo ""

echo "🔟 患者-试验匹配测试..."
echo "--------------------------------------"
curl -s -X POST "$BASE_URL/api/v2/trials/match" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 60,
    "gender": "男",
    "diagnosis": "2型糖尿病",
    "stage": "中度",
    "comorbidities": ["高血压"]
  }' | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'找到 {len(data)} 个匹配试验:')
for trial in data[:3]:
    print(f'  - {trial[\"trial_title\"]} (匹配度: {trial[\"match_score\"]:.0%})')
"
echo ""

echo "======================================"
echo "✅ 所有API测试完成!"
echo "======================================"
echo ""
echo "🌐 Swagger UI: $BASE_URL/docs"
echo "📚 ReDoc:      $BASE_URL/redoc"
echo ""
