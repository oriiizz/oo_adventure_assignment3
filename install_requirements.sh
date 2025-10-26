#!/bin/bash

echo "🎮 安装摄像头控制游戏所需的库..."
echo ""

# 安装必要的Python包
pip3 install opencv-python mediapipe numpy pygame

echo ""
echo "✅ 安装完成!"
echo ""
echo "运行游戏："
echo "python3 jump_ball_webcam.py"
