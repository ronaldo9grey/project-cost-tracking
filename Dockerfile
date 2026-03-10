# 项目成本系统 - 生产环境 Dockerfile
FROM node:22-alpine AS frontend-builder

WORKDIR /app/frontend

# 复制 package 文件
COPY frontend/package*.json ./
RUN npm install

# 复制前端源码并构建
COPY frontend/ .
RUN npm run build

# 后端阶段
FROM python:3.11-slim AS backend

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# 完整阶段（包含前端）
FROM nginx:alpine AS production

# 复制前端构建产物
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html/project

# 复制 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
