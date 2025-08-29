#!/usr/bin/env python3
"""
測試 ChromeDriver 架構問題
檢查系統架構和 ChromeDriver 是否匹配
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def test_system_architecture():
    """測試系統架構"""
    print("🔍 檢查系統架構...")
    
    # 檢查 Python 架構
    python_arch = platform.architecture()[0]
    print(f"Python 架構: {python_arch}")
    
    # 檢查系統架構
    system_arch = platform.machine()
    print(f"系統架構: {system_arch}")
    
    # 檢查作業系統
    os_name = platform.system()
    os_version = platform.version()
    print(f"作業系統: {os_name} {os_version}")
    
    # 判斷需要的 ChromeDriver 架構
    if python_arch == '64bit':
        required_arch = 'win64'
        print("✅ 需要 win64 版本的 ChromeDriver")
    else:
        required_arch = 'win32'
        print("✅ 需要 win32 版本的 ChromeDriver")
    
    return required_arch

def test_chrome_version():
    """測試 Chrome 版本"""
    print("\n🔍 檢查 Chrome 版本...")
    
    try:
        # 嘗試從註冊表獲取
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
        chrome_version = winreg.QueryValueEx(key, "version")[0]
        winreg.CloseKey(key)
        print(f"Chrome 版本: {chrome_version}")
        return chrome_version
    except:
        print("❌ 無法從註冊表獲取 Chrome 版本")
        
        # 嘗試從執行檔獲取
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ]
        
        for path in chrome_paths:
            if os.path.exists(path):
                try:
                    result = subprocess.run([path, "--version"], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        version_line = result.stdout.strip()
                        chrome_version = version_line.split()[-1]
                        print(f"Chrome 版本: {chrome_version}")
                        return chrome_version
                except:
                    continue
        
        print("❌ 無法檢測 Chrome 版本")
        return None

def test_webdriver_manager():
    """測試 webdriver-manager"""
    print("\n🔍 測試 webdriver-manager...")
    
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        print("✅ webdriver-manager 已安裝")
        
        # 檢查版本
        import webdriver_manager
        print(f"webdriver-manager 版本: {webdriver_manager.__version__}")
        
        return True
    except ImportError:
        print("❌ webdriver-manager 未安裝")
        return False

def test_chromedriver_download():
    """測試 ChromeDriver 下載"""
    print("\n🔍 測試 ChromeDriver 下載...")
    
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        
        # 獲取系統架構
        required_arch = test_system_architecture()
        
        print(f"嘗試下載 {required_arch} 版本的 ChromeDriver...")
        
        # 下載 ChromeDriver
        driver_path = ChromeDriverManager(os_type=required_arch).install()
        print(f"✅ ChromeDriver 已下載: {driver_path}")
        
        # 檢查檔案
        if os.path.exists(driver_path):
            file_size = os.path.getsize(driver_path)
            print(f"檔案大小: {file_size:,} bytes")
            
            if driver_path.endswith('.exe'):
                print("✅ 檔案格式正確")
            else:
                print("⚠️ 檔案格式可能不正確")
        else:
            print("❌ 下載的檔案不存在")
            return False
        
        # 測試啟動
        print("測試 ChromeDriver 啟動...")
        service = Service(driver_path)
        options = webdriver.chrome.options.Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(service=service, options=options)
        driver.quit()
        print("✅ ChromeDriver 測試成功")
        
        return True
        
    except Exception as e:
        print(f"❌ ChromeDriver 測試失敗: {e}")
        return False

def test_selenium():
    """測試 Selenium"""
    print("\n🔍 測試 Selenium...")
    
    try:
        import selenium
        print(f"✅ Selenium 已安裝，版本: {selenium.__version__}")
        return True
    except ImportError:
        print("❌ Selenium 未安裝")
        return False

def check_cache():
    """檢查快取"""
    print("\n🔍 檢查 ChromeDriver 快取...")
    
    cache_path = Path.home() / '.wdm'
    if cache_path.exists():
        print(f"快取目錄存在: {cache_path}")
        
        # 檢查快取內容
        try:
            for item in cache_path.rglob('*'):
                if item.is_file() and item.name == 'chromedriver.exe':
                    file_size = item.stat().st_size
                    print(f"找到 ChromeDriver: {item}")
                    print(f"檔案大小: {file_size:,} bytes")
        except Exception as e:
            print(f"檢查快取時發生錯誤: {e}")
    else:
        print("快取目錄不存在")

def main():
    """主函數"""
    print("=" * 60)
    print("🧪 ChromeDriver 架構測試工具")
    print("=" * 60)
    print()
    
    # 測試系統架構
    required_arch = test_system_architecture()
    
    # 測試 Chrome 版本
    chrome_version = test_chrome_version()
    
    # 測試 Selenium
    selenium_ok = test_selenium()
    
    # 測試 webdriver-manager
    wdm_ok = test_webdriver_manager()
    
    # 檢查快取
    check_cache()
    
    # 測試 ChromeDriver 下載
    if selenium_ok and wdm_ok:
        chromedriver_ok = test_chromedriver_download()
    else:
        chromedriver_ok = False
    
    # 總結
    print("\n" + "=" * 60)
    print("📋 測試總結")
    print("=" * 60)
    
    print(f"系統架構: {required_arch}")
    print(f"Chrome 版本: {chrome_version or '未知'}")
    print(f"Selenium: {'✅ 正常' if selenium_ok else '❌ 異常'}")
    print(f"webdriver-manager: {'✅ 正常' if wdm_ok else '❌ 異常'}")
    print(f"ChromeDriver: {'✅ 正常' if chromedriver_ok else '❌ 異常'}")
    
    if chromedriver_ok:
        print("\n🎉 所有測試通過！ChromeDriver 應該可以正常工作。")
    else:
        print("\n⚠️ 發現問題，建議執行修復：")
        print("python chromedriver_fix.py")

if __name__ == "__main__":
    main()
