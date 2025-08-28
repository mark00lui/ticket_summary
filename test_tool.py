"""
測試腳本
驗證週報自動生成工具的基本功能
"""

import os
import sys
import logging
from datetime import datetime, timedelta

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """測試模組匯入"""
    try:
        import config
        from browser_automation import BrowserAutomation
        from report_generator import ReportGenerator
        logger.info("✓ 所有模組匯入成功")
        return True
    except ImportError as e:
        logger.error(f"✗ 模組匯入失敗: {e}")
        return False

def test_config():
    """測試配置檔案"""
    try:
        import config
        
        # 檢查必要配置
        required_configs = ['ESERVICE_CONFIG', 'JIRA_CONFIG', 'REPORT_CONFIG', 'CHROME_CONFIG']
        for config_name in required_configs:
            if not hasattr(config, config_name):
                logger.error(f"✗ 缺少配置: {config_name}")
                return False
        
        logger.info("✓ 配置檔案檢查通過")
        return True
    except Exception as e:
        logger.error(f"✗ 配置檔案檢查失敗: {e}")
        return False

def test_report_generator():
    """測試報告生成器"""
    try:
        from report_generator import ReportGenerator
        
        # 建立報告生成器
        report_gen = ReportGenerator()
        
        # 建立測試資料
        test_activities = [
            {
                'date': datetime.now() - timedelta(days=1),
                'title': '測試活動 1',
                'content': '這是測試活動的內容',
                'status': '進行中',
                'source': 'eservice'
            },
            {
                'date': datetime.now() - timedelta(days=2),
                'title': '測試活動 2',
                'content': '另一個測試活動',
                'status': '已完成',
                'source': 'jira'
            }
        ]
        
        # 添加活動
        report_gen.add_activities(test_activities)
        
        # 分類活動
        categorized = report_gen.categorize_activities()
        
        # 生成報告資料
        report_data = report_gen.generate_report_data()
        
        # 檢查報告資料
        if report_data['total_activities'] == 2:
            logger.info("✓ 報告生成器測試通過")
            return True
        else:
            logger.error(f"✗ 報告資料不正確: {report_data['total_activities']}")
            return False
            
    except Exception as e:
        logger.error(f"✗ 報告生成器測試失敗: {e}")
        return False

def test_browser_automation():
    """測試瀏覽器自動化（不實際啟動瀏覽器）"""
    try:
        from browser_automation import BrowserAutomation
        
        # 建立瀏覽器自動化實例
        browser = BrowserAutomation()
        
        # 測試日期解析
        test_dates = [
            "2024-01-15",
            "2024/01/15",
            "01/15/2024",
            "2024年01月15日"
        ]
        
        for date_str in test_dates:
            parsed_date = browser._parse_date(date_str)
            if not isinstance(parsed_date, datetime):
                logger.error(f"✗ 日期解析失敗: {date_str}")
                return False
        
        logger.info("✓ 瀏覽器自動化基本功能測試通過")
        return True
        
    except Exception as e:
        logger.error(f"✗ 瀏覽器自動化測試失敗: {e}")
        return False

def test_mcp_server():
    """測試 MCP 伺服器（不實際啟動）"""
    try:
        from mcp_server import WeeklyReportMCPServer
        
        # 建立 MCP 伺服器實例
        mcp_server = WeeklyReportMCPServer()
        
        # 檢查工具註冊
        if hasattr(mcp_server, 'server'):
            logger.info("✓ MCP 伺服器測試通過")
            return True
        else:
            logger.error("✗ MCP 伺服器工具註冊失敗")
            return False
            
    except Exception as e:
        logger.error(f"✗ MCP 伺服器測試失敗: {e}")
        return False

def test_dependencies():
    """測試依賴套件"""
    try:
        import selenium
        import pandas
        import jinja2
        import requests
        import beautifulsoup4
        
        logger.info("✓ 所有依賴套件檢查通過")
        return True
    except ImportError as e:
        logger.error(f"✗ 依賴套件檢查失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("週報自動生成工具測試")
    print("=" * 50)
    
    tests = [
        ("依賴套件檢查", test_dependencies),
        ("模組匯入測試", test_imports),
        ("配置檔案測試", test_config),
        ("報告生成器測試", test_report_generator),
        ("瀏覽器自動化測試", test_browser_automation),
        ("MCP 伺服器測試", test_mcp_server),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n執行 {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} 失敗")
    
    print("\n" + "=" * 50)
    print(f"測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過！工具已準備就緒。")
        print("\n下一步:")
        print("1. 編輯 config.py 設定您的網站 URL 和選擇器")
        print("2. 執行 python mcp_server.py 啟動 MCP 伺服器")
        print("3. 或在支援 MCP 的應用程式中連接到此伺服器")
    else:
        print("❌ 部分測試失敗，請檢查錯誤訊息並修正問題。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
