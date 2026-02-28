#!/bin/bash

# -*- ENCODING:UTF-8 -*-
echo "========================================="
echo "Mistake-Hunter V1.0.0"
echo "如果是首次执行请使用参数"-r"安装环境依赖"
echo "We recommend using .venv Virtual enviremnet to prevent version conflict"
echo "========================================="

# 检查是否安装 Python
echo "[*]Run Envirment check..."
python --version >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "[E]未检测到 Python，请先安装 Python 并确保已添加到系统环境变量。"
    read -p "按 Enter 键继续..."
    exit 1
fi
echo "[*]Python has installed"

# 如果传入 -r 参数，先安装依赖
if [ "$1" = "-r" ]; then
    echo "[*]The -r parameter has been detected, starting to install dependencies"
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[E]依赖安装失败，请检查 requirements.txt 文件。"
        read -p "按 Enter 键继续..."
        exit 1
    fi
fi

# 启动服务器
echo "[*]Starting Django Server"
cd ./src
python manage.py runserver