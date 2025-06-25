#!/usr/bin/env python3
"""
RSS抓取并推送到Slack
专门用于抓取SoSoValue中文频道的RSS内容
"""

import feedparser
import schedule
import time
import json
import os
import requests
import re
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config import Config

class RSSSlackBot:
    def __init__(self):
        # RSS配置
        self.rss_url = "https://rsshub.app/telegram/channel/SoSoValue_CN"
        
        # Slack配置
        self.slack_client = WebClient(token=Config.SLACK_BOT_TOKEN)
        self.channel_a = Config.SLACK_CHANNEL_A  # 画板频道
        self.channel_b = Config.SLACK_CHANNEL_B  # 消息频道
        
        # 记录已推送的消息
        self.pushed_links_file = "pushed_links.json"
        self.pushed_links = self.load_pushed_links()
        
        # 关键词过滤
        self.filter_keywords = Config.CONTENT_FILTER_KEYWORDS
        
    def load_pushed_links(self):
        """加载已推送的链接"""
        if os.path.exists(self.pushed_links_file):
            try:
                with open(self.pushed_links_file, 'r', encoding='utf-8') as f:
                    return set(json.load(f))
            except:
                return set()
        return set()
    
    def save_pushed_links(self):
        """保存已推送的链接"""
        with open(self.pushed_links_file, 'w', encoding='utf-8') as f:
            json.dump(list(self.pushed_links), f, ensure_ascii=False, indent=2)
    
    def should_include_message(self, title, content):
        """判断消息是否应该被包含"""
        if not self.filter_keywords:
            return True
        
        text = (title + " " + content).lower()
        return any(keyword.lower() in text for keyword in self.filter_keywords if keyword.strip())
    
    def extract_numbered_content(self, content):
        """提取按数字排序的内容，去掉前缀日期和正文中的日期"""
        # 保留换行
        content = re.sub(r'<br\s*/?>', '\n', content)
        # 去除所有日期
        content = re.sub(r'(\d{2,4}[.\-/]\s*\d{1,2}[.\-/]\d{1,2})', '', content)
        content = re.sub(r'(\d{1,2}[.\-/]\s*\d{1,2}/)\d{1,2}/', '', content)
        # 匹配 1/ 内容 – <a href="网址" ...>source</a>
        pattern = r'([1-9][0-9]?)/\s*([^–]+)–\s*<a href="([^"]+)"[^>]*>source</a>'
        matches = re.findall(pattern, content)
        formatted_items = []
        for match in matches:
            number = match[0]
            text = match[1].strip()
            link = match[2]
            formatted_items.append(f"{number}. {text} <{link}|【详情】>")
        if formatted_items:
            return formatted_items
        # 如果没有，尝试更简单的格式
        pattern2 = r'([1-9][0-9]?)/\s*([^–\n]+)'
        matches = re.findall(pattern2, content)
        for match in matches:
            number = match[0]
            text = match[1].strip()
            formatted_items.append(f"{number}. {text}")
        return formatted_items
    
    def format_message_for_channel_a(self, entry):
        """格式化消息用于频道A（画板），只输出内容列表，不重复标题"""
        # 提取主要内容
        content = entry.summary
        # 提取按数字排序的内容
        numbered_items = self.extract_numbered_content(content)
        if numbered_items:
            # 在每条内容之间添加换行
            formatted_msg = f"\n\n".join(numbered_items[:10]).strip()
        else:
            # 如果没有找到数字格式，使用原始内容
            content = re.sub(r'<[^>]+>', '', content)
            formatted_msg = f"{content[:500]}{'...' if len(content) > 500 else ''}"
        return formatted_msg
    
    def format_message_for_channel_b(self, entry):
        """格式化消息用于频道B（消息列表）"""
        # 提取标题（去掉前缀）
        title = entry.title
        if "SoSoValue" in title:
            # 提取日期部分
            date_match = re.search(r'(\d{4}/\d{1,2}/\d{1,2})', title)
            if date_match:
                title = f"每日加密热点新闻榜单｜{date_match.group(1)}"
        
        # 提取主要内容
        content = entry.summary
        
        # 提取按数字排序的内容
        numbered_items = self.extract_numbered_content(content)
        
        if numbered_items:
            # 格式化消息
            formatted_msg = f"""
*{title}*

{chr(10).join(numbered_items[:5])}  # 最多显示5条

*完整内容:* {entry.link}
            """.strip()
        else:
            # 如果没有找到数字格式，使用原始内容
            content = re.sub(r'<[^>]+>', '', content)
            formatted_msg = f"""
*{title}*

{content[:300]}{'...' if len(content) > 300 else ''}

*完整内容:* {entry.link}
            """.strip()
        
        return formatted_msg
    
    def send_to_slack(self, message, channel, title=None):
        """发送消息到Slack，主标题只用日期，并记录待删除消息"""
        try:
            # 如果title为None，则用 entry.title 提取日期标题
            if title is None:
                # 尝试从最近一次消息中提取标题
                date_today = datetime.now().strftime('%Y/%-m/%-d')
                title = f"每日加密热点新闻榜单｜{date_today}"
            # 在消息底部加自动删除提示，添加更多换行
            message = message.strip() + "\n\n\n本消息 48 小时后自动删除"
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": title,
                        "emoji": True
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": message
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        }
                    ]
                }
            ]
            response = self.slack_client.chat_postMessage(
                channel=channel,
                blocks=blocks,
                text=title
            )
            # 记录待删除消息
            ts = response['ts']
            self.save_pending_delete(channel, ts)
            print(f"✅ 成功发送到Slack频道: {channel}")
            return True
        except SlackApiError as e:
            print(f"❌ 发送到Slack失败: {e.response['error']}")
            return False
    
    def fetch_rss_with_headers(self):
        """使用请求头抓取RSS"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        try:
            # 先尝试用requests获取
            response = requests.get(self.rss_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # 然后用feedparser解析
            feed = feedparser.parse(response.content)
            return feed
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 网络请求失败: {e}")
            # 如果requests失败，尝试直接用feedparser
            try:
                feed = feedparser.parse(self.rss_url)
                return feed
            except Exception as e2:
                print(f"❌ feedparser也失败: {e2}")
                return None
    
    def fetch_and_process(self):
        """抓取RSS并处理，只推送当天内容，两个频道内容一致，均用频道A格式"""
        print(f"🔄 开始抓取RSS: {self.rss_url}")
        
        try:
            feed = self.fetch_rss_with_headers()
            
            if not feed or not feed.entries:
                print("📭 没有获取到新消息")
                if feed and hasattr(feed, 'status'):
                    print(f"RSS状态码: {feed.status}")
                return
            
            print(f"📝 获取到 {len(feed.entries)} 条消息")
            
            # 获取今天日期字符串
            today = datetime.now().strftime('%Y/%-m/%-d')  # 2025/6/25
            today_alt = datetime.now().strftime('%Y/%#m/%#d')  # 兼容Windows
            today_title = f"每日加密热点新闻榜单｜{today}"
            today_title_alt = f"每日加密热点新闻榜单｜{today_alt}"
            
            new_messages = []
            
            for entry in feed.entries:
                # 只推送当天内容
                if today_title not in entry.title and today_title_alt not in entry.title:
                    continue
                # 不做去重，方便调试
                # 检查关键词过滤
                if not self.should_include_message(entry.title, entry.summary):
                    continue
                new_messages.append(entry)
            
            if not new_messages:
                print("📭 没有找到当天的内容")
                return
            
            print(f"📤 准备推送 {len(new_messages)} 条当天内容")
            
            # 只推送到C06AUSCKYKF频道
            for entry in new_messages:
                content = self.format_message_for_channel_a(entry)
                self.send_to_slack(content, 'C06AUSCKYKF')
            
            print(f"✅ 成功推送 {len(new_messages)} 条当天内容到C06AUSCKYKF频道")
            
        except Exception as e:
            print(f"❌ 抓取RSS失败: {e}")
    
    def save_pending_delete(self, channel, ts):
        """保存待删除消息"""
        file = 'pending_deletes.json'
        record = {'channel': channel, 'ts': ts, 'send_time': time.time()}
        try:
            with open(file, 'r') as f:
                data = json.load(f)
        except:
            data = []
        data.append(record)
        with open(file, 'w') as f:
            json.dump(data, f)
    
    def delete_expired_messages(self):
        """定时检查并删除过期消息"""
        file = 'pending_deletes.json'
        try:
            with open(file, 'r') as f:
                data = json.load(f)
        except:
            data = []
        
        if not data:
            return
        
        print(f"🔍 检查 {len(data)} 条待删除消息...")
        current_time = time.time()
        new_data = []
        delete_after_seconds = 172800  # 48小时 = 48 * 60 * 60 = 172800秒
        
        for record in data:
            time_diff = current_time - record['send_time']
            hours_diff = time_diff / 3600
            print(f"   消息 {record['ts']}: 已发送 {hours_diff:.1f} 小时")
            
            if time_diff >= delete_after_seconds:  # 48小时后删除
                try:
                    print(f"   🗑️  尝试删除消息: {record['ts']}")
                    self.slack_client.chat_delete(channel=record['channel'], ts=record['ts'])
                    print(f"   ✅ 成功删除消息: {record['ts']}")
                except Exception as e:
                    print(f"   ❌ 删除失败: {e}")
                    new_data.append(record)  # 保留未成功删除的
            else:
                remaining_hours = (delete_after_seconds - time_diff) / 3600
                print(f"   ⏳ 消息未过期，还需等待 {remaining_hours:.1f} 小时")
                new_data.append(record)
        
        with open(file, 'w') as f:
            json.dump(new_data, f)
        
        print(f"📊 删除检查完成，剩余 {len(new_data)} 条待删除消息")
    
    def run_scheduler(self):
        """运行定时任务"""
        print("🚀 RSS抓取机器人启动")
        print(f"📡 RSS地址: {self.rss_url}")
        print(f"🎯 过滤关键词: {self.filter_keywords}")
        print(f"⏰ 执行时间: 每周一到周五 10:00")
        print("=" * 50)
        
        # 检查是否在GitHub Actions环境中
        if os.getenv('GITHUB_ACTIONS'):
            print("🔧 检测到GitHub Actions环境，执行单次任务")
            self.fetch_and_process()
            print("✅ 任务完成，退出")
            return
        
        # 本地环境：立即执行一次
        self.fetch_and_process()
        
        # 设置定时任务：每周一到周五的早上10:00
        schedule.every().monday.at("10:00").do(self.fetch_and_process)
        schedule.every().tuesday.at("10:00").do(self.fetch_and_process)
        schedule.every().wednesday.at("10:00").do(self.fetch_and_process)
        schedule.every().thursday.at("10:00").do(self.fetch_and_process)
        schedule.every().friday.at("10:00").do(self.fetch_and_process)
        
        # 运行调度器
        while True:
            try:
                schedule.run_pending()
                self.delete_expired_messages()  # 定时检查并删除过期消息
                time.sleep(60)
            except KeyboardInterrupt:
                print("\n🛑 收到中断信号，正在退出...")
                break
            except Exception as e:
                print(f"❌ 调度器错误: {e}")
                time.sleep(60)

def main():
    """主函数"""
    # 检查配置
    if not Config.SLACK_BOT_TOKEN:
        print("❌ 错误: 未设置SLACK_BOT_TOKEN")
        print("请在.env文件中设置你的Slack Bot Token")
        return
    
    if not Config.SLACK_CHANNEL_A or not Config.SLACK_CHANNEL_B:
        print("❌ 错误: 未设置Slack频道ID")
        print("请在.env文件中设置SLACK_CHANNEL_A和SLACK_CHANNEL_B")
        return
    
    # 创建并运行机器人
    bot = RSSSlackBot()
    bot.run_scheduler()

if __name__ == "__main__":
    main() 