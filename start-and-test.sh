#!/bin/bash
# MedRoundTable V2.0 - 快速部署启动脚本

echo "======================================"
echo "🚀 MedRoundTable V2.0 启动器"
echo "======================================"
echo ""

# 检查服务状态
echo "📋 检查服务状态..."
PID=$(ps aux | grep "uvicorn.*main:app" | grep -v grep | awk '{print $2}')

if [ -n "$PID" ]; then
    echo "✅ 服务已在运行 (PID: $PID)"
else
    echo "🔄 启动服务..."
    cd /root/.openclaw/workspace/medroundtable
    nohup python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 > /tmp/medroundtable.log 2>&1 &
    sleep 3
    echo "✅ 服务已启动"
fi

echo ""
echo "======================================"
echo "🌐 访问方式"
echo "======================================"
echo ""

echo "方式1: 本地访问 (当前服务器)"
echo "--------------------------------------"
echo "API文档:    http://localhost:8000/docs"
echo "API根地址:  http://localhost:8000/api/v2/"
echo ""

echo "方式2: IP访问 (如果防火墙允许)"
echo "--------------------------------------"
echo "API文档:    http://43.134.3.158:8000/docs"
echo "API根地址:  http://43.134.3.158:8000/api/v2/"
echo ""

echo "方式3: SSH隧道 (推荐用于测试)"
echo "--------------------------------------"
echo "在你的本地机器运行:"
echo "  ssh -L 8000:localhost:8000 root@43.134.3.158"
echo ""
echo "然后访问:"
echo "  http://localhost:8000/docs"
echo ""

echo "======================================"
echo "🧪 快速测试"
echo "======================================"
echo ""

echo "测试1: API状态"
curl -s http://localhost:8000/api/v2/ | python3 -m json.tool 2>/dev/null || echo "服务响应异常"
echo ""

echo "测试2: 平台统计"
curl -s http://localhost:8000/api/v2/stats | python3 -m json.tool 2>/dev/null || echo "服务响应异常"
echo ""

echo "测试3: 技能数量"
SKILL_COUNT=$(curl -s http://localhost:8000/api/v2/stats | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['skills']['total_skills'])" 2>/dev/null)
echo "注册技能数: ${SKILL_COUNT:-未知}"
echo ""

echo "======================================"
echo "📖 文档链接"
echo "======================================"
echo ""
echo "整合报告:    /root/.openclaw/workspace/medroundtable/MEDROUNDTABLE_V2_INTEGRATION_REPORT.md"
echo "迁移指南:    /root/.openclaw/workspace/medroundtable/docs/MIGRATION_TO_CUSTOM_AUTH.md"
echo "部署指南:    /root/.openclaw/workspace/medroundtable/DEPLOYMENT_GUIDE.md"
echo "测试脚本:    /root/.openclaw/workspace/medroundtable/test-v2-api.sh"
echo ""

echo "======================================"
echo "✅ 启动完成!"
echo "======================================"
echo ""
echo "提示: 使用 SSH隧道 是最稳定的测试方式"
echo ""
