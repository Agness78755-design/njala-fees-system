#!/bin/bash

# ════════════════════════════════════════════════════════════════════════════
# DATABASE MANAGEMENT SCRIPT
# Backup, restore, and manage PostgreSQL database
# ════════════════════════════════════════════════════════════════════════════

set -e

# Configuration
DB_NAME="${1:-njala_fees}"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
BACKUP_DIR="./backups"
LOG_FILE="./logs/db_backup.log"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# ── Backup Functions ──

backup_database() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$BACKUP_DIR/${DB_NAME}_${timestamp}.sql.gz"
    
    print_info "Starting database backup..."
    log "Backup started: $backup_file"
    
    if PGPASSWORD=$DB_PASSWORD pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -v | gzip > "$backup_file"; then
        
        local file_size=$(du -h "$backup_file" | cut -f1)
        print_success "Database backed up successfully"
        log "Backup completed: $backup_file (Size: $file_size)"
        
        echo "Backup file: $backup_file"
    else
        print_error "Backup failed"
        log "Backup failed"
        exit 1
    fi
}

# ── Restore Functions ──

restore_database() {
    local backup_file="$1"
    
    if [ ! -f "$backup_file" ]; then
        print_error "Backup file not found: $backup_file"
        exit 1
    fi
    
    print_info "Starting database restore from: $backup_file"
    log "Restore started from: $backup_file"
    
    # Verify backup file integrity
    if ! gzip -t "$backup_file" 2>/dev/null; then
        print_error "Backup file is corrupted"
        log "Backup file is corrupted: $backup_file"
        exit 1
    fi
    
    # Confirm restore
    read -p "⚠️  This will overwrite the database. Continue? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        print_info "Restore cancelled"
        exit 0
    fi
    
    # Drop and recreate database
    print_info "Dropping existing database..."
    PGPASSWORD=$DB_PASSWORD psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -c "DROP DATABASE IF EXISTS $DB_NAME;" || true
    
    print_info "Creating new database..."
    PGPASSWORD=$DB_PASSWORD psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -c "CREATE DATABASE $DB_NAME;"
    
    # Restore from backup
    print_info "Restoring data..."
    if gunzip -c "$backup_file" | PGPASSWORD=$DB_PASSWORD psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -v > /dev/null 2>&1; then
        
        print_success "Database restored successfully"
        log "Restore completed from: $backup_file"
    else
        print_error "Restore failed"
        log "Restore failed from: $backup_file"
        exit 1
    fi
}

# ── Cleanup Functions ──

cleanup_old_backups() {
    local days="${1:-30}"
    
    print_info "Removing backups older than $days days..."
    log "Cleanup: Removing backups older than $days days"
    
    find "$BACKUP_DIR" -name "${DB_NAME}_*.sql.gz" -mtime +$days -delete
    
    local remaining=$(ls -1 "$BACKUP_DIR"/${DB_NAME}_*.sql.gz 2>/dev/null | wc -l)
    print_success "Cleanup completed. Remaining backups: $remaining"
    log "Cleanup completed. Remaining backups: $remaining"
}

# ── Verification Functions ──

verify_backup() {
    local backup_file="$1"
    
    if [ ! -f "$backup_file" ]; then
        print_error "Backup file not found: $backup_file"
        return 1
    fi
    
    print_info "Verifying backup file..."
    
    if gzip -t "$backup_file" 2>/dev/null; then
        print_success "Backup file is valid"
        
        local file_size=$(du -h "$backup_file" | cut -f1)
        local file_date=$(stat -f %Sm -t %Y-%m-%d\ %H:%M:%S "$backup_file" 2>/dev/null || stat -c %y "$backup_file" | cut -d' ' -f1-2)
        
        echo "  File: $backup_file"
        echo "  Size: $file_size"
        echo "  Date: $file_date"
        return 0
    else
        print_error "Backup file is corrupted"
        return 1
    fi
}

# ── List Functions ──

list_backups() {
    echo "Available backups:"
    echo ""
    
    if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -1 "$BACKUP_DIR"/${DB_NAME}_*.sql.gz 2>/dev/null)" ]; then
        print_info "No backups found"
        return
    fi
    
    ls -lh "$BACKUP_DIR"/${DB_NAME}_*.sql.gz | awk '{print "  " $9 " (" $5 ")"}'
}

# ── Database Statistics ──

show_stats() {
    print_info "Database Statistics:"
    
    PGPASSWORD=$DB_PASSWORD psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -c "
        SELECT 
            schemaname,
            COUNT(*) as table_count,
            SUM(n_live_tup) as total_rows
        FROM pg_stat_user_tables
        GROUP BY schemaname;
        "
}

# ── Main Menu ──

show_usage() {
    cat << EOF
Database Management Tool for Njala Fees System

Usage: $0 [COMMAND] [OPTIONS]

Commands:
    backup              Create a database backup
    restore [FILE]      Restore from a backup file
    list                List available backups
    verify [FILE]       Verify a backup file
    cleanup [DAYS]      Remove old backups (default: 30 days)
    stats               Show database statistics
    help                Show this help message

Environment Variables:
    DB_NAME             Database name (default: njala_fees)
    DB_USER             Database user (default: postgres)
    DB_HOST             Database host (default: localhost)
    DB_PORT             Database port (default: 5432)
    DB_PASSWORD         Database password (required for backup/restore)

Examples:
    $0 backup
    $0 restore backups/njala_fees_20250101_120000.sql.gz
    $0 list
    $0 verify backups/njala_fees_20250101_120000.sql.gz
    $0 cleanup 60
    $0 stats

EOF
}

# ── Main ──

case "${1:-help}" in
    backup)
        backup_database
        ;;
    restore)
        if [ -z "$2" ]; then
            print_error "Please specify backup file to restore"
            echo "Usage: $0 restore [BACKUP_FILE]"
            exit 1
        fi
        restore_database "$2"
        ;;
    list)
        list_backups
        ;;
    verify)
        if [ -z "$2" ]; then
            print_error "Please specify backup file to verify"
            exit 1
        fi
        verify_backup "$2"
        ;;
    cleanup)
        cleanup_old_backups "${2:-30}"
        ;;
    stats)
        show_stats
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac
