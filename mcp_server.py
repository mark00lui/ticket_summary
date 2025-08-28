"""
MCP 伺服器主程式
提供週報自動生成工具給 AI 助手使用
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional
import getpass

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

from browser_automation import BrowserAutomation
from report_generator import ReportGenerator
import config

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeeklyReportMCPServer:
    """週報 MCP 伺服器"""
    
    def __init__(self):
        self.server = Server("weekly-report-generator")
        self.browser_automation = None
        self.report_generator = ReportGenerator()
        self.credentials = {}
        
        # 註冊工具
        self._register_tools()
    
    def _register_tools(self):
        """註冊 MCP 工具"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """列出可用工具"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="login_eservice",
                        description="登入 eService 網站並等待使用者輸入帳號密碼",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "username": {
                                    "type": "string",
                                    "description": "eService 帳號"
                                },
                                "password": {
                                    "type": "string",
                                    "description": "eService 密碼"
                                }
                            },
                            "required": ["username", "password"]
                        }
                    ),
                    Tool(
                        name="login_jira",
                        description="登入 Jira 網站並等待使用者輸入帳號密碼",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "username": {
                                    "type": "string",
                                    "description": "Jira 帳號"
                                },
                                "password": {
                                    "type": "string",
                                    "description": "Jira 密碼"
                                }
                            },
                            "required": ["username", "password"]
                        }
                    ),
                    Tool(
                        name="fetch_weekly_activities",
                        description="抓取過去一週的活動資料",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "days_back": {
                                    "type": "integer",
                                    "description": "要抓取的天數（預設為 7 天）",
                                    "default": 7
                                }
                            }
                        }
                    ),
                    Tool(
                        name="generate_weekly_report",
                        description="生成週報（支援 HTML、Excel、Markdown 格式）",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "format": {
                                    "type": "string",
                                    "description": "報告格式（html、excel、markdown、all）",
                                    "enum": ["html", "excel", "markdown", "all"],
                                    "default": "all"
                                },
                                "output_dir": {
                                    "type": "string",
                                    "description": "輸出目錄（可選）"
                                }
                            }
                        }
                    ),
                    Tool(
                        name="setup_browser",
                        description="設定 Chrome 瀏覽器（首次使用時需要）",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    ),
                    Tool(
                        name="close_browser",
                        description="關閉 Chrome 瀏覽器",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """處理工具呼叫"""
            try:
                if name == "setup_browser":
                    return await self._setup_browser()
                elif name == "login_eservice":
                    return await self._login_eservice(arguments)
                elif name == "login_jira":
                    return await self._login_jira(arguments)
                elif name == "fetch_weekly_activities":
                    return await self._fetch_weekly_activities(arguments)
                elif name == "generate_weekly_report":
                    return await self._generate_weekly_report(arguments)
                elif name == "close_browser":
                    return await self._close_browser()
                else:
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"未知工具: {name}"
                            )
                        ]
                    )
            except Exception as e:
                logger.error(f"工具執行錯誤: {e}")
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"執行工具 {name} 時發生錯誤: {str(e)}"
                        )
                    ]
                )
    
    async def _setup_browser(self) -> CallToolResult:
        """設定瀏覽器"""
        try:
            if not self.browser_automation:
                self.browser_automation = BrowserAutomation()
            
            self.browser_automation.setup_driver()
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="Chrome 瀏覽器已成功啟動，可以開始登入網站。"
                    )
                ]
            )
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"啟動瀏覽器失敗: {str(e)}"
                    )
                ]
            )
    
    async def _login_eservice(self, arguments: Dict[str, Any]) -> CallToolResult:
        """登入 eService"""
        try:
            if not self.browser_automation:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text="請先使用 setup_browser 工具啟動瀏覽器。"
                        )
                    ]
                )
            
            username = arguments.get("username")
            password = arguments.get("password")
            
            if not username or not password:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text="請提供 eService 的帳號和密碼。"
                        )
                    ]
                )
            
            # 儲存憑證
            self.credentials['eservice'] = {'username': username, 'password': password}
            
            # 執行登入
            success = self.browser_automation.login_to_website(
                config.ESERVICE_CONFIG, username, password
            )
            
            if success:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text="eService 登入成功！"
                        )
                    ]
                )
            else:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text="eService 登入失敗，請檢查帳號密碼或網站設定。"
                        )
                    ]
                )
                
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"eService 登入過程中發生錯誤: {str(e)}"
                    )
                ]
            )
    
    async def _login_jira(self, arguments: Dict[str, Any]) -> CallToolResult:
        """登入 Jira"""
        try:
            if not self.browser_automation:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text="請先使用 setup_browser 工具啟動瀏覽器。"
                        )
                    ]
                )
            
            username = arguments.get("username")
            password = arguments.get("password")
            
            if not username or not password:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text="請提供 Jira 的帳號和密碼。"
                        )
                    ]
                )
            
            # 儲存憑證
            self.credentials['jira'] = {'username': username, 'password': password}
            
            # 執行登入
            success = self.browser_automation.login_to_website(
                config.JIRA_CONFIG, username, password
            )
            
            if success:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text="Jira 登入成功！"
                        )
                    ]
                )
            else:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text="Jira 登入失敗，請檢查帳號密碼或網站設定。"
                        )
                    ]
                )
                
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Jira 登入過程中發生錯誤: {str(e)}"
                    )
                ]
            )
    
    async def _fetch_weekly_activities(self, arguments: Dict[str, Any]) -> CallToolResult:
        """抓取週活動資料"""
        try:
            if not self.browser_automation:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text="請先使用 setup_browser 工具啟動瀏覽器並登入網站。"
                        )
                    ]
                )
            
            days_back = arguments.get("days_back", 7)
            
            all_activities = []
            
            # 抓取 eService 活動
            if 'eservice' in self.credentials:
                logger.info("正在抓取 eService 活動...")
                eservice_activities = self.browser_automation.fetch_activities(
                    config.ESERVICE_CONFIG, days_back
                )
                all_activities.extend(eservice_activities)
                logger.info(f"從 eService 抓取到 {len(eservice_activities)} 個活動")
            
            # 抓取 Jira 活動
            if 'jira' in self.credentials:
                logger.info("正在抓取 Jira 活動...")
                jira_activities = self.browser_automation.fetch_activities(
                    config.JIRA_CONFIG, days_back
                )
                all_activities.extend(jira_activities)
                logger.info(f"從 Jira 抓取到 {len(jira_activities)} 個活動")
            
            # 添加到報告生成器
            self.report_generator.add_activities(all_activities)
            
            # 分類活動
            categorized = self.report_generator.categorize_activities()
            
            # 生成摘要
            summary = []
            summary.append(f"成功抓取 {len(all_activities)} 個活動")
            
            for category, activities in categorized.items():
                if activities:
                    category_name = self.report_generator._get_category_display_name(category)
                    summary.append(f"{category_name}: {len(activities)} 個")
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"活動抓取完成！\n\n" + "\n".join(summary)
                    )
                ]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"抓取活動時發生錯誤: {str(e)}"
                    )
                ]
            )
    
    async def _generate_weekly_report(self, arguments: Dict[str, Any]) -> CallToolResult:
        """生成週報"""
        try:
            report_format = arguments.get("format", "all")
            output_dir = arguments.get("output_dir")
            
            if not self.report_generator.activities:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text="沒有活動資料可以生成報告，請先使用 fetch_weekly_activities 工具抓取資料。"
                        )
                    ]
                )
            
            generated_files = []
            
            # 生成報告資料
            self.report_generator.generate_report_data()
            
            # 根據格式生成報告
            if report_format in ["html", "all"]:
                html_path = self.report_generator.generate_html_report(output_dir)
                generated_files.append(f"HTML: {html_path}")
            
            if report_format in ["excel", "all"]:
                excel_path = self.report_generator.generate_excel_report(output_dir)
                generated_files.append(f"Excel: {excel_path}")
            
            if report_format in ["markdown", "all"]:
                md_path = self.report_generator.generate_markdown_report(output_dir)
                generated_files.append(f"Markdown: {md_path}")
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"週報生成完成！\n\n已生成以下檔案：\n" + "\n".join(generated_files)
                    )
                ]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"生成週報時發生錯誤: {str(e)}"
                    )
                ]
            )
    
    async def _close_browser(self) -> CallToolResult:
        """關閉瀏覽器"""
        try:
            if self.browser_automation:
                self.browser_automation.close_driver()
                self.browser_automation = None
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="Chrome 瀏覽器已關閉。"
                    )
                ]
            )
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"關閉瀏覽器時發生錯誤: {str(e)}"
                    )
                ]
            )

async def main():
    """主程式"""
    # 建立 MCP 伺服器
    mcp_server = WeeklyReportMCPServer()
    
    # 啟動伺服器
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="weekly-report-generator",
                server_version="1.0.0",
                capabilities=mcp_server.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
