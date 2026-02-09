#!/bin/bash
# deploy.sh - web_project目录一键部署脚本

set -e

echo "🚀 开始部署企业项目管理系统..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否为root用户
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}请不要使用root用户运行此脚本${NC}"
    exit 1
fi

# 检查操作系统
if ! grep -q Ubuntu /etc/os-release; then
    echo -e "${RED}此脚本仅支持Ubuntu系统${NC}"
    exit 1
fi

echo -e "${GREEN}1. 更新系统包...${NC}"
sudo apt update && sudo apt upgrade -y

echo -e "${GREEN}2. 安装Docker和Docker Compose...${NC}"
sudo apt install docker.io docker-compose -y
sudo usermod -aG docker $USER

echo -e "${GREEN}3. 启动Docker服务...${NC}"
sudo systemctl start docker
sudo systemctl enable docker

echo -e "${GREEN}4. 检查项目文件结构...${NC}"

# 检查当前目录是否正确
echo "当前目录: $(pwd)"
echo "目录内容:"
ls -la

# 检查docker-compose.yml
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}未找到docker-compose.yml文件${NC}"
    echo "请确保在web_project目录运行此脚本"
    exit 1
fi

# 检查前端目录
if [ ! -d "frontend" ]; then
    echo -e "${RED}未找到frontend目录${NC}"
    echo "请确保frontend目录在当前目录下"
    exit 1
fi

# 检查后端目录
if [ ! -d "backend" ]; then
    echo -e "${RED}未找到backend目录${NC}"
    echo "请确保backend目录在当前目录下"
    exit 1
fi

echo -e "${GREEN}5. 配置环境变量...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}未找到.env文件，使用默认配置${NC}"
    # 生成随机密码
    SECRET_KEY=$(openssl rand -base64 32)
    
    cat > .env << EOF
DATABASE_URL=postgresql://yjydb:Jlbk@2025@cd-postgres-2p7vnsx4.sql.tencentcdb.com:25331/project_cost_tracking
SECRET_KEY=$SECRET_KEY
API_PORT=8000
API_HOST=0.0.0.0
FRONTEND_PORT=80
ENVIRONMENT=production
DEBUG=false
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=15
DB_POOL_TIMEOUT=20
DB_POOL_RECYCLE=1800
EOF
    echo -e "${YELLOW}已生成默认环境配置文件${NC}"
fi

echo -e "${GREEN}6. 创建Nginx配置目录...${NC}"
mkdir -p nginx/ssl

# 创建nginx配置文件
cat > nginx/nginx.conf << EOF
server {
    listen 80;
    server_name _;

    # 前端静态文件
    location / {
        root /usr/share/nginx/html;
        try_files \$uri \$uri/ /index.html;
        
        # 启用gzip压缩
        gzip on;
        gzip_vary on;
        gzip_min_length 1024;
        gzip_proxied any;
        gzip_comp_level 6;
        gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    }

    # API代理到后端
    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

echo -e "${GREEN}7. 构建和启动服务...${NC}"
docker-compose down --remove-orphans
docker-compose build --no-cache
docker-compose up -d

echo -e "${GREEN}8. 等待服务启动...${NC}"
sleep 20

# 检查服务状态
echo -e "${GREEN}9. 检查服务状态...${NC}"
docker-compose ps

# 检查端口
echo -e "${GREEN}10. 检查端口占用...${NC}"
netstat -tlnp | grep -E ':80|:8000|:443'

echo -e "${GREEN}✅ 部署完成！${NC}"
echo ""
echo "📊 服务访问地址："
echo "   前端页面: http://$(curl -s ifconfig.me):80"
echo "   后端API:  http://$(curl -s ifconfig.me):8000"
echo "   API文档:  http://$(curl -s ifconfig.me):8000/docs"
echo ""
echo "🔧 常用命令："
echo "   查看日志: docker-compose logs -f"
echo "   重启服务: docker-compose restart"
echo "   停止服务: docker-compose down"
echo "   更新服务: docker-compose pull && docker-compose up -d"
echo ""
echo -e "${YELLOW}⚠️  重要提醒：${NC}"
echo "   1. 请确保安全组已开放80、8000、443端口"
echo "   2. 生产环境请修改.env文件中的默认密码"
echo "   3. 建议配置域名和SSL证书"
echo ""
echo -e "${GREEN}🎉 部署成功！请访问上述地址测试系统${NC}"