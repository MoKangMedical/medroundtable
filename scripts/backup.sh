#!/bin/bash
# =============================================================================
# MedRoundTable - 数据库自动备份脚本
# =============================================================================
# 用法: ./scripts/backup.sh [options]
#
# 选项:
#   -h, --help              显示帮助信息
#   -t, --type TYPE         备份类型: auto, manual, scheduled (默认: manual)
#   -d, --destination DIR   备份目标目录 (默认: ./backups)
#   --s3-bucket BUCKET      上传至S3存储桶
#   --s3-region REGION      S3区域 (默认: us-east-1)
#   --retention DAYS        本地备份保留天数 (默认: 30)
#   --encrypt               加密备份文件
#   --notify URL            发送通知到Webhook URL
#   --full                  完整备份（包括文件附件）
#   --database-only         仅备份数据库
#
# 示例:
#   ./scripts/backup.sh                     # 手动备份到默认位置
#   ./scripts/backup.sh --type auto         # 自动备份
#   ./scripts/backup.sh --s3-bucket mybucket # 备份到S3
#   ./scripts/backup.sh --retention 7       # 保留7天
#
# 定时任务示例 (crontab):
#   0 2 * * * /path/to/scripts/backup.sh --type auto --retention 14
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 全局变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_TYPE="manual"
BACKUP_DIR="$PROJECT_ROOT/backups"
S3_BUCKET=""
S3_REGION="us-east-1"
RETENTION_DAYS=30
ENCRYPT=false
NOTIFY_URL=""
FULL_BACKUP=false
DATABASE_ONLY=false
ENCRYPTION_KEY=""
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="medroundtable_${BACKUP_TYPE}_${TIMESTAMP}"
LOG_FILE="$BACKUP_DIR/backup_${TIMESTAMP}.log"

# 数据库配置（从环境变量读取，或使用默认值）
DB_TYPE="${DB_TYPE:-sqlite}"  # sqlite, postgresql, mysql
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-medroundtable}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-}"
DB_PATH="${DB_PATH:-$PROJECT_ROOT/data/medroundtable.db}"

# =============================================================================
# 日志函数
# =============================================================================
log_info() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $1"
    echo -e "${BLUE}${msg}${NC}"
    echo "$msg" >> "$LOG_FILE" 2>/dev/null || true
}

log_success() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] [SUCCESS] $1"
    echo -e "${GREEN}${msg}${NC}"
    echo "$msg" >> "$LOG_FILE" 2>/dev/null || true
}

log_warning() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] [WARNING] $1"
    echo -e "${YELLOW}${msg}${NC}"
    echo "$msg" >> "$LOG_FILE" 2>/dev/null || true
}

log_error() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $1"
    echo -e "${RED}${msg}${NC}"
    echo "$msg" >> "$LOG_FILE" 2>/dev/null || true
}

# =============================================================================
# 错误处理
# =============================================================================
error_exit() {
    log_error "$1"
    send_notification "失败" "$1"
    exit 1
}

trap 'error_exit "备份过程中断"' INT TERM

# =============================================================================
# 解析命令行参数
# =============================================================================
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -t|--type)
                BACKUP_TYPE="$2"
                shift 2
                ;;
            -d|--destination)
                BACKUP_DIR="$2"
                shift 2
                ;;
            --s3-bucket)
                S3_BUCKET="$2"
                shift 2
                ;;
            --s3-region)
                S3_REGION="$2"
                shift 2
                ;;
            --retention)
                RETENTION_DAYS="$2"
                shift 2
                ;;
            --encrypt)
                ENCRYPT=true
                shift
                ;;
            --notify)
                NOTIFY_URL="$2"
                shift 2
                ;;
            --full)
                FULL_BACKUP=true
                shift
                ;;
            --database-only)
                DATABASE_ONLY=true
                shift
                ;;
            *)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

show_help() {
    head -n 25 "$0" | tail -n 23
}

# =============================================================================
# 初始化
# =============================================================================
init() {
    # 创建备份目录
    mkdir -p "$BACKUP_DIR"
    
    # 创建临时目录
    TEMP_DIR=$(mktemp -d)
    trap "rm -rf $TEMP_DIR" EXIT
    
    log_info "=========================================="
    log_info "MedRoundTable 数据库备份"
    log_info "=========================================="
    log_info "备份类型: $BACKUP_TYPE"
    log_info "备份时间: $(date)"
    log_info "备份目录: $BACKUP_DIR"
    log_info "数据库类型: $DB_TYPE"
    
    if [ "$FULL_BACKUP" = true ]; then
        log_info "模式: 完整备份"
    else
        log_info "模式: 仅数据库"
    fi
}

# =============================================================================
# 数据库备份 - SQLite
# =============================================================================
backup_sqlite() {
    log_info "备份SQLite数据库..."
    
    if [ ! -f "$DB_PATH" ]; then
        error_exit "数据库文件不存在: $DB_PATH"
    fi
    
    local backup_file="$TEMP_DIR/database.db"
    
    # 使用SQLite的在线备份功能
    sqlite3 "$DB_PATH" ".backup '$backup_file'"
    
    if [ $? -eq 0 ] && [ -f "$backup_file" ]; then
        log_success "SQLite备份成功: $(du -h "$backup_file" | cut -f1)"
    else
        error_exit "SQLite备份失败"
    fi
    
    # 验证备份完整性
    if sqlite3 "$backup_file" "PRAGMA integrity_check;" | grep -q "ok"; then
        log_success "备份完整性验证通过"
    else
        error_exit "备份完整性验证失败"
    fi
}

# =============================================================================
# 数据库备份 - PostgreSQL
# =============================================================================
backup_postgresql() {
    log_info "备份PostgreSQL数据库..."
    
    local backup_file="$TEMP_DIR/database.sql"
    
    # 检查pg_dump是否可用
    if ! command -v pg_dump &> /dev/null; then
        error_exit "未找到pg_dump命令，请安装PostgreSQL客户端"
    fi
    
    # 执行备份
    PGPASSWORD="$DB_PASSWORD" pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -F custom \
        -f "$backup_file" \
        --verbose 2>> "$LOG_FILE"
    
    if [ $? -eq 0 ] && [ -f "$backup_file" ]; then
        log_success "PostgreSQL备份成功: $(du -h "$backup_file" | cut -f1)"
    else
        error_exit "PostgreSQL备份失败"
    fi
}

# =============================================================================
# 数据库备份 - MySQL
# =============================================================================
backup_mysql() {
    log_info "备份MySQL数据库..."
    
    local backup_file="$TEMP_DIR/database.sql"
    
    # 检查mysqldump是否可用
    if ! command -v mysqldump &> /dev/null; then
        error_exit "未找到mysqldump命令，请安装MySQL客户端"
    fi
    
    # 执行备份
    mysqldump \
        -h "$DB_HOST" \
        -P "$DB_PORT" \
        -u "$DB_USER" \
        -p"$DB_PASSWORD" \
        "$DB_NAME" \
        --single-transaction \
        --routines \
        --triggers \
        > "$backup_file" 2>> "$LOG_FILE"
    
    if [ $? -eq 0 ] && [ -f "$backup_file" ]; then
        log_success "MySQL备份成功: $(du -h "$backup_file" | cut -f1)"
    else
        error_exit "MySQL备份失败"
    fi
}

# =============================================================================
# 备份文件和上传目录
# =============================================================================
backup_files() {
    if [ "$DATABASE_ONLY" = true ]; then
        return
    fi
    
    log_info "备份文件和上传目录..."
    
    local files_backup="$TEMP_DIR/files.tar.gz"
    local dirs_to_backup=""
    
    # 检查并添加需要备份的目录
    [ -d "$PROJECT_ROOT/uploads" ] && dirs_to_backup="$dirs_to_backup uploads"
    [ -d "$PROJECT_ROOT/static" ] && dirs_to_backup="$dirs_to_backup static"
    [ -d "$PROJECT_ROOT/media" ] && dirs_to_backup="$dirs_to_backup media"
    [ -d "$PROJECT_ROOT/data/documents" ] && dirs_to_backup="$dirs_to_backup data/documents"
    
    if [ -z "$dirs_to_backup" ]; then
        log_warning "没有找到需要备份的文件目录"
        return
    fi
    
    # 创建压缩包
    cd "$PROJECT_ROOT"
    tar -czf "$files_backup" $dirs_to_backup 2>> "$LOG_FILE"
    
    if [ $? -eq 0 ] && [ -f "$files_backup" ]; then
        log_success "文件备份成功: $(du -h "$files_backup" | cut -f1)"
    else
        log_warning "文件备份部分失败"
    fi
}

# =============================================================================
# 创建备份元数据
# =============================================================================
create_metadata() {
    log_info "创建备份元数据..."
    
    local metadata_file="$TEMP_DIR/backup_metadata.json"
    
    # 收集系统信息
    local disk_usage=$(df -h "$BACKUP_DIR" | tail -1 | awk '{print $5}')
    local db_size=""
    
    case $DB_TYPE in
        sqlite)
            db_size=$(du -h "$DB_PATH" 2>/dev/null | cut -f1 || echo "unknown")
            ;;
        postgresql)
            db_size=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));" 2>/dev/null | tail -3 | head -1 | xargs || echo "unknown")
            ;;
    esac
    
    cat > "$metadata_file" << EOF
{
    "backup_name": "$BACKUP_NAME",
    "backup_type": "$BACKUP_TYPE",
    "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "version": "1.0",
    "database": {
        "type": "$DB_TYPE",
        "size": "$db_size",
        "path": "$DB_PATH"
    },
    "system": {
        "hostname": "$(hostname)",
        "disk_usage": "$disk_usage",
        "backup_size": "$(du -sh "$TEMP_DIR" 2>/dev/null | cut -f1 || echo 'unknown')"
    },
    "retention_days": $RETENTION_DAYS
}
EOF
    
    log_success "元数据创建完成"
}

# =============================================================================
# 加密备份
# =============================================================================
encrypt_backup() {
    if [ "$ENCRYPT" = false ]; then
        return
    fi
    
    log_info "加密备份文件..."
    
    # 从环境变量或文件获取加密密钥
    if [ -z "$ENCRYPTION_KEY" ]; then
        ENCRYPTION_KEY="${BACKUP_ENCRYPTION_KEY:-}"
    fi
    
    if [ -z "$ENCRYPTION_KEY" ]; then
        log_warning "未设置加密密钥，跳过加密"
        return
    fi
    
    # 加密数据库文件
    if [ -f "$TEMP_DIR/database.db" ]; then
        openssl enc -aes-256-cbc -salt -in "$TEMP_DIR/database.db" \
            -out "$TEMP_DIR/database.db.enc" \
            -k "$ENCRYPTION_KEY" 2>> "$LOG_FILE"
        rm -f "$TEMP_DIR/database.db"
        log_success "数据库文件已加密"
    fi
    
    if [ -f "$TEMP_DIR/database.sql" ]; then
        openssl enc -aes-256-cbc -salt -in "$TEMP_DIR/database.sql" \
            -out "$TEMP_DIR/database.sql.enc" \
            -k "$ENCRYPTION_KEY" 2>> "$LOG_FILE"
        rm -f "$TEMP_DIR/database.sql"
        log_success "数据库文件已加密"
    fi
}

# =============================================================================
# 创建最终备份包
# =============================================================================
package_backup() {
    log_info "创建最终备份包..."
    
    local final_backup="$BACKUP_DIR/${BACKUP_NAME}.tar.gz"
    
    cd "$TEMP_DIR"
    tar -czf "$final_backup" .
    
    if [ $? -eq 0 ] && [ -f "$final_backup" ]; then
        local backup_size=$(du -h "$final_backup" | cut -f1)
        log_success "备份包创建成功: $final_backup ($backup_size)"
        
        # 创建校验和
        sha256sum "$final_backup" > "${final_backup}.sha256"
        log_success "校验和已保存: ${final_backup}.sha256"
    else
        error_exit "备份包创建失败"
    fi
}

# =============================================================================
# 上传到S3
# =============================================================================
upload_to_s3() {
    if [ -z "$S3_BUCKET" ]; then
        return
    fi
    
    log_info "上传备份到S3: $S3_BUCKET"
    
    # 检查AWS CLI
    if ! command -v aws &> /dev/null; then
        log_warning "未找到AWS CLI，跳过S3上传"
        return
    fi
    
    local final_backup="$BACKUP_DIR/${BACKUP_NAME}.tar.gz"
    local s3_key="medroundtable/backups/${BACKUP_NAME}.tar.gz"
    
    aws s3 cp "$final_backup" "s3://$S3_BUCKET/$s3_key" \
        --region "$S3_REGION" 2>> "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        log_success "备份已上传到S3: s3://$S3_BUCKET/$s3_key"
        
        # 上传校验和
        aws s3 cp "${final_backup}.sha256" "s3://$S3_BUCKET/$s3_key.sha256" \
            --region "$S3_REGION" 2>> "$LOG_FILE"
    else
        log_error "S3上传失败"
    fi
}

# =============================================================================
# 清理旧备份
# =============================================================================
cleanup_old_backups() {
    log_info "清理过期备份（保留${RETENTION_DAYS}天）..."
    
    local deleted_count=0
    
    # 清理本地备份
    while IFS= read -r file; do
        log_info "删除过期备份: $file"
        rm -f "$file" "${file}.sha256"
        deleted_count=$((deleted_count + 1))
    done < <(find "$BACKUP_DIR" -name "medroundtable_*.tar.gz" -type f -mtime +$RETENTION_DAYS 2>/dev/null)
    
    if [ $deleted_count -gt 0 ]; then
        log_success "已清理 $deleted_count 个过期备份"
    else
        log_info "没有需要清理的过期备份"
    fi
    
    # 清理日志文件
    find "$BACKUP_DIR" -name "backup_*.log" -type f -mtime +7 -delete 2>/dev/null || true
}

# =============================================================================
# 发送通知
# =============================================================================
send_notification() {
    local status="$1"
    local message="$2"
    
    if [ -z "$NOTIFY_URL" ]; then
        return
    fi
    
    log_info "发送通知..."
    
    local backup_size=""
    local final_backup="$BACKUP_DIR/${BACKUP_NAME}.tar.gz"
    [ -f "$final_backup" ] && backup_size=$(du -h "$final_backup" | cut -f1)
    
    # Slack/Discord格式
    local payload=$(cat <<EOF
{
    "text": "🗄️ MedRoundTable 备份${status}",
    "attachments": [{
        "color": "${status == "成功" && "good" || "danger"}",
        "fields": [
            {"title": "类型", "value": "$BACKUP_TYPE", "short": true},
            {"title": "状态", "value": "$status", "short": true},
            {"title": "大小", "value": "$backup_size", "short": true},
            {"title": "时间", "value": "$(date)", "short": true},
            {"title": "详情", "value": "$message", "short": false}
        ]
    }]
}
EOF
)
    
    curl -s -X POST -H "Content-Type: application/json" \
        -d "$payload" "$NOTIFY_URL" > /dev/null 2>&1 || true
}

# =============================================================================
# 记录备份历史到数据库
# =============================================================================
record_backup_history() {
    log_info "记录备份历史..."
    
    # 这里可以将备份记录写入数据库
    # 用于在管理界面显示备份历史
    
    local final_backup="$BACKUP_DIR/${BACKUP_NAME}.tar.gz"
    local backup_size=$(stat -f%z "$final_backup" 2>/dev/null || stat -c%s "$final_backup" 2>/dev/null || echo "0")
    
    log_info "备份记录:"
    log_info "  - 文件名: ${BACKUP_NAME}.tar.gz"
    log_info "  - 大小: $(du -h "$final_backup" | cut -f1)"
    log_info "  - 位置: $BACKUP_DIR"
    log_info "  - 类型: $BACKUP_TYPE"
}

# =============================================================================
# 主函数
# =============================================================================
main() {
    # 解析参数
    parse_args "$@"
    
    # 初始化
    init
    
    # 执行备份
    case $DB_TYPE in
        sqlite)
            backup_sqlite
            ;;
        postgresql|postgres)
            backup_postgresql
            ;;
        mysql)
            backup_mysql
            ;;
        *)
            error_exit "不支持的数据库类型: $DB_TYPE"
            ;;
    esac
    
    # 备份文件
    backup_files
    
    # 创建元数据
    create_metadata
    
    # 加密（如果需要）
    encrypt_backup
    
    # 打包
    package_backup
    
    # 上传到S3（如果配置了）
    upload_to_s3
    
    # 清理旧备份
    cleanup_old_backups
    
    # 记录历史
    record_backup_history
    
    # 发送通知
    send_notification "成功" "备份已完成"
    
    log_success "=========================================="
    log_success "备份完成!"
    log_success "=========================================="
    log_info "备份文件: $BACKUP_DIR/${BACKUP_NAME}.tar.gz"
    log_info "日志文件: $LOG_FILE"
}

# 执行主函数
main "$@"
