#!/usr/bin/env python3
"""
簡化版安裝腳本
專門處理 Python 3.13 相容性問題
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """顯示歡迎橫幅"""
    print("=" * 60)
    print("🎯 週報自動生成工具 - 簡化版安裝")
    print("=" * 60)
    print("專門為 Python 3.13+ 設計的簡化版本")
    print("不依賴 pandas，使用 CSV 格式替代 Excel")
    print()

def check_python_version():
    """檢查 Python 版本"""
    version = sys.version_info
    print(f"Python 版本: {version.major}.{version.minor}.{version.micro}")
    
    if version >= (3, 13):
        print("✓ 檢測到 Python 3.13+，將使用簡化版本")
        return "simple"
    elif version >= (3, 8):
        print("✓ Python 版本相容，可以使用完整版本")
        return "full"
    else:
        print("❌ 需要 Python 3.8 或以上版本")
        return None

def install_basic_packages():
    """安裝基本套件"""
    print("\n📦 安裝基本套件...")
    
    basic_packages = [
        "selenium>=4.15.0",
        "webdriver-manager>=4.0.0",
        "beautifulsoup4>=4.12.0",
        "requests>=2.31.0",
        "jinja2>=3.1.0"
    ]
    
    for package in basic_packages:
        try:
            print(f"安裝 {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package} 安裝成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ {package} 安裝失敗: {e}")
            return False
    
    return True

def try_install_pandas():
    """嘗試安裝 pandas"""
    print("\n📊 嘗試安裝 pandas...")
    
    try:
        # 嘗試安裝最新版本
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas>=2.2.0"])
        print("✓ pandas 安裝成功")
        return True
    except subprocess.CalledProcessError:
        print("⚠️  pandas 安裝失敗，嘗試安裝預編譯版本...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--only-binary=all", "pandas>=2.2.0"])
            print("✓ pandas 預編譯版本安裝成功")
            return True
        except subprocess.CalledProcessError:
            print("❌ pandas 安裝失敗，將使用簡化版本")
            return False

def create_directories():
    """建立必要目錄"""
    print("\n📁 建立必要目錄...")
    directories = ["reports", "templates", "logs"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ 建立目錄：{directory}")
    
    return True

def test_imports():
    """測試套件匯入"""
    print("\n🧪 測試套件匯入...")
    
    test_packages = [
        ("selenium", "selenium"),
        ("webdriver-manager", "webdriver_manager"),
        ("beautifulsoup4", "bs4"),
        ("requests", "requests"),
        ("jinja2", "jinja2")
    ]
    
    failed_packages = []
    
    for package_name, import_name in test_packages:
        try:
            __import__(import_name)
            print(f"✓ {package_name} 匯入成功")
        except ImportError:
            print(f"❌ {package_name} 匯入失敗")
            failed_packages.append(package_name)
    
    # 測試 pandas
    try:
        import pandas
        print("✓ pandas 匯入成功")
        pandas_available = True
    except ImportError:
        print("⚠️  pandas 匯入失敗，將使用簡化版本")
        pandas_available = False
    
    if failed_packages:
        print(f"\n❌ 以下套件匯入失敗: {', '.join(failed_packages)}")
        return False
    
    return True

def show_usage_instructions(python_mode):
    """顯示使用說明"""
    print("\n" + "=" * 60)
    print("🎉 安裝完成！")
    print("=" * 60)
    
    if python_mode == "simple":
        print("\n📋 使用說明（簡化版）：")
        print()
        print("1. 🚀 快速測試：")
        print("   python example_usage_simple.py")
        print("   選擇 '測試模式' 使用模擬資料")
        print()
        print("2. 🔧 實際使用：")
        print("   python example_usage_simple.py")
        print("   選擇 '完整模式' 登入實際網站")
        print()
        print("3. 📝 配置網站：")
        print("   編輯 config.py 設定網站 URL 和選擇器")
        print()
        print("4. 📊 報告格式：")
        print("   - HTML: 美觀的網頁報告")
        print("   - CSV: 表格資料（可用 Excel 開啟）")
        print("   - Markdown: 文字格式報告")
        print()
        print("💡 簡化版特色：")
        print("   - 不依賴 pandas，相容性更好")
        print("   - 使用 CSV 替代 Excel 格式")
        print("   - 支援 Python 3.13+")
        print("   - 功能完整，效能優化")
        
    else:
        print("\n📋 使用說明（完整版）：")
        print()
        print("1. 🚀 啟動 MCP 伺服器：")
        print("   python mcp_server.py")
        print()
        print("2. 🔧 簡化版本：")
        print("   python example_usage_simple.py")
        print()
        print("3. 📝 配置網站：")
        print("   編輯 config.py 設定網站 URL 和選擇器")
        print()
        print("4. 📊 報告格式：")
        print("   - HTML: 美觀的網頁報告")
        print("   - Excel: 完整的試算表報告")
        print("   - Markdown: 文字格式報告")
    
    print("\n📚 更多資訊：")
    print("   - README.md: 詳細使用說明")
    print("   - setup_guide.md: 設定指南")
    print("   - config.py: 網站配置")

def main():
    """主函數"""
    print_banner()
    
    # 檢查 Python 版本
    python_mode = check_python_version()
    if not python_mode:
        return False
    
    # 安裝基本套件
    if not install_basic_packages():
        print("❌ 基本套件安裝失敗")
        return False
    
    # 嘗試安裝 pandas
    pandas_available = try_install_pandas()
    
    # 建立目錄
    if not create_directories():
        print("❌ 目錄建立失敗")
        return False
    
    # 測試匯入
    if not test_imports():
        print("❌ 套件匯入測試失敗")
        return False
    
    # 顯示使用說明
    show_usage_instructions(python_mode)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 安裝已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 發生未預期的錯誤：{e}")
        sys.exit(1)
