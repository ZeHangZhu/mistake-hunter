#!/usr/bin/env python 
# -*- coding:utf-8 -*-

import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from WebITRTeach import FormulaRecognizer

# 配置
APPID = "bd6d7a3c"
APIKey = "ca854ccd4fa3c72a8ea1b0fbf3afac1c"
Secret = "MTEzNjZlZDZhMTVjYTRiM2NiMmU3YzQz"

def test_ocr():
    print("=== 开始测试 OCR 识别 ===")
    
    # 初始化识别器
    recognizer = FormulaRecognizer(APPID, APIKey, Secret)
    print("识别器初始化完成")
    
    # 测试图片路径
    test_image_path = None
    
    # 检查是否有 media 目录和图片
    media_dir = os.path.join(os.path.dirname(__file__), 'src', 'media')
    if os.path.exists(media_dir):
        print(f"找到 media 目录: {media_dir}")
        # 查找图片文件
        for root, dirs, files in os.walk(media_dir):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    test_image_path = os.path.join(root, file)
                    print(f"找到测试图片: {test_image_path}")
                    break
            if test_image_path:
                break
    
    if not test_image_path:
        print("未找到测试图片，请上传一张图片后再测试")
        return
    
    # 开始识别
    try:
        print(f"\n开始识别图片: {test_image_path}")
        
        # 获取原始响应
        raw_response = recognizer.recognize(test_image_path, return_raw=True)
        print(f"\n原始 API 响应:")
        print(raw_response)
        
        # 获取处理后的结果
        result = recognizer.recognize(test_image_path)
        print(f"\n处理后的识别结果:")
        print(f"'{result}'")
        
    except Exception as e:
        print(f"\n识别出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ocr()
