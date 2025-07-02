# # Dockerfile

# FROM python:3.11-slim
# # 用 pytorch/pytorch:latest作为基础镜像
# #FROM pytorch/pytorch:latest

# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1

# WORKDIR /app

# # ---> 新增：安装 mysqlclient 可能需要的系统依赖 (Debian/Ubuntu 示例) <---
# RUN apt-get update && apt-get install -y gcc default-libmysqlclient-dev pkg-config && rm -rf /var/lib/apt/lists/*
# # ---> 其他系统可能需要不同的包名 <---

# # 安装 Python 依赖
# RUN pip install --upgrade pip
# COPY requirements.txt /app/
# # RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt


# # 复制项目代码
# COPY . /app/

# 使用 Python 官方精简镜像
FROM python:3.11-slim

# 环境变量配置
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 设置工作目录
WORKDIR /app

# 设置清华 Debian 软件源，加速系统依赖安装
RUN echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm main contrib non-free non-free-firmware\n\
deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm-updates main contrib non-free non-free-firmware\n\
deb https://mirrors.tuna.tsinghua.edu.cn/debian-security bookworm-security main contrib non-free non-free-firmware" \
> /etc/apt/sources.list

# 安装构建 mysqlclient 等 Python 包所需的系统依赖
RUN apt-get update && \
    apt-get install -y gcc default-libmysqlclient-dev pkg-config && \
    rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
RUN pip install --upgrade pip
COPY requirements.txt /app/
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 复制项目代码
COPY . /app/

