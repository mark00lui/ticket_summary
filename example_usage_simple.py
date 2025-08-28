"""
簡化版使用範例
不依賴 MCP 和 pandas，直接使用瀏覽器自動化和簡化版報告生成器
"""

import logging
from browser_automation import BrowserAutomation
from report_generator_simple import SimpleReportGenerator
import config

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def simple_usage_example():
    """簡化版使用範例"""
    
    # 建立瀏覽器自動化實例
    browser = BrowserAutomation()
    report_gen = SimpleReportGenerator()
    
    try:
        print("🎯 週報自動生成工具 - 簡化版")
        print("=" * 50)
        
        # 1. 啟動瀏覽器
        print("步驟 1: 啟動 Chrome 瀏覽器...")
        browser.setup_driver()
        print("✓ Chrome 瀏覽器已啟動")
        
        # 2. 登入 eService
        print("\n步驟 2: 登入 eService...")
        eservice_username = input("請輸入 eService 帳號: ").strip()
        eservice_password = input("請輸入 eService 密碼: ").strip()
        
        eservice_success = browser.login_to_website(
            config.ESERVICE_CONFIG,
            eservice_username,
            eservice_password
        )
        
        if eservice_success:
            print("✓ eService 登入成功")
            
            # 3. 抓取 eService 活動
            print("\n步驟 3: 抓取 eService 活動...")
            eservice_activities = browser.fetch_activities(config.ESERVICE_CONFIG, 7)
            report_gen.add_activities(eservice_activities)
            print(f"✓ 抓取到 {len(eservice_activities)} 個 eService 活動")
        else:
            print("❌ eService 登入失敗")
        
        # 4. 登入 Jira
        print("\n步驟 4: 登入 Jira...")
        jira_username = input("請輸入 Jira 帳號: ").strip()
        jira_password = input("請輸入 Jira 密碼: ").strip()
        
        jira_success = browser.login_to_website(
            config.JIRA_CONFIG,
            jira_username,
            jira_password
        )
        
        if jira_success:
            print("✓ Jira 登入成功")
            
            # 5. 抓取 Jira 活動
            print("\n步驟 5: 抓取 Jira 活動...")
            jira_activities = browser.fetch_activities(config.JIRA_CONFIG, 7)
            report_gen.add_activities(jira_activities)
            print(f"✓ 抓取到 {len(jira_activities)} 個 Jira 活動")
        else:
            print("❌ Jira 登入失敗")
        
        # 6. 分類活動
        print("\n步驟 6: 分類活動...")
        categorized = report_gen.categorize_activities()
        for category, activities in categorized.items():
            if activities:
                print(f"  - {category}: {len(activities)} 個活動")
        
        # 7. 生成報告
        print("\n步驟 7: 生成報告...")
        report_gen.generate_report_data()
        
        # 生成 HTML 報告
        html_path = report_gen.generate_html_report()
        print(f"✓ HTML 報告已生成: {html_path}")
        
        # 生成 CSV 報告
        csv_path = report_gen.generate_csv_report()
        print(f"✓ CSV 報告已生成: {csv_path}")
        
        # 生成 Markdown 報告
        md_path = report_gen.generate_markdown_report()
        print(f"✓ Markdown 報告已生成: {md_path}")
        
        print("\n🎉 週報生成完成！")
        print("您可以在 reports/ 目錄中找到生成的報告檔案。")
        
    except Exception as e:
        print(f"❌ 執行過程中發生錯誤: {e}")
        logger.error(f"錯誤詳情: {e}")
    
    finally:
        # 關閉瀏覽器
        print("\n關閉瀏覽器...")
        browser.close_driver()
        print("✓ 瀏覽器已關閉")

def test_mode():
    """測試模式 - 使用模擬資料"""
    
    print("🧪 測試模式 - 使用模擬資料")
    print("=" * 50)
    
    # 建立報告生成器
    report_gen = SimpleReportGenerator()
    
    # 建立模擬活動資料
    from datetime import datetime, timedelta
    
    test_activities = [
        {
            'date': datetime.now() - timedelta(days=1),
            'title': '客戶支援 - 系統登入問題',
            'content': '協助客戶解決登入系統時遇到的問題，提供技術支援',
            'status': '已解決',
            'source': 'eservice'
        },
        {
            'date': datetime.now() - timedelta(days=2),
            'title': 'Bug 修復 - 報表顯示異常',
            'content': '修復報表頁面顯示異常的問題，更新相關程式碼',
            'status': '進行中',
            'source': 'jira'
        },
        {
            'date': datetime.now() - timedelta(days=3),
            'title': '功能開發 - 新增匯出功能',
            'content': '為系統新增 Excel 匯出功能，提升使用者體驗',
            'status': '已完成',
            'source': 'jira'
        },
        {
            'date': datetime.now() - timedelta(days=4),
            'title': '會議討論 - 專案進度檢討',
            'content': '參與專案進度檢討會議，討論下階段開發計畫',
            'status': '已完成',
            'source': 'eservice'
        },
        {
            'date': datetime.now() - timedelta(days=5),
            'title': '文件撰寫 - API 文件更新',
            'content': '更新系統 API 文件，新增最新功能的說明',
            'status': '已完成',
            'source': 'jira'
        }
    ]
    
    try:
        # 添加活動
        report_gen.add_activities(test_activities)
        print(f"✓ 已添加 {len(test_activities)} 個模擬活動")
        
        # 分類活動
        categorized = report_gen.categorize_activities()
        print("\n活動分類結果:")
        for category, activities in categorized.items():
            if activities:
                print(f"  - {category}: {len(activities)} 個活動")
        
        # 生成報告
        print("\n生成報告...")
        report_gen.generate_report_data()
        
        # 生成各種格式的報告
        html_path = report_gen.generate_html_report()
        csv_path = report_gen.generate_csv_report()
        md_path = report_gen.generate_markdown_report()
        
        print(f"✓ HTML 報告: {html_path}")
        print(f"✓ CSV 報告: {csv_path}")
        print(f"✓ Markdown 報告: {md_path}")
        
        print("\n🎉 測試完成！請檢查 reports/ 目錄中的報告檔案。")
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")
        logger.error(f"錯誤詳情: {e}")

def main():
    """主函數"""
    print("週報自動生成工具 - 簡化版")
    print("=" * 50)
    print("選擇使用模式:")
    print("1. 完整模式 - 實際登入網站並抓取資料")
    print("2. 測試模式 - 使用模擬資料生成報告")
    print("3. 退出")
    
    while True:
        choice = input("\n請選擇 (1-3): ").strip()
        
        if choice == "1":
            simple_usage_example()
            break
        elif choice == "2":
            test_mode()
            break
        elif choice == "3":
            print("👋 再見！")
            break
        else:
            print("❌ 無效選擇，請重新輸入")

if __name__ == "__main__":
    main()
