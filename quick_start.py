#!/usr/bin/env python3
"""
快速啟動腳本
幫助使用者快速設定和測試週報自動生成工具
"""

import os
import sys
import subprocess
import getpass
from pathlib import Path

def print_banner():
    """顯示歡迎橫幅"""
    print("=" * 60)
    print("🎯 週報自動生成工具 - 快速啟動")
    print("=" * 60)
    print("這個工具可以自動從 eService 和 Jira 抓取活動資料")
    print("並生成結構化的週報。")
    print()

def check_python_version():
    """檢查 Python 版本"""
    if sys.version_info < (3, 8):
        print("❌ 錯誤：需要 Python 3.8 或以上版本")
        print(f"當前版本：{sys.version}")
        return False
    print(f"✓ Python 版本檢查通過：{sys.version.split()[0]}")
    return True

def install_dependencies():
    """安裝依賴套件"""
    print("\n📦 安裝依賴套件...")
    
    # 根據 Python 版本選擇合適的 requirements 檔案
    if sys.version_info >= (3, 13):
        requirements_file = "requirements_python313.txt"
        print("檢測到 Python 3.13+，使用相容版本...")
    else:
        requirements_file = "requirements.txt"
    
    try:
        # 先嘗試安裝基本套件
        basic_packages = [
            "selenium>=4.15.0",
            "webdriver-manager>=4.0.0", 
            "beautifulsoup4>=4.12.0",
            "requests>=2.31.0",
            "python-dateutil>=2.8.0",
            "jinja2>=3.1.0",
            "aiohttp>=3.9.0"
        ]
        
        print("安裝基本套件...")
        for package in basic_packages:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        
        # 嘗試安裝 pandas（可能需要編譯）
        print("安裝 pandas...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas>=2.2.0"])
        except subprocess.CalledProcessError:
            print("⚠️  pandas 安裝失敗，嘗試安裝預編譯版本...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--only-binary=all", "pandas>=2.2.0"])
        
        # 安裝其他套件
        print("安裝其他套件...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl>=3.1.0"])
        
        # 嘗試安裝 MCP（可能不存在）
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp>=1.0.0"])
        except subprocess.CalledProcessError:
            print("⚠️  MCP 套件安裝失敗，可能需要手動安裝")
        
        print("✓ 依賴套件安裝完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 依賴套件安裝失敗：{e}")
        print("\n💡 建議解決方案：")
        print("1. 使用 conda 環境：conda create -n weekly_report python=3.11")
        print("2. 或使用較舊的 Python 版本（3.8-3.11）")
        print("3. 手動安裝套件：pip install selenium webdriver-manager beautifulsoup4 requests pandas jinja2")
        return False

def run_tests():
    """執行測試"""
    print("\n🧪 執行測試...")
    try:
        result = subprocess.run([sys.executable, "test_tool.py"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ 所有測試通過")
            return True
        else:
            print("❌ 測試失敗")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ 執行測試時發生錯誤：{e}")
        return False

def configure_websites():
    """配置網站設定"""
    print("\n⚙️  配置網站設定...")
    
    config_file = Path("config.py")
    if not config_file.exists():
        print("❌ 找不到 config.py 檔案")
        return False
    
    print("請輸入您的網站資訊：")
    
    # eService 配置
    print("\n--- eService 配置 ---")
    eservice_url = input("eService 登入 URL: ").strip()
    if not eservice_url:
        eservice_url = "https://your-eservice-domain.com/login"
    
    # Jira 配置
    print("\n--- Jira 配置 ---")
    jira_url = input("Jira 登入 URL: ").strip()
    if not jira_url:
        jira_url = "https://your-jira-domain.com/login"
    
    # 更新配置檔案
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替換 URL
        content = content.replace(
            '"login_url": "https://your-eservice-domain.com/login"',
            f'"login_url": "{eservice_url}"'
        )
        content = content.replace(
            '"login_url": "https://your-jira-domain.com/login"',
            f'"login_url": "{jira_url}"'
        )
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✓ 網站配置已更新")
        return True
        
    except Exception as e:
        print(f"❌ 更新配置檔案失敗：{e}")
        return False

def create_directories():
    """建立必要目錄"""
    print("\n📁 建立必要目錄...")
    directories = ["reports", "templates", "logs"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ 建立目錄：{directory}")
    
    return True

def show_next_steps():
    """顯示下一步操作"""
    print("\n" + "=" * 60)
    print("🎉 快速設定完成！")
    print("=" * 60)
    print("\n下一步操作：")
    print()
    print("1. 📝 編輯 config.py 檔案，調整網站選擇器")
    print("   - 使用瀏覽器開發者工具找到正確的 CSS 選擇器")
    print("   - 參考 setup_guide.md 中的詳細說明")
    print()
    print("2. 🚀 啟動 MCP 伺服器：")
    print("   python mcp_server.py")
    print()
    print("3. 🔧 在支援 MCP 的應用程式中連接到此伺服器")
    print("   - 伺服器名稱：weekly-report-generator")
    print("   - 可用工具：setup_browser, login_eservice, login_jira, fetch_weekly_activities, generate_weekly_report")
    print()
    print("4. 📚 查看文件：")
    print("   - README.md：基本使用說明")
    print("   - setup_guide.md：詳細設定指南")
    print("   - example_usage.py：使用範例")
    print()
    print("5. 🧪 測試工具：")
    print("   python test_tool.py")
    print()
    print("💡 提示：首次使用時，您需要手動輸入帳號密碼。")
    print("   工具會自動處理後續的登入和資料抓取。")

def main():
    """主函數"""
    print_banner()
    
    # 檢查 Python 版本
    if not check_python_version():
        return False
    
    # 安裝依賴套件
    if not install_dependencies():
        return False
    
    # 建立目錄
    if not create_directories():
        return False
    
    # 配置網站
    if not configure_websites():
        print("⚠️  網站配置跳過，請手動編輯 config.py")
    
    # 執行測試
    if not run_tests():
        print("⚠️  測試失敗，請檢查錯誤訊息")
    
    # 顯示下一步
    show_next_steps()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 快速設定已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 發生未預期的錯誤：{e}")
        sys.exit(1)
