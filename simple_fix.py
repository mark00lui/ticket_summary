#!/usr/bin/env python3
"""
簡單的 ChromeDriver 修復工具
專門解決 WinError 193 架構不匹配問題
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    print("🔧 修復 ChromeDriver 架構問題...")
    print()
    
    # 1. 清除 webdriver-manager 快取
    print("步驟 1: 清除 ChromeDriver 快取...")
    cache_path = Path.home() / '.wdm'
    if cache_path.exists():
        try:
            shutil.rmtree(cache_path)
            print("✓ 快取已清除")
        except Exception as e:
            print(f"⚠️  清除快取時發生錯誤: {e}")
    else:
        print("快取不存在")
    
    # 2. 更新 webdriver-manager
    print("\n步驟 2: 更新 webdriver-manager...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "webdriver-manager"])
        print("✓ webdriver-manager 已更新")
    except Exception as e:
        print(f"⚠️  更新失敗: {e}")
    
    # 3. 測試修復
    print("\n步驟 3: 測試修復結果...")
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        
        # 檢查系統架構
        import platform
        system_arch = platform.architecture()[0]
        print(f"系統架構: {system_arch}")
        
        # 明確指定下載 x64 版本的 ChromeDriver
        if system_arch == '64bit':
            print("指定下載 x64 版本的 ChromeDriver...")
            driver_path = ChromeDriverManager(os_type="win64").install()
        else:
            print("指定下載 x32 版本的 ChromeDriver...")
            driver_path = ChromeDriverManager(os_type="win32").install()
            
        print(f"✓ ChromeDriver 已下載: {driver_path}")
        
        # 測試啟動
        service = Service(driver_path)
        options = webdriver.chrome.options.Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(service=service, options=options)
        driver.quit()
        print("✓ ChromeDriver 測試成功")
        
        print("\n" + "=" * 50)
        print("✅ 修復完成！現在可以正常使用專案了。")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        print("\n💡 建議手動解決方案：")
        print("1. 確保 Chrome 瀏覽器已更新到最新版本")
        print("2. 重新啟動電腦")
        print("3. 以系統管理員身份執行")
        print("4. 檢查防毒軟體是否阻擋 ChromeDriver")

if __name__ == "__main__":
    main()
