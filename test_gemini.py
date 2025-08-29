"""
Gemini 功能測試工具
用於測試 Gemini API 連接和生成周報功能
"""

import os
import sys
import json
from datetime import datetime

def test_gemini_connection():
    """測試 Gemini 連接"""
    try:
        from gemini_service import GeminiService
        
        # 檢查 API Key
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ 未設定 GEMINI_API_KEY 環境變數")
            print("💡 請設定環境變數: set GEMINI_API_KEY=your_api_key")
            return False
        
        # 初始化服務
        gemini_service = GeminiService(api_key)
        
        # 測試連接
        if gemini_service.test_connection():
            print("✅ Gemini API 連接測試成功")
            return True
        else:
            print("❌ Gemini API 連接測試失敗")
            return False
            
    except ImportError:
        print("❌ 未安裝 google-generativeai 套件")
        print("💡 請執行: pip install google-generativeai")
        return False
    except Exception as e:
        print(f"❌ Gemini 連接測試失敗: {e}")
        return False

def test_gemini_report_generation():
    """測試周報生成功能"""
    try:
        from gemini_service import GeminiService
        
        # 檢查 API Key
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ 未設定 GEMINI_API_KEY 環境變數")
            return False
        
        # 初始化服務
        gemini_service = GeminiService(api_key)
        
        # 檢查測試 JSON 文件是否存在
        test_json_file = "./test/test.json"
        if not os.path.exists(test_json_file):
            print(f"❌ 測試文件不存在: {test_json_file}")
            return False
        
        print(f"📝 使用測試數據文件: {test_json_file}")
        
        # 生成周報
        html_file = gemini_service.generate_weekly_report(test_json_file, "./reports")
        
        if html_file:
            print(f"✅ 測試周報生成成功: {html_file}")
            return True
        else:
            print("❌ 測試周報生成失敗")
            return False
            
    except Exception as e:
        print(f"❌ 測試周報生成失敗: {e}")
        return False

def main():
    """主函數"""
    print("🤖 Gemini 功能測試工具")
    print("="*50)
    
    print("\n1. 測試 Gemini API 連接...")
    if test_gemini_connection():
        print("\n2. 測試周報生成功能...")
        if test_gemini_report_generation():
            print("\n✅ 所有測試通過！")
        else:
            print("\n❌ 周報生成測試失敗")
    else:
        print("\n❌ 連接測試失敗，跳過周報生成測試")

if __name__ == "__main__":
    main()
