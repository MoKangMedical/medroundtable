#!/bin/bash
# 确保 MedRoundTable 服务持续运行

cd /root/.openclaw/workspace/medroundtable

# 检查后端
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "$(date): 后端未运行，正在重启..." >> /var/log/medroundtable-monitor.log
    pkill -f "backend/main.py" 2>/dev/null
    PYTHONPATH="/root/.openclaw/workspace/medroundtable" nohup python3 backend/main.py > /tmp/api_server.log 2>&1 &
    sleep 3
fi

# 检查前端
if ! curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "$(date): 前端未运行，正在重启..." >> /var/log/medroundtable-monitor.log
    pkill -f "http.server 3000" 2>/dev/null
    cd /root/.openclaw/workspace/medroundtable/frontend
    nohup python3 -m http.server 3000 > /tmp/web_server.log 2>&1 &
    sleep 2
fi

# 记录状态
echo "$(date): 服务检查完成" >> /var/log/medroundtable-monitor.log
