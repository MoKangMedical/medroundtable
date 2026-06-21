#!/bin/bash
# MedRoundTable 24/7 监控脚本

LOG_FILE="/var/log/medroundtable-monitor.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> $LOG_FILE
}

# 检查后端
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    log "后端服务异常，正在重启..."
    pkill -f "python.*backend/main.py" 2>/dev/null
    sleep 2
    cd /root/.openclaw/workspace/medroundtable
    PYTHONPATH="/root/.openclaw/workspace/medroundtable" nohup python3 backend/main.py > /tmp/api_server.log 2>&1 &
    log "后端已重启，PID: $!"
    sleep 3
fi

# 检查前端
if ! curl -s http://localhost:3000 > /dev/null 2>&1; then
    log "前端服务异常，正在重启..."
    pkill -f "http.server 3000" 2>/dev/null
    sleep 2
    cd /root/.openclaw/workspace/medroundtable/frontend
    nohup python3 -m http.server 3000 > /tmp/web_server.log 2>&1 &
    log "前端已重启，PID: $!"
fi

# 检查 Cloudflare 隧道
if ! pgrep -f "cloudflared.*3000" > /dev/null; then
    log "前端隧道异常，正在重启..."
    nohup cloudflared tunnel --url http://localhost:3000 > /tmp/cf_web.log 2>&1 &
    sleep 8
    URL=$(grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" /tmp/cf_web.log | head -1)
    log "前端隧道已重启: $URL"
fi

if ! pgrep -f "cloudflared.*8000" > /dev/null; then
    log "API隧道异常，正在重启..."
    nohup cloudflared tunnel --url http://localhost:8000 > /tmp/cf_api.log 2>&1 &
    sleep 8
    URL=$(grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" /tmp/cf_api.log | head -1)
    log "API隧道已重启: $URL"
fi

log "监控检查完成"
