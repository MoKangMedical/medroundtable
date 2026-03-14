#!/bin/bash

# =============================================================================
# MedRoundTable 健康监控脚本
# =============================================================================
# 功能：
#   - 定时健康检查
#   - 多维度监控（HTTP状态、响应时间、API功能）
#   - 异常时发送告警（Webhook/邮件/短信）
#   - 自动恢复尝试
#   - 历史记录和报告生成
#
# 使用方法：
#   chmod +x monitor-health.sh
#   ./monitor-health.sh [命令] [选项]
#
# 命令：
#   check      - 执行一次健康检查
#   daemon     - 守护模式，持续监控（默认）
#   report     - 生成健康报告
#   history    - 查看检查历史
#   cron       - 设置定时监控
#
# 示例：
#   ./monitor-health.sh check                    # 单次检查
#   ./monitor-health.sh daemon                   # 持续监控
#   ./monitor-health.sh check -d example.zeabur.app  # 检查指定域名
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 配置
DOMAIN="${DOMAIN:-}"
CHECK_INTERVAL="${CHECK_INTERVAL:-60}"  # 默认每60秒检查一次
TIMEOUT="${TIMEOUT:-10}"  # 请求超时时间
LOG_DIR="${LOG_DIR:-./logs/monitor}"
ALERT_COOLDOWN="${ALERT_COOLDOWN:-300}"  # 告警冷却时间（秒）
MAX_RETRY="${MAX_RETRY:-3}"  # 最大重试次数

# 告警阈值
RESPONSE_TIME_WARNING="${RESPONSE_TIME_WARNING:-1000}"  # 响应时间警告阈值（毫秒）
RESPONSE_TIME_CRITICAL="${RESPONSE_TIME_CRITICAL:-5000}"  # 响应时间严重阈值

# 通知配置
WEBHOOK_URL="${WEBHOOK_URL:-}"
EMAIL_TO="${EMAIL_TO:-}"
SLACK_WEBHOOK="${SLACK_WEBHOOK:-}"

# 状态跟踪
LAST_ALERT_TIME=0
CONSECUTIVE_FAILURES=0
IS_HEALTHY=true

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_header() {
    echo -e "\n${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}\n"
}

# 显示使用帮助
show_help() {
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════╗
║           MedRoundTable 健康监控脚本                                 ║
╚══════════════════════════════════════════════════════════════════════╝

使用方法: ./monitor-health.sh [命令] [选项]

命令:
  check       执行一次健康检查（默认）
  daemon      守护模式，持续监控
  report      生成健康报告
  history     查看检查历史
  status      显示当前状态
  test-alert  测试告警通知
  cron        设置定时监控
  help        显示此帮助信息

选项:
  -d, --domain <域名>      指定要监控的域名
  -i, --interval <秒>      检查间隔（默认: 60秒）
  -t, --timeout <秒>       请求超时（默认: 10秒）
  -l, --log-dir <目录>     日志目录（默认: ./logs/monitor）
  -w, --webhook <URL>      Webhook 通知地址
  -e, --email <地址>       邮件通知地址
  -v, --verbose            显示详细输出

环境变量:
  DOMAIN              监控目标域名
  CHECK_INTERVAL      检查间隔（秒）
  TIMEOUT             请求超时（秒）
  LOG_DIR             日志目录
  WEBHOOK_URL         Webhook 通知地址
  EMAIL_TO            通知邮箱
  SLACK_WEBHOOK       Slack Webhook
  
  # 告警阈值
  RESPONSE_TIME_WARNING    响应时间警告阈值（毫秒，默认: 1000）
  RESPONSE_TIME_CRITICAL   响应时间严重阈值（毫秒，默认: 5000）

示例:
  # 单次检查
  ./monitor-health.sh check
  ./monitor-health.sh check -d medroundtable.zeabur.app

  # 持续监控（守护模式）
  ./monitor-health.sh daemon
  ./monitor-health.sh daemon -i 30 -d example.com

  # 生成报告
  ./monitor-health.sh report

  # 设置每 5 分钟检查一次
  ./monitor-health.sh cron --schedule "*/5 * * * *"

  # 测试告警
  ./monitor-health.sh test-alert

EOF
}

# 获取域名
get_domain() {
    if [ -n "$DOMAIN" ]; then
        echo "$DOMAIN"
    elif [ -f ".zeabur_domain" ]; then
        cat .zeabur_domain
    else
        echo ""
    fi
}

# 记录日志
log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    
    # 确保日志目录存在
    mkdir -p "$LOG_DIR"
    
    # 写入日志文件
    echo "[$timestamp] [$level] $message" >> "$LOG_DIR/monitor.log"
    
    # 同时输出到控制台
    case "$level" in
        INFO)
            print_info "$message"
            ;;
        SUCCESS)
            print_success "$message"
            ;;
        WARNING)
            print_warning "$message"
            ;;
        ERROR)
            print_error "$message"
            ;;
    esac
}

# 发送告警
send_alert() {
    local status="$1"
    local message="$2"
    local details="${3:-}"
    
    local current_time=$(date +%s)
    
    # 检查冷却时间
    if [ $((current_time - LAST_ALERT_TIME)) -lt $ALERT_COOLDOWN ]; then
        log_message "INFO" "告警冷却中，跳过发送"
        return 0
    fi
    
    LAST_ALERT_TIME=$current_time
    
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    local hostname=$(hostname)
    local domain=$(get_domain)
    
    # 构建告警内容
    local title="🚨 MedRoundTable 健康告警"
    if [ "$status" = "RECOVERED" ]; then
        title="✅ MedRoundTable 服务恢复"
    fi
    
    local content="时间: ${timestamp}\n"
    content+="服务器: ${hostname}\n"
    content+="域名: ${domain}\n"
    content+="状态: ${status}\n"
    content+="消息: ${message}\n"
    if [ -n "$details" ]; then
        content+="详情: ${details}"
    fi
    
    log_message "INFO" "发送告警通知..."
    
    # 发送到 Webhook（企业微信/钉钉/飞书）
    if [ -n "$WEBHOOK_URL" ]; then
        local webhook_payload=$(cat <<EOF
{
    "msgtype": "markdown",
    "markdown": {
        "content": "${title}\n${content}"
    }
}
EOF
)
        
        curl -s -X POST "$WEBHOOK_URL" \
            -H "Content-Type: application/json" \
            -d "$webhook_payload" > /dev/null 2>&1 || true
        
        log_message "INFO" "Webhook 通知已发送"
    fi
    
    # 发送到 Slack
    if [ -n "$SLACK_WEBHOOK" ]; then
        local slack_payload=$(cat <<EOF
{
    "text": "${title}",
    "attachments": [
        {
            "color": "$([ "$status" = "RECOVERED" ] && echo "good" || echo "danger")",
            "fields": [
                {"title": "时间", "value": "${timestamp}", "short": true},
                {"title": "域名", "value": "${domain}", "short": true},
                {"title": "状态", "value": "${status}", "short": true},
                {"title": "消息", "value": "${message}", "short": false}
            ]
        }
    ]
}
EOF
)
        
        curl -s -X POST "$SLACK_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "$slack_payload" > /dev/null 2>&1 || true
        
        log_message "INFO" "Slack 通知已发送"
    fi
    
    # 发送到邮件
    if [ -n "$EMAIL_TO" ] && command -v mail &> /dev/null; then
        echo -e "$content" | mail -s "$title" "$EMAIL_TO" || true
        log_message "INFO" "邮件通知已发送"
    fi
}

# HTTP 健康检查
check_http() {
    local domain="$1"
    local url="https://${domain}"
    
    local start_time=$(date +%s%N)
    local http_code
    local response
    
    # 执行请求
    response=$(curl -s -o /dev/null -w "%{http_code},%{time_total}" \
        --max-time "$TIMEOUT" \
        "$url" 2>&1)
    
    local curl_exit=$?
    local end_time=$(date +%s%N)
    
    # 计算响应时间（毫秒）
    local response_time=$(( (end_time - start_time) / 1000000 ))
    
    if [ $curl_exit -ne 0 ]; then
        echo "ERROR,$curl_exit,$response_time"
        return 1
    fi
    
    http_code=$(echo "$response" | cut -d',' -f1)
    
    echo "$http_code,0,$response_time"
}

# 检查 API 端点
check_api() {
    local domain="$1"
    local endpoint="$2"
    local url="https://${domain}${endpoint}"
    
    local response
    response=$(curl -s --max-time "$TIMEOUT" "$url" 2>&1)
    
    if [ $? -eq 0 ] && [ -n "$response" ]; then
        echo "OK"
    else
        echo "FAIL"
    fi
}

# 执行完整健康检查
do_check() {
    local domain=$(get_domain)
    
    if [ -z "$domain" ]; then
        log_message "ERROR" "未指定域名，请使用 -d 参数或设置 DOMAIN 环境变量"
        return 1
    fi
    
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    local has_error=0
    local error_details=""
    
    log_message "INFO" "开始健康检查: $domain"
    
    # 1. HTTP 基础检查
    log_message "INFO" "检查 HTTP 连接..."
    local http_result=$(check_http "$domain")
    local http_code=$(echo "$http_result" | cut -d',' -f1)
    local response_time=$(echo "$http_result" | cut -d',' -f3)
    
    if [ "$http_code" = "ERROR" ]; then
        log_message "ERROR" "HTTP 连接失败 (curl 错误码: $http_code)"
        has_error=1
        error_details="HTTP 连接失败"
    elif [ "$http_code" = "200" ] || [ "$http_code" = "307" ]; then
        log_message "SUCCESS" "HTTP 检查通过 (状态码: $http_code, 响应时间: ${response_time}ms)"
    else
        log_message "WARNING" "HTTP 返回非 200 状态码: $http_code"
        has_error=1
        error_details="HTTP 状态码异常: $http_code"
    fi
    
    # 2. 响应时间检查
    if [ "$response_time" -gt "$RESPONSE_TIME_CRITICAL" ]; then
        log_message "ERROR" "响应时间过长: ${response_time}ms (阈值: ${RESPONSE_TIME_CRITICAL}ms)"
        has_error=1
        error_details="${error_details}; 响应时间过长: ${response_time}ms"
    elif [ "$response_time" -gt "$RESPONSE_TIME_WARNING" ]; then
        log_message "WARNING" "响应时间偏慢: ${response_time}ms (阈值: ${RESPONSE_TIME_WARNING}ms)"
    fi
    
    # 3. 健康检查端点
    log_message "INFO" "检查 /health 端点..."
    local health_result=$(check_api "$domain" "/health")
    if [ "$health_result" = "OK" ]; then
        log_message "SUCCESS" "健康检查端点正常"
    else
        log_message "ERROR" "健康检查端点异常"
        has_error=1
        error_details="${error_details}; /health 端点异常"
    fi
    
    # 4. A2A Discovery
    log_message "INFO" "检查 A2A Discovery..."
    local discovery_result=$(check_api "$domain" "/api/a2a/discovery")
    if [ "$discovery_result" = "OK" ]; then
        log_message "SUCCESS" "A2A Discovery 正常"
    else
        log_message "WARNING" "A2A Discovery 可能异常"
    fi
    
    # 5. Agent 列表
    log_message "INFO" "检查 Agent 列表..."
    local agents_result=$(check_api "$domain" "/api/v1/agents")
    if [ "$agents_result" = "OK" ]; then
        log_message "SUCCESS" "Agent 列表 API 正常"
    else
        log_message "WARNING" "Agent 列表 API 可能异常"
    fi
    
    # 记录检查结果
    local status="HEALTHY"
    if [ $has_error -ne 0 ]; then
        status="UNHEALTHY"
        CONSECUTIVE_FAILURES=$((CONSECUTIVE_FAILURES + 1))
        IS_HEALTHY=false
    else
        CONSECUTIVE_FAILURES=0
        IS_HEALTHY=true
    fi
    
    # 记录到 CSV
    mkdir -p "$LOG_DIR"
    echo "${timestamp},${domain},${status},${http_code},${response_time},${CONSECUTIVE_FAILURES}" >> "$LOG_DIR/checks.csv"
    
    # 发送告警
    if [ $has_error -ne 0 ]; then
        if [ $CONSECUTIVE_FAILURES -ge $MAX_RETRY ]; then
            send_alert "CRITICAL" "服务连续 ${CONSECUTIVE_FAILURES} 次检查失败" "$error_details"
        else
            send_alert "WARNING" "健康检查发现问题" "$error_details"
        fi
    elif [ "$IS_HEALTHY" = "false" ] && [ $has_error -eq 0 ]; then
        # 服务恢复
        send_alert "RECOVERED" "服务已恢复正常"
        IS_HEALTHY=true
        CONSECUTIVE_FAILURES=0
    fi
    
    # 返回结果
    if [ $has_error -eq 0 ]; then
        log_message "SUCCESS" "✅ 健康检查通过"
        return 0
    else
        log_message "ERROR" "❌ 健康检查未通过"
        return 1
    fi
}

# 守护模式
do_daemon() {
    print_header "启动健康监控守护进程"
    
    local domain=$(get_domain)
    if [ -z "$domain" ]; then
        print_error "未指定域名"
        exit 1
    fi
    
    print_info "监控目标: $domain"
    print_info "检查间隔: ${CHECK_INTERVAL} 秒"
    print_info "日志目录: $LOG_DIR"
    print_info "按 Ctrl+C 停止监控"
    
    echo ""
    
    # 主循环
    while true; do
        do_check
        echo "---"
        sleep "$CHECK_INTERVAL"
    done
}

# 生成报告
do_report() {
    print_header "生成健康报告"
    
    local domain=$(get_domain)
    local report_file="$LOG_DIR/report_$(date +%Y%m%d_%H%M%S).txt"
    
    mkdir -p "$LOG_DIR"
    
    {
        echo "======================================"
        echo "  MedRoundTable 健康监控报告"
        echo "======================================"
        echo "生成时间: $(date "+%Y-%m-%d %H:%M:%S")"
        echo "监控目标: ${domain:-未指定}"
        echo ""
        
        if [ -f "$LOG_DIR/checks.csv" ]; then
            echo "检查统计:"
            echo "---------"
            
            local total_checks=$(tail -n +1 "$LOG_DIR/checks.csv" | wc -l)
            local healthy_checks=$(grep ",HEALTHY," "$LOG_DIR/checks.csv" | wc -l)
            local unhealthy_checks=$(grep ",UNHEALTHY," "$LOG_DIR/checks.csv" | wc -l)
            
            echo "总检查次数: $total_checks"
            echo "正常次数: $healthy_checks"
            echo "异常次数: $unhealthy_checks"
            
            if [ $total_checks -gt 0 ]; then
                local uptime=$((healthy_checks * 100 / total_checks))
                echo "可用率: ${uptime}%"
            fi
            
            echo ""
            echo "最近 24 小时检查记录:"
            echo "---------------------"
            tail -50 "$LOG_DIR/checks.csv" | column -t -s',' | head -20
        else
            echo "暂无检查记录"
        fi
        
        echo ""
        echo "======================================"
        
    } | tee "$report_file"
    
    print_success "报告已保存: $report_file"
}

# 查看历史
do_history() {
    print_header "检查历史"
    
    if [ -f "$LOG_DIR/checks.csv" ]; then
        echo -e "${CYAN}时间                域名                    状态      HTTP  响应时间  连续失败${NC}"
        echo "------------------------------------------------------------------------"
        tail -20 "$LOG_DIR/checks.csv" | while IFS=',' read -r timestamp domain status http_code response_time failures; do
            local color="$NC"
            if [ "$status" = "HEALTHY" ]; then
                color="$GREEN"
            else
                color="$RED"
            fi
            printf "${color}%-20s %-24s %-10s %-6s %-10s %-5s${NC}\n" \
                "$timestamp" "$domain" "$status" "$http_code" "${response_time}ms" "$failures"
        done
    else
        print_info "暂无检查记录"
    fi
}

# 显示状态
do_status() {
    print_header "当前监控状态"
    
    local domain=$(get_domain)
    
    echo -e "${CYAN}配置信息:${NC}"
    echo "  监控域名: ${domain:-未设置}"
    echo "  检查间隔: ${CHECK_INTERVAL} 秒"
    echo "  请求超时: ${TIMEOUT} 秒"
    echo "  告警冷却: ${ALERT_COOLDOWN} 秒"
    echo "  响应时间警告阈值: ${RESPONSE_TIME_WARNING}ms"
    echo "  响应时间严重阈值: ${RESPONSE_TIME_CRITICAL}ms"
    
    echo ""
    echo -e "${CYAN}通知配置:${NC}"
    echo "  Webhook: ${WEBHOOK_URL:-未设置}"
    echo "  Slack: ${SLACK_WEBHOOK:-未设置}"
    echo "  Email: ${EMAIL_TO:-未设置}"
    
    echo ""
    echo -e "${CYAN}运行状态:${NC}"
    echo "  当前状态: $([ "$IS_HEALTHY" = "true" ] && echo -e "${GREEN}健康${NC}" || echo -e "${RED}异常${NC}")"
    echo "  连续失败次数: $CONSECUTIVE_FAILURES"
    
    if [ -f "$LOG_DIR/checks.csv" ]; then
        local last_check=$(tail -1 "$LOG_DIR/checks.csv" | cut -d',' -f1)
        echo "  最后检查: $last_check"
    fi
}

# 测试告警
do_test_alert() {
    print_header "测试告警通知"
    
    print_info "发送测试告警..."
    send_alert "TEST" "这是一条测试告警消息" "测试详情：告警系统工作正常"
    
    print_success "测试告警已发送，请检查你的通知渠道"
}

# 设置定时任务
do_cron() {
    local schedule="${1:-*/5 * * * *}"
    
    print_header "设置定时监控"
    
    print_info "监控计划: $schedule"
    
    # 获取脚本绝对路径
    local script_path=$(realpath "$0")
    local domain=$(get_domain)
    
    # 构建 cron 命令
    local cron_cmd="$schedule $script_path check -d $domain >> $LOG_DIR/cron.log 2>&1"
    
    print_info "添加到 crontab..."
    
    # 添加到 crontab
    (crontab -l 2>/dev/null | grep -v "$script_path"; echo "$cron_cmd") | crontab -
    
    print_success "定时任务已设置"
    print_info "查看当前 crontab:"
    crontab -l | grep "monitor-health" || echo "  (未找到)"
}

# 主函数
main() {
    local command="${1:-check}"
    shift || true
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--domain)
                DOMAIN="$2"
                shift 2
                ;;
            -i|--interval)
                CHECK_INTERVAL="$2"
                shift 2
                ;;
            -t|--timeout)
                TIMEOUT="$2"
                shift 2
                ;;
            -l|--log-dir)
                LOG_DIR="$2"
                shift 2
                ;;
            -w|--webhook)
                WEBHOOK_URL="$2"
                shift 2
                ;;
            -e|--email)
                EMAIL_TO="$2"
                shift 2
                ;;
            --schedule)
                CRON_SCHEDULE="$2"
                shift 2
                ;;
            -v|--verbose)
                set -x
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                break
                ;;
        esac
    done
    
    # 切换到项目目录
    cd "$(dirname "$0")/.." || exit 1
    
    case "$command" in
        check)
            do_check
            ;;
        daemon)
            do_daemon
            ;;
        report)
            do_report
            ;;
        history)
            do_history
            ;;
        status)
            do_status
            ;;
        test-alert)
            do_test_alert
            ;;
        cron)
            do_cron "${CRON_SCHEDULE:-*/5 * * * *}"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
