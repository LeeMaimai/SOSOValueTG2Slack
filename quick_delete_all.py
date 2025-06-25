#!/usr/bin/env python3
"""
快速删除Slack频道所有消息
简化版本，直接删除所有消息
"""

import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config import Config

def delete_all_messages_in_channel(channel_id, channel_name):
    """删除频道中的所有消息"""
    client = WebClient(token=Config.SLACK_BOT_TOKEN)
    
    print(f"🗑️  开始删除 {channel_name} 中的所有消息...")
    
    try:
        # 获取频道历史消息
        response = client.conversations_history(channel=channel_id, limit=1000)
        messages = response['messages']
        
        if not messages:
            print(f"📭 {channel_name} 中没有消息")
            return
        
        print(f"📝 找到 {len(messages)} 条消息")
        
        deleted_count = 0
        failed_count = 0
        
        for i, message in enumerate(messages, 1):
            ts = message['ts']
            user = message.get('user', 'unknown')
            text = message.get('text', '')[:30] + '...' if len(message.get('text', '')) > 30 else message.get('text', '')
            
            print(f"   [{i}/{len(messages)}] 删除: {text}")
            
            try:
                client.chat_delete(channel=channel_id, ts=ts)
                deleted_count += 1
            except SlackApiError as e:
                if e.response['error'] == 'message_not_found':
                    print(f"     ⚠️  消息已不存在")
                    deleted_count += 1
                elif e.response['error'] == 'cant_delete_message':
                    print(f"     ❌ 无法删除: 权限不足或消息太旧")
                    failed_count += 1
                else:
                    print(f"     ❌ 删除失败: {e.response['error']}")
                    failed_count += 1
            
            # 添加延迟避免API限制
            time.sleep(0.1)
        
        print(f"✅ {channel_name} 删除完成: 成功 {deleted_count} 条，失败 {failed_count} 条")
        
    except SlackApiError as e:
        print(f"❌ 获取 {channel_name} 历史消息失败: {e.response['error']}")

def main():
    """主函数"""
    print("🗑️  快速删除Slack频道所有消息")
    print("=" * 50)
    
    # 检查配置
    if not Config.SLACK_BOT_TOKEN:
        print("❌ 错误: 未设置SLACK_BOT_TOKEN")
        return
    
    if not Config.SLACK_CHANNEL_A or not Config.SLACK_CHANNEL_B:
        print("❌ 错误: 未设置Slack频道ID")
        return
    
    print(f"📊 频道信息:")
    print(f"   频道A: {Config.SLACK_CHANNEL_A}")
    print(f"   频道B: {Config.SLACK_CHANNEL_B}")
    print()
    
    # 删除频道A的消息
    delete_all_messages_in_channel(Config.SLACK_CHANNEL_A, "频道A")
    print()
    
    # 删除频道B的消息
    delete_all_messages_in_channel(Config.SLACK_CHANNEL_B, "频道B")
    print()
    
    print("🎉 所有频道消息删除完成！")

if __name__ == "__main__":
    main() 