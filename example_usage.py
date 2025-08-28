"""
使用範例
展示如何使用週報自動生成工具
"""

import asyncio
import logging
from mcp_server import WeeklyReportMCPServer

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def example_usage():
    """使用範例"""
    
    # 建立 MCP 伺服器實例
    mcp_server = WeeklyReportMCPServer()
    
    try:
        # 1. 設定瀏覽器
        logger.info("步驟 1: 設定瀏覽器")
        result = await mcp_server._setup_browser()
        print(result.content[0].text)
        
        # 2. 登入 eService
        logger.info("步驟 2: 登入 eService")
        eservice_result = await mcp_server._login_eservice({
            "username": "your_eservice_username",
            "password": "your_eservice_password"
        })
        print(eservice_result.content[0].text)
        
        # 3. 登入 Jira
        logger.info("步驟 3: 登入 Jira")
        jira_result = await mcp_server._login_jira({
            "username": "your_jira_username", 
            "password": "your_jira_password"
        })
        print(jira_result.content[0].text)
        
        # 4. 抓取週活動資料
        logger.info("步驟 4: 抓取週活動資料")
        fetch_result = await mcp_server._fetch_weekly_activities({
            "days_back": 7
        })
        print(fetch_result.content[0].text)
        
        # 5. 生成週報
        logger.info("步驟 5: 生成週報")
        report_result = await mcp_server._generate_weekly_report({
            "format": "all"
        })
        print(report_result.content[0].text)
        
        # 6. 關閉瀏覽器
        logger.info("步驟 6: 關閉瀏覽器")
        close_result = await mcp_server._close_browser()
        print(close_result.content[0].text)
        
    except Exception as e:
        logger.error(f"執行過程中發生錯誤: {e}")
    
    finally:
        # 確保瀏覽器被關閉
        if mcp_server.browser_automation:
            await mcp_server._close_browser()

def manual_usage_example():
    """手動使用範例（不使用 MCP）"""
    
    from browser_automation import BrowserAutomation
    from report_generator import ReportGenerator
    import config
    
    # 建立瀏覽器自動化實例
    browser = BrowserAutomation()
    report_gen = ReportGenerator()
    
    try:
        # 1. 啟動瀏覽器
        print("啟動 Chrome 瀏覽器...")
        browser.setup_driver()
        
        # 2. 登入 eService
        print("登入 eService...")
        eservice_success = browser.login_to_website(
            config.ESERVICE_CONFIG,
            "your_eservice_username",
            "your_eservice_password"
        )
        
        if eservice_success:
            print("eService 登入成功")
            
            # 3. 抓取 eService 活動
            print("抓取 eService 活動...")
            eservice_activities = browser.fetch_activities(config.ESERVICE_CONFIG, 7)
            report_gen.add_activities(eservice_activities)
            print(f"抓取到 {len(eservice_activities)} 個 eService 活動")
        
        # 4. 登入 Jira
        print("登入 Jira...")
        jira_success = browser.login_to_website(
            config.JIRA_CONFIG,
            "your_jira_username",
            "your_jira_password"
        )
        
        if jira_success:
            print("Jira 登入成功")
            
            # 5. 抓取 Jira 活動
            print("抓取 Jira 活動...")
            jira_activities = browser.fetch_activities(config.JIRA_CONFIG, 7)
            report_gen.add_activities(jira_activities)
            print(f"抓取到 {len(jira_activities)} 個 Jira 活動")
        
        # 6. 分類活動
        print("分類活動...")
        categorized = report_gen.categorize_activities()
        for category, activities in categorized.items():
            if activities:
                print(f"{category}: {len(activities)} 個活動")
        
        # 7. 生成報告
        print("生成報告...")
        report_gen.generate_report_data()
        
        # 生成 HTML 報告
        html_path = report_gen.generate_html_report()
        print(f"HTML 報告已生成: {html_path}")
        
        # 生成 Excel 報告
        excel_path = report_gen.generate_excel_report()
        print(f"Excel 報告已生成: {excel_path}")
        
        # 生成 Markdown 報告
        md_path = report_gen.generate_markdown_report()
        print(f"Markdown 報告已生成: {md_path}")
        
    except Exception as e:
        print(f"執行過程中發生錯誤: {e}")
    
    finally:
        # 關閉瀏覽器
        browser.close_driver()
        print("瀏覽器已關閉")

if __name__ == "__main__":
    print("週報自動生成工具使用範例")
    print("=" * 50)
    
    # 選擇使用方式
    choice = input("請選擇使用方式 (1: MCP 方式, 2: 手動方式): ")
    
    if choice == "1":
        print("使用 MCP 方式...")
        asyncio.run(example_usage())
    elif choice == "2":
        print("使用手動方式...")
        manual_usage_example()
    else:
        print("無效選擇")
