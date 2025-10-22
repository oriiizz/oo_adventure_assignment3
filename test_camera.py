#!/usr/bin/env python3
"""测试摄像头访问"""

import cv2
import sys

print("🔍 正在测试摄像头访问...")
print("📹 请在弹出的权限对话框中点击'允许'")
print()

try:
    # 尝试打开摄像头
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ 摄像头打开失败!")
        print()
        print("💡 解决方法:")
        print("1. 打开 系统设置 > 隐私与安全性 > 摄像头")
        print("2. 确保 Python 或 Terminal 有访问权限")
        print("3. 重新运行此脚本")
        sys.exit(1)
    
    print("✅ 摄像头打开成功!")
    print("📸 正在读取画面...")
    
    # 读取一帧
    ret, frame = cap.read()
    
    if ret:
        print(f"✅ 成功读取画面! 分辨率: {frame.shape[1]}x{frame.shape[0]}")
        print()
        print("🎉 摄像头工作正常!")
        print("👉 现在可以运行游戏了: python jump_ball_webcam.py")
    else:
        print("❌ 无法读取摄像头画面")
    
    cap.release()
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()

print()
print("测试完成!")
