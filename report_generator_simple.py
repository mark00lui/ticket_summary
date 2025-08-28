"""
簡化版週報生成模組
不依賴 pandas，使用 CSV 格式替代 Excel
"""

import os
import logging
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Any
from jinja2 import Environment, FileSystemLoader
import config

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleReportGenerator:
    """簡化版週報生成器類別"""
    
    def __init__(self):
        self.activities = []
        self.categorized_activities = {}
        self.report_data = {}
        
    def add_activities(self, activities: List[Dict]):
        """添加活動資料"""
        self.activities.extend(activities)
        logger.info(f"已添加 {len(activities)} 個活動")
    
    def categorize_activities(self) -> Dict[str, List[Dict]]:
        """將活動按類別分類"""
        categorized = {}
        
        # 初始化類別
        for category in config.REPORT_CONFIG["categories"].keys():
            categorized[category] = []
        
        for activity in self.activities:
            category = self._determine_category(activity)
            categorized[category].append(activity)
        
        self.categorized_activities = categorized
        
        # 記錄分類結果
        for category, activities in categorized.items():
            logger.info(f"{category}: {len(activities)} 個活動")
        
        return categorized
    
    def _determine_category(self, activity: Dict) -> str:
        """根據活動內容決定類別"""
        title = activity.get('title', '').lower()
        content = activity.get('content', '').lower()
        status = activity.get('status', '').lower()
        
        # 檢查每個類別的關鍵字
        for category, keywords in config.REPORT_CONFIG["categories"].items():
            for keyword in keywords:
                if (keyword.lower() in title or 
                    keyword.lower() in content or 
                    keyword.lower() in status):
                    return category
        
        # 如果沒有匹配，歸類為其他
        return 'other'
    
    def generate_report_data(self) -> Dict[str, Any]:
        """生成報告資料"""
        # 計算日期範圍
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # 統計資料
        total_activities = len(self.activities)
        eservice_activities = len([a for a in self.activities if a.get('source') == 'eservice'])
        jira_activities = len([a for a in self.activities if a.get('source') == 'jira'])
        
        # 按日期分組
        activities_by_date = {}
        for activity in self.activities:
            date_str = activity['date'].strftime(config.REPORT_CONFIG["date_format"])
            if date_str not in activities_by_date:
                activities_by_date[date_str] = []
            activities_by_date[date_str].append(activity)
        
        # 按狀態統計
        status_stats = {}
        for activity in self.activities:
            status = activity.get('status', '未知')
            status_stats[status] = status_stats.get(status, 0) + 1
        
        self.report_data = {
            'report_date': datetime.now().strftime(config.REPORT_CONFIG["date_format"]),
            'start_date': start_date.strftime(config.REPORT_CONFIG["date_format"]),
            'end_date': end_date.strftime(config.REPORT_CONFIG["date_format"]),
            'total_activities': total_activities,
            'eservice_activities': eservice_activities,
            'jira_activities': jira_activities,
            'categorized_activities': self.categorized_activities,
            'activities_by_date': activities_by_date,
            'status_stats': status_stats,
            'summary': self._generate_summary()
        }
        
        return self.report_data
    
    def _generate_summary(self) -> str:
        """生成摘要"""
        if not self.activities:
            return "本週無活動記錄"
        
        summary_parts = []
        
        # 總體統計
        summary_parts.append(f"本週共處理 {len(self.activities)} 個活動")
        
        # 按來源統計
        eservice_count = len([a for a in self.activities if a.get('source') == 'eservice'])
        jira_count = len([a for a in self.activities if a.get('source') == 'jira'])
        
        if eservice_count > 0:
            summary_parts.append(f"其中 eService 相關 {eservice_count} 個")
        if jira_count > 0:
            summary_parts.append(f"Jira 相關 {jira_count} 個")
        
        # 按類別統計
        for category, activities in self.categorized_activities.items():
            if activities:
                category_name = self._get_category_display_name(category)
                summary_parts.append(f"{category_name}: {len(activities)} 個")
        
        return "，".join(summary_parts) + "。"
    
    def _get_category_display_name(self, category: str) -> str:
        """取得類別顯示名稱"""
        display_names = {
            'customer_support': '客戶支援',
            'bug_fixes': '錯誤修復',
            'feature_development': '功能開發',
            'meetings': '會議討論',
            'documentation': '文件撰寫',
            'other': '其他事項'
        }
        return display_names.get(category, category)
    
    def generate_html_report(self, output_path: str = None) -> str:
        """生成 HTML 報告"""
        if not output_path:
            os.makedirs(config.REPORT_CONFIG["output_dir"], exist_ok=True)
            output_path = os.path.join(
                config.REPORT_CONFIG["output_dir"],
                f"weekly_report_{datetime.now().strftime('%Y%m%d')}.html"
            )
        
        # 確保報告資料已生成
        if not self.report_data:
            self.generate_report_data()
        
        # 使用 Jinja2 模板
        template_dir = config.REPORT_CONFIG["template_dir"]
        if not os.path.exists(template_dir):
            os.makedirs(template_dir, exist_ok=True)
            self._create_html_template()
        
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template('weekly_report.html')
        
        html_content = template.render(**self.report_data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML 報告已生成: {output_path}")
        return output_path
    
    def generate_csv_report(self, output_path: str = None) -> str:
        """生成 CSV 報告（替代 Excel）"""
        if not output_path:
            os.makedirs(config.REPORT_CONFIG["output_dir"], exist_ok=True)
            output_path = os.path.join(
                config.REPORT_CONFIG["output_dir"],
                f"weekly_report_{datetime.now().strftime('%Y%m%d')}.csv"
            )
        
        # 確保報告資料已生成
        if not self.report_data:
            self.generate_report_data()
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['日期', '標題', '內容', '狀態', '來源', '類別']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            
            for activity in self.activities:
                writer.writerow({
                    '日期': activity['date'].strftime(config.REPORT_CONFIG["date_format"]),
                    '標題': activity['title'],
                    '內容': activity['content'],
                    '狀態': activity['status'],
                    '來源': activity['source'],
                    '類別': self._determine_category(activity)
                })
        
        logger.info(f"CSV 報告已生成: {output_path}")
        return output_path
    
    def generate_markdown_report(self, output_path: str = None) -> str:
        """生成 Markdown 報告"""
        if not output_path:
            os.makedirs(config.REPORT_CONFIG["output_dir"], exist_ok=True)
            output_path = os.path.join(
                config.REPORT_CONFIG["output_dir"],
                f"weekly_report_{datetime.now().strftime('%Y%m%d')}.md"
            )
        
        # 確保報告資料已生成
        if not self.report_data:
            self.generate_report_data()
        
        markdown_content = self._generate_markdown_content()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logger.info(f"Markdown 報告已生成: {output_path}")
        return output_path
    
    def _generate_markdown_content(self) -> str:
        """生成 Markdown 內容"""
        content = []
        
        # 標題
        content.append(f"# 週報 - {self.report_data['start_date']} 至 {self.report_data['end_date']}")
        content.append("")
        
        # 摘要
        content.append("## 摘要")
        content.append(self.report_data['summary'])
        content.append("")
        
        # 統計資料
        content.append("## 統計資料")
        content.append(f"- 總活動數: {self.report_data['total_activities']}")
        content.append(f"- eService 活動: {self.report_data['eservice_activities']}")
        content.append(f"- Jira 活動: {self.report_data['jira_activities']}")
        content.append("")
        
        # 按類別分類
        content.append("## 按類別分類")
        for category, activities in self.categorized_activities.items():
            if activities:
                category_name = self._get_category_display_name(category)
                content.append(f"### {category_name} ({len(activities)} 個)")
                
                for activity in activities:
                    date_str = activity['date'].strftime(config.REPORT_CONFIG["date_format"])
                    content.append(f"- **{date_str}** - {activity['title']}")
                    if activity['content']:
                        content.append(f"  - {activity['content'][:100]}...")
                content.append("")
        
        # 按日期分類
        content.append("## 按日期分類")
        for date_str in sorted(self.report_data['activities_by_date'].keys()):
            activities = self.report_data['activities_by_date'][date_str]
            content.append(f"### {date_str} ({len(activities)} 個)")
            
            for activity in activities:
                content.append(f"- **{activity['title']}** ({activity['source']})")
                if activity['status']:
                    content.append(f"  - 狀態: {activity['status']}")
                if activity['content']:
                    content.append(f"  - {activity['content'][:100]}...")
            content.append("")
        
        return "\n".join(content)
    
    def _create_html_template(self):
        """建立 HTML 模板"""
        template_content = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>週報 - {{ start_date }} 至 {{ end_date }}</title>
    <style>
        body {
            font-family: 'Microsoft JhengHei', Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin-top: 30px;
        }
        h3 {
            color: #2980b9;
            margin-top: 25px;
        }
        .summary {
            background-color: #ecf0f1;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
            font-size: 18px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .stat-card {
            background-color: #3498db;
            color: white;
            padding: 20px;
            border-radius: 5px;
            text-align: center;
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
        }
        .activity-item {
            background-color: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        }
        .activity-date {
            color: #7f8c8d;
            font-size: 0.9em;
        }
        .activity-title {
            font-weight: bold;
            color: #2c3e50;
            margin: 5px 0;
        }
        .activity-content {
            color: #34495e;
            margin: 5px 0;
        }
        .activity-status {
            display: inline-block;
            background-color: #e74c3c;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 0.8em;
        }
        .category-section {
            margin: 30px 0;
        }
        .source-badge {
            display: inline-block;
            background-color: #95a5a6;
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.8em;
            margin-left: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>週報 - {{ start_date }} 至 {{ end_date }}</h1>
        
        <div class="summary">
            {{ summary }}
        </div>
        
        <h2>統計資料</h2>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{{ total_activities }}</div>
                <div>總活動數</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ eservice_activities }}</div>
                <div>eService 活動</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ jira_activities }}</div>
                <div>Jira 活動</div>
            </div>
        </div>
        
        <h2>按類別分類</h2>
        {% for category, activities in categorized_activities.items() %}
            {% if activities %}
            <div class="category-section">
                <h3>{{ category|title }} ({{ activities|length }} 個)</h3>
                {% for activity in activities %}
                <div class="activity-item">
                    <div class="activity-date">{{ activity.date.strftime('%Y-%m-%d %H:%M') }}</div>
                    <div class="activity-title">
                        {{ activity.title }}
                        <span class="source-badge">{{ activity.source }}</span>
                    </div>
                    {% if activity.content %}
                    <div class="activity-content">{{ activity.content[:200] }}{% if activity.content|length > 200 %}...{% endif %}</div>
                    {% endif %}
                    {% if activity.status %}
                    <div class="activity-status">{{ activity.status }}</div>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
            {% endif %}
        {% endfor %}
        
        <h2>按日期分類</h2>
        {% for date_str, activities in activities_by_date.items() %}
        <div class="category-section">
            <h3>{{ date_str }} ({{ activities|length }} 個)</h3>
            {% for activity in activities %}
            <div class="activity-item">
                <div class="activity-title">
                    {{ activity.title }}
                    <span class="source-badge">{{ activity.source }}</span>
                </div>
                {% if activity.content %}
                <div class="activity-content">{{ activity.content[:200] }}{% if activity.content|length > 200 %}...{% endif %}</div>
                {% endif %}
                {% if activity.status %}
                <div class="activity-status">{{ activity.status }}</div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% endfor %}
    </div>
</body>
</html>"""
        
        template_path = os.path.join(config.REPORT_CONFIG["template_dir"], "weekly_report.html")
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
