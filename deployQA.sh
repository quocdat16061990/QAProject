#!/bin/bash
set -e

LOG_FILE=~/QAProject/deploy.log
DATE=$(date '+%Y-%m-%d %H:%M:%S')

log() {
    echo "[$DATE] $1" | tee -a $LOG_FILE
}

log "==============================================="
log "🚀 Bắt đầu deployment..."

# Pull code mới nhất
log "📥 Pulling latest code from GitHub..."
cd ~/QAProject
git pull origin main 2>&1 | tee -a $LOG_FILE

# Các bước deploy của bạn
log "🔧 Running deployment steps..."

# Ví dụ
# npm install 2>&1 | tee -a $LOG_FILE
# npm run build 2>&1 | tee -a $LOG_FILE
# pm2 restart app 2>&1 | tee -a $LOG_FILE

log "✅ Deployment hoàn tất!"
log "==============================================="
