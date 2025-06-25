#!/bin/bash

# 毛孩子AI后端服务 - 快速启动脚本
# FurryKids AI Backend - Quick Start Script

set -e

echo "🐾 毛孩子AI后端服务 - 快速启动"
echo "================================"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "�� 激活虚拟环境..."
source venv/bin/activate

# 检查基础配置
echo "🧪 运行配置检查..."
python3 simple_test.py

if [ $? -ne 0 ]; then
    echo "❌ 配置检查失败，请先修复配置问题"
    exit 1
fi

echo ""
echo "✅ 配置检查通过！"
echo ""

# 安装依赖选项
echo "📋 选择操作:"
echo "1) 安装基础依赖 (fastapi, uvicorn, pymysql, python-dotenv)"
echo "2) 安装完整依赖 (所有requirements.txt中的包)"
echo "3) 跳过依赖安装"
echo "4) 直接启动服务 (假设依赖已安装)"

read -p "请选择 (1-4): " choice

case $choice in
    1)
        echo "📦 安装基础依赖..."
        pip install fastapi uvicorn pymysql python-dotenv sqlalchemy alembic pydantic pydantic-settings
        ;;
    2)
        echo "📦 安装完整依赖..."
        pip install -r requirements-simple.txt
        ;;
    3)
        echo "⏭️  跳过依赖安装"
        ;;
    4)
        echo "🚀 直接启动服务..."
        ;;
    *)
        echo "❌ 无效选择，退出"
        exit 1
        ;;
esac

# 检查OpenRouter API密钥
if grep -q "your-openrouter-api-key-here" .env; then
    echo ""
    echo "⚠️  注意: OpenRouter API密钥未配置"
    echo "   AI功能将无法使用，请在.env文件中设置OPENROUTER_API_KEY"
    echo ""
fi

# 启动选项
echo "🚀 选择启动方式:"
echo "1) 开发模式 (自动重载)"
echo "2) 生产模式"
echo "3) 退出"

read -p "请选择 (1-3): " start_choice

case $start_choice in
    1)
        echo "🔥 启动开发服务器..."
        echo "📍 服务地址: http://localhost:3001"
        echo "📚 API文档: http://localhost:3001/docs"
        echo ""
        uvicorn app.main:app --reload --host 0.0.0.0 --port 3001
        ;;
    2)
        echo "🏭 启动生产服务器..."
        uvicorn app.main:app --host 0.0.0.0 --port 3001
        ;;
    3)
        echo "👋 退出启动脚本"
        exit 0
        ;;
    *)
        echo "❌ 无效选择，退出"
        exit 1
        ;;
esac
