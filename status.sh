#!/bin/bash
echo "🚀 MedRoundTable - 服务状态"
echo "=============================="
echo ""

echo "📊 本地服务:"
echo "-------------"
curl -s http://localhost:8000/health && echo " ✅ 后端正常" || echo " ❌ 后端异常"
curl -s http://localhost:3000 | head -1 && echo " ✅ 前端正常" || echo " ❌ 前端异常"

echo ""
echo "🌐 外部访问链接:"
echo "-----------------"

# 获取前端隧道 URL
if [ -f /tmp/cf_web.log ]; then
    WEB_URL=$(grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" /tmp/cf_web.log | tail -1)
    if [ -n "$WEB_URL" ]; then
        echo "前端: $WEB_URL"
    else
        echo "前端: 正在获取..."
    fi
else
    echo "前端: 未启动"
fi

# 获取 API 隧道 URL
if [ -f /tmp/cf_api.log ]; then
    API_URL=$(grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" /tmp/cf_api.log | tail -1)
    if [ -n "$API_URL" ]; then
        echo "API:  $API_URL"
    else
        echo "API:  正在获取..."
    fi
else
    echo "API:  未启动"
fi

echo ""
echo "📈 运行时间:"
echo "-------------"
uptime

echo ""
echo "📝 最近日志:"
echo "-------------"
tail -5 /var/log/medroundtable-monitor.log 2>/dev/null || echo "暂无日志"
