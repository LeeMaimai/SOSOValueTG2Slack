#!/usr/bin/env python3
"""
Slack频道消息删除工具
支持删除频道中的所有消息或特定条件的消息
"""

import os
import time
import json
from datetime import datetime, timedelta
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config import Config

class SlackMessageDeleter:
    def __init__(self):
        self.slack_client = WebClient(token=Config.SLACK_BOT_TOKEN)
        self.channel_a = Config.SLACK_CHANNEL_A
        self.channel_b = Config.SLACK_CHANNEL_B
        
    def get_channel_history(self, channel_id, limit=1000):
        """获取频道历史消息"""
        try:
            response = self.slack_client.conversations_history(
                channel=channel_id,
                limit=limit
            )
            return response['messages']
        except SlackApiError as e:
            print(f"❌ 获取频道历史失败: {e.response['error']}")
            return []
    
    def delete_message(self, channel_id, ts):
        """删除单条消息"""
        try:
            self.slack_client.chat_delete(channel=channel_id, ts=ts)
            return True
        except SlackApiError as e:
            if e.response['error'] == 'message_not_found':
                print(f"⚠️  消息 {ts} 不存在或已被删除")
                return True
            elif e.response['error'] == 'cant_delete_message':
                print(f"❌ 无法删除消息 {ts}: 权限不足或消息太旧")
                return False
            else:
                print(f"❌ 删除消息 {ts} 失败: {e.response['error']}")
                return False
    
    def delete_all_messages(self, channel_id, channel_name="频道"):
        """删除频道中的所有消息"""
        print(f"🗑️  开始删除 {channel_name} 中的所有消息...")
        
        messages = self.get_channel_history(channel_id)
        if not messages:
            print(f"📭 {channel_name} 中没有消息")
            return
        
        print(f"📝 找到 {len(messages)} 条消息")
        
        deleted_count = 0
        failed_count = 0
        
        for i, message in enumerate(messages, 1):
            ts = message['ts']
            user = message.get('user', 'unknown')
            text = message.get('text', '')[:50] + '...' if len(message.get('text', '')) > 50 else message.get('text', '')
            
            print(f"   [{i}/{len(messages)}] 删除消息 {ts} (用户: {user}): {text}")
            
            if self.delete_message(channel_id, ts):
                deleted_count += 1
            else:
                failed_count += 1
            
            # 添加延迟避免API限制
            time.sleep(0.1)
        
        print(f"✅ 删除完成: 成功 {deleted_count} 条，失败 {failed_count} 条")
    
    def delete_messages_by_time(self, channel_id, hours_ago, channel_name="频道"):
        """删除指定时间范围内的消息"""
        cutoff_time = time.time() - (hours_ago * 3600)
        print(f"🗑️  删除 {channel_name} 中 {hours_ago} 小时内的消息...")
        
        messages = self.get_channel_history(channel_id)
        if not messages:
            print(f"📭 {channel_name} 中没有消息")
            return
        
        filtered_messages = [msg for msg in messages if float(msg['ts']) > cutoff_time]
        
        if not filtered_messages:
            print(f"📭 没有找到 {hours_ago} 小时内的消息")
            return
        
        print(f"📝 找到 {len(filtered_messages)} 条符合条件的消息")
        
        deleted_count = 0
        failed_count = 0
        
        for i, message in enumerate(filtered_messages, 1):
            ts = message['ts']
            user = message.get('user', 'unknown')
            text = message.get('text', '')[:50] + '...' if len(message.get('text', '')) > 50 else message.get('text', '')
            
            print(f"   [{i}/{len(filtered_messages)}] 删除消息 {ts} (用户: {user}): {text}")
            
            if self.delete_message(channel_id, ts):
                deleted_count += 1
            else:
                failed_count += 1
            
            time.sleep(0.1)
        
        print(f"✅ 删除完成: 成功 {deleted_count} 条，失败 {failed_count} 条")
    
    def delete_messages_by_user(self, channel_id, user_id, channel_name="频道"):
        """删除指定用户的消息"""
        print(f"🗑️  删除 {channel_name} 中用户 {user_id} 的消息...")
        
        messages = self.get_channel_history(channel_id)
        if not messages:
            print(f"📭 {channel_name} 中没有消息")
            return
        
        user_messages = [msg for msg in messages if msg.get('user') == user_id]
        
        if not user_messages:
            print(f"📭 没有找到用户 {user_id} 的消息")
            return
        
        print(f"📝 找到 {len(user_messages)} 条用户消息")
        
        deleted_count = 0
        failed_count = 0
        
        for i, message in enumerate(user_messages, 1):
            ts = message['ts']
            text = message.get('text', '')[:50] + '...' if len(message.get('text', '')) > 50 else message.get('text', '')
            
            print(f"   [{i}/{len(user_messages)}] 删除消息 {ts}: {text}")
            
            if self.delete_message(channel_id, ts):
                deleted_count += 1
            else:
                failed_count += 1
            
            time.sleep(0.1)
        
        print(f"✅ 删除完成: 成功 {deleted_count} 条，失败 {failed_count} 条")
    
    def delete_pending_deletes(self):
        """删除pending_deletes.json中记录的所有消息"""
        file = 'pending_deletes.json'
        try:
            with open(file, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            print("📭 pending_deletes.json 文件不存在")
            return
        except json.JSONDecodeError:
            print("❌ pending_deletes.json 文件格式错误")
            return
        
        if not data:
            print("📭 没有待删除的消息记录")
            return
        
        print(f"🗑️  删除 {len(data)} 条待删除消息...")
        
        deleted_count = 0
        failed_count = 0
        
        for i, record in enumerate(data, 1):
            channel = record['channel']
            ts = record['ts']
            send_time = datetime.fromtimestamp(record['send_time']).strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"   [{i}/{len(data)}] 删除消息 {ts} (发送时间: {send_time})")
            
            if self.delete_message(channel, ts):
                deleted_count += 1
            else:
                failed_count += 1
            
            time.sleep(0.1)
        
        # 清空pending_deletes.json文件
        with open(file, 'w') as f:
            json.dump([], f)
        
        print(f"✅ 删除完成: 成功 {deleted_count} 条，失败 {failed_count} 条")
        print("📝 已清空 pending_deletes.json 文件")
    
    def show_channel_info(self):
        """显示频道信息"""
        print("📊 频道信息:")
        print(f"   频道A (画板): {self.channel_a}")
        print(f"   频道B (消息): {self.channel_b}")
        
        # 获取频道A的消息数量
        messages_a = self.get_channel_history(self.channel_a, limit=1000)
        print(f"   频道A消息数量: {len(messages_a)}")
        
        # 获取频道B的消息数量
        messages_b = self.get_channel_history(self.channel_b, limit=1000)
        print(f"   频道B消息数量: {len(messages_b)}")
        
        # 显示pending_deletes.json中的记录
        try:
            with open('pending_deletes.json', 'r') as f:
                pending_data = json.load(f)
            print(f"   待删除消息记录: {len(pending_data)} 条")
        except:
            print("   待删除消息记录: 0 条")

def main():
    """主函数"""
    print("🗑️  Slack频道消息删除工具")
    print("=" * 50)
    
    # 检查配置
    if not Config.SLACK_BOT_TOKEN:
        print("❌ 错误: 未设置SLACK_BOT_TOKEN")
        return
    
    if not Config.SLACK_CHANNEL_A or not Config.SLACK_CHANNEL_B:
        print("❌ 错误: 未设置Slack频道ID")
        return
    
    deleter = SlackMessageDeleter()
    
    # 显示频道信息
    deleter.show_channel_info()
    print()
    
    while True:
        print("请选择操作:")
        print("1. 删除频道A中的所有消息")
        print("2. 删除频道B中的所有消息")
        print("3. 删除两个频道中的所有消息")
        print("4. 删除频道A中最近24小时的消息")
        print("5. 删除频道B中最近24小时的消息")
        print("6. 删除pending_deletes.json中记录的消息")
        print("7. 显示频道信息")
        print("0. 退出")
        
        choice = input("\n请输入选项 (0-7): ").strip()
        
        if choice == '0':
            print("👋 退出程序")
            break
        elif choice == '1':
            confirm = input("⚠️  确定要删除频道A中的所有消息吗？(y/N): ").strip().lower()
            if confirm == 'y':
                deleter.delete_all_messages(Config.SLACK_CHANNEL_A, "频道A")
        elif choice == '2':
            confirm = input("⚠️  确定要删除频道B中的所有消息吗？(y/N): ").strip().lower()
            if confirm == 'y':
                deleter.delete_all_messages(Config.SLACK_CHANNEL_B, "频道B")
        elif choice == '3':
            confirm = input("⚠️  确定要删除两个频道中的所有消息吗？(y/N): ").strip().lower()
            if confirm == 'y':
                deleter.delete_all_messages(Config.SLACK_CHANNEL_A, "频道A")
                deleter.delete_all_messages(Config.SLACK_CHANNEL_B, "频道B")
        elif choice == '4':
            confirm = input("⚠️  确定要删除频道A中最近24小时的消息吗？(y/N): ").strip().lower()
            if confirm == 'y':
                deleter.delete_messages_by_time(Config.SLACK_CHANNEL_A, 24, "频道A")
        elif choice == '5':
            confirm = input("⚠️  确定要删除频道B中最近24小时的消息吗？(y/N): ").strip().lower()
            if confirm == 'y':
                deleter.delete_messages_by_time(Config.SLACK_CHANNEL_B, 24, "频道B")
        elif choice == '6':
            confirm = input("⚠️  确定要删除pending_deletes.json中记录的消息吗？(y/N): ").strip().lower()
            if confirm == 'y':
                deleter.delete_pending_deletes()
        elif choice == '7':
            deleter.show_channel_info()
        else:
            print("❌ 无效选项，请重新选择")
        
        print("\n" + "=" * 50)

if __name__ == "__main__":
    main() 