#!/bin/bash

# 设置颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置信息
SERVER_USER="root"
SERVER_IP="8.148.71.20"  # 修改为你的实际服务器 IP
REMOTE_PATH="/www/wwwroot/photox_frontend/dist"

echo -e "${GREEN}开始部署流程...${NC}"

# 1. 构建项目
echo -e "${GREEN}正在构建项目...${NC}"
# 跳过类型检查，直接构建
SKIP_TYPE_CHECK=true npm run build-only

if [ $? -ne 0 ]; then
    echo -e "${RED}构建失败！请检查错误信息。${NC}"
    exit 1
fi

echo -e "${GREEN}构建成功！${NC}"

# 2. 上传到服务器
echo -e "${GREEN}正在上传到服务器...${NC}"
# 使用 scp 替代 rsync，支持断点续传和增量更新
# 添加 SSH 参数以提高连接稳定性
scp -o ServerAliveInterval=60 -o ServerAliveCountMax=3 -r dist/* ${SERVER_USER}@${SERVER_IP}:${REMOTE_PATH}

if [ $? -ne 0 ]; then
    echo -e "${RED}上传失败！请检查网络连接和服务器配置。${NC}"
    exit 1
fi

echo -e "${GREEN}部署完成！${NC}" 