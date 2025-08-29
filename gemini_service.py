"""
Gemini API 服務模塊
用於生成周報的 AI 分析功能
"""

import os
import json
import logging
from datetime import datetime
import google.generativeai as genai

# 設定日誌
logger = logging.getLogger(__name__)

class GeminiService:
    """Gemini API 服務類"""
    
    def __init__(self, api_key=None):
        """初始化 Gemini 服務"""
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("需要提供 GEMINI_API_KEY 環境變數或直接傳入 api_key 參數")
        
        # 配置 Gemini
        genai.configure(api_key=self.api_key)
        
        # 初始化模型
        try:
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            logger.info("Gemini 2.0 模型初始化成功")
        except Exception as e:
            logger.error(f"Gemini 模型初始化失敗: {e}")
            raise
    
    def generate_weekly_report(self, json_file_path, output_dir="./reports"):
        """生成周報"""
        try:
            print("🤖 正在使用 Gemini 生成周報...")
            
            # 讀取 JSON 文件
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 優化數據 - 減少數據量以避免超時
            # optimized_data = self._optimize_data_for_gemini(data)
            optimized_data = data
            
            # 構建 prompt
            prompt = self._build_prompt(optimized_data)
            
            print(f"📊 發送數據大小: {len(prompt)} 字符")
            
            # 調用 Gemini API 並增加超時處理
            try:
                # 設定生成配置
                generation_config = genai.types.GenerationConfig(
                    temperature=0.3,
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=8192,
                )
                
                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                
                if response.text:
                    # 生成輸出文件名
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    html_file = f"{output_dir}/weekly_report_{timestamp}.html"
                    
                    # 確保輸出目錄存在
                    os.makedirs(output_dir, exist_ok=True)
                    
                    # 保存 HTML 文件
                    with open(html_file, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    
                    print(f"✅ 周報已生成: {html_file}")
                    return html_file
                else:
                    logger.error("Gemini 返回空內容")
                    return None
                    
            except Exception as api_error:
                logger.error(f"Gemini API 調用失敗: {api_error}")
                print(f"❌ Gemini API 調用失敗: {api_error}")
                
                # 嘗試使用簡化版本
                return self._generate_simple_report(optimized_data, output_dir)
                
        except Exception as e:
            logger.error(f"生成周報失敗: {e}")
            return None
    
    def _optimize_data_for_gemini(self, data):
        """優化數據以減少大小，避免超時"""
        try:
            optimized_data = {
                'report_date': data.get('report_date', ''),
                'scan_days': data.get('scan_days', 0),
                'total_activities': data.get('total_activities', 0),
                'activities': []
            }
            
            # 只取最近的活動，限制數量
            activities = data.get('activities', [])
            max_activities = 10  # 限制最多 10 個活動
            
            for activity in activities[:max_activities]:
                optimized_activity = {
                    'id': activity.get('id', ''),
                    'title': activity.get('title', '')[:100],  # 限制標題長度
                    'date': activity.get('date', ''),
                    'status': activity.get('status', ''),
                    'content': activity.get('content', '')[:200],  # 限制內容長度
                    'detailed_interactions': []
                }
                
                # 優化互動內容
                interactions = activity.get('detailed_interactions', [])
                for interaction in interactions[:3]:  # 每個活動最多 3 個互動
                    optimized_interaction = {
                        'timestamp': interaction.get('timestamp', ''),
                        'author': interaction.get('author', ''),
                        'content': interaction.get('content', '')[:150],  # 限制內容長度
                        'ltr_content': interaction.get('ltr_content', '')[:300],  # 限制 LTR 內容長度
                        'jira_links': interaction.get('jira_links', [])
                    }
                    optimized_activity['detailed_interactions'].append(optimized_interaction)
                
                optimized_data['activities'].append(optimized_activity)
            
            return optimized_data
            
        except Exception as e:
            logger.error(f"優化數據失敗: {e}")
            return data
    
    def _generate_simple_report(self, data, output_dir):
        """生成簡化的 HTML 報告（當 Gemini API 失敗時使用）"""
        try:
            print("🔄 使用簡化模式生成報告...")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_file = f"{output_dir}/weekly_report_simple_{timestamp}.html"
            
            # 生成簡單的 HTML 表格
            # html_content = self._create_simple_html_table(data)
            html_content = data
            
            # 保存文件
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ 簡化周報已生成: {html_file}")
            return html_file
            
        except Exception as e:
            logger.error(f"生成簡化報告失敗: {e}")
            return None
    
    def _create_simple_html_table(self, data):
        """創建簡單的 HTML 表格"""
        report_date = data.get('report_date', '')
        scan_days = data.get('scan_days', 0)
        total_activities = data.get('total_activities', 0)
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>FAE 周報</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; font-weight: bold; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .highlight {{ background-color: #e6f3ff; }}
        .jira-link {{ color: #0066cc; text-decoration: none; }}
        .jira-link:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1>FAE 周報</h1>
    <p><strong>生成時間:</strong> {report_date}</p>
    <p><strong>掃描範圍:</strong> 過去 {scan_days} 天</p>
    <p><strong>活動數量:</strong> {total_activities} 個</p>
    
    <table>
        <thead>
            <tr>
                <th>Ticket ID</th>
                <th>標題</th>
                <th>日期</th>
                <th>狀態</th>
                <th>Jira 連結</th>
                <th>回應重點</th>
            </tr>
        </thead>
        <tbody>
"""
        
        for activity in data.get('activities', []):
            # 提取 Jira 連結
            jira_links = []
            for interaction in activity.get('detailed_interactions', []):
                for jira_link in interaction.get('jira_links', []):
                    jira_links.append(jira_link.get('ticket_id', ''))
            
            jira_links_text = ', '.join(set(jira_links)) if jira_links else '無'
            
            # 提取回應重點
            response_summary = ""
            for interaction in activity.get('detailed_interactions', []):
                content = interaction.get('ltr_content', '') or interaction.get('content', '')
                if content:
                    response_summary += content[:100] + "... "
            
            response_summary = response_summary[:200] + "..." if len(response_summary) > 200 else response_summary
            
            html += f"""
            <tr>
                <td>{activity.get('id', 'N/A')}</td>
                <td>{activity.get('title', 'N/A')}</td>
                <td>{activity.get('date', 'N/A')}</td>
                <td>{activity.get('status', 'N/A')}</td>
                <td>{jira_links_text}</td>
                <td>{response_summary}</td>
            </tr>
            """
        
        html += """
        </tbody>
    </table>
    
    <p><em>此報告由系統自動生成，突出 FAE 的專業能力和解決問題的決心。</em></p>
</body>
</html>
"""
        
        return html
    
    def _build_prompt(self, data):
        """構建發送給 Gemini 的 prompt"""
        
        # 將數據轉換為 JSON 字符串
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        
        prompt = f"""
請分析以下 FAE 活動數據並生成 HTML 表格格式的周報。

數據包含：
- 活動數量：{data.get('total_activities', 0)} 個
- 掃描範圍：過去 {data.get('scan_days', 0)} 天

要求：
0. 分析activities的內容, /a/tickets/XXXXXX , 其中XXXXXX為Ticket ID, 它的json內層有關連的文字內容以及Jira號
1. 提取所有 Jira 號碼 (https://ticket.quectel.com/browse/FAE-XXXXXX 格式), FAE-XXXXXX 是Jira號
2. 因為是weekly report, 所以只取最近7天的數據
3. 分析回應重點，突出 FAE 的專業能力
4. 生成美觀的 HTML 表格，包含：Ticket ID、Jira號碼、標題、狀態(Closed, Pending, Waiting on Third Party)、客戶與我們的問答重點
5. 只輸出 HTML 表格，不要其他內容
6. 使用美觀的 CSS 樣式

數據：
{json_data}
"""
        
        return prompt
    
    def test_connection(self):
        """測試 Gemini 連接"""
        try:
            response = self.model.generate_content("Hello, 請回覆 '連接成功' 來確認 Gemini API 正常工作。")
            if response.text and "連接成功" in response.text:
                print("✅ Gemini API 連接測試成功")
                return True
            else:
                print("❌ Gemini API 連接測試失敗")
                return False
        except Exception as e:
            print(f"❌ Gemini API 連接測試失敗: {e}")
            return False
