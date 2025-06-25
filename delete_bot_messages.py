#!/usr/bin/env python3
"""
删除Bot自己发送的消息
避免权限问题，只删除Bot发送的消息
"""

import time
import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config import Config

def delete_bot_messages():
    """删除Bot自己发送的消息"""
    client = WebClient(token=Config.SLACK_BOT_TOKEN)
    
    print("🗑️  删除Bot自己发送的消息")
    print("=" * 50)
    
    # 获取Bot信息
    try:
        auth_response = client.auth_test()
        bot_user_id = auth_response['user_id']
        print(f"🤖 Bot用户ID: {bot_user_id}")
    except SlackApiError as e:
        print(f"❌ 获取Bot信息失败: {e.response['error']}")
        return
    
    # 包含所有相关频道
    channels = [
        (Config.SLACK_CHANNEL_A, "频道A"),
        (Config.SLACK_CHANNEL_B, "频道B"),
        ("C06AUSCKYKF", "C06AUSCKYKF")  # 添加实际使用的频道
    ]
    
    total_deleted = 0
    
    for channel_id, channel_name in channels:
        print(f"\n📺 处理 {channel_name} ({channel_id})...")
        
        try:
            # 获取频道历史消息
            response = client.conversations_history(
                channel=channel_id,
                limit=1000
            )
            messages = response['messages']
            
            if not messages:
                print(f"   📭 没有消息")
                continue
            
            print(f"   📝 找到 {len(messages)} 条消息")
            
            # 过滤出Bot发送的消息
            bot_messages = [msg for msg in messages if msg.get('user') == bot_user_id]
            
            if not bot_messages:
                print(f"   📭 没有Bot发送的消息")
                continue
            
            print(f"   🤖 找到 {len(bot_messages)} 条Bot消息")
            
            deleted_count = 0
            failed_count = 0
            
            for i, message in enumerate(bot_messages, 1):
                ts = message['ts']
                text = message.get('text', '')[:30] + '...' if len(message.get('text', '')) > 30 else message.get('text', '')
                
                print(f"   [{i}/{len(bot_messages)}] 删除: {text}")
                
                try:
                    client.chat_delete(channel=channel_id, ts=ts)
                    deleted_count += 1
                    total_deleted += 1
                except SlackApiError as e:
                    if e.response['error'] == 'message_not_found':
                        print(f"     ⚠️  消息已不存在")
                        deleted_count += 1
                        total_deleted += 1
                    elif e.response['error'] == 'cant_delete_message':
                        print(f"     ❌ 无法删除: 权限不足或消息太旧")
                        failed_count += 1
                    else:
                        print(f"     ❌ 删除失败: {e.response['error']}")
                        failed_count += 1
                
                # 添加延迟避免API限制
                time.sleep(0.1)
            
            print(f"   ✅ {channel_name} 删除完成: 成功 {deleted_count} 条，失败 {failed_count} 条")
            
        except SlackApiError as e:
            print(f"   ❌ 获取 {channel_name} 历史消息失败: {e.response['error']}")
    
    print(f"\n🎉 总删除完成: {total_deleted} 条Bot消息")

def delete_pending_deletes():
    """删除pending_deletes.json中记录的消息"""
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
    
    client = WebClient(token=Config.SLACK_BOT_TOKEN)
    
    print(f"🗑️  删除 {len(data)} 条待删除消息...")
    
    deleted_count = 0
    failed_count = 0
    
    for i, record in enumerate(data, 1):
        channel = record['channel']
        ts = record['ts']
        
        print(f"   [{i}/{len(data)}] 删除消息 {ts}")
        
        try:
            client.chat_delete(channel=channel, ts=ts)
            deleted_count += 1
        except SlackApiError as e:
            if e.response['error'] == 'message_not_found':
                print(f"     ⚠️  消息已不存在")
                deleted_count += 1
            else:
                print(f"     ❌ 删除失败: {e.response['error']}")
                failed_count += 1
        
        time.sleep(0.1)
    
    # 清空pending_deletes.json文件
    with open(file, 'w') as f:
        json.dump([], f)
    
    print(f"✅ 删除完成: 成功 {deleted_count} 条，失败 {failed_count} 条")
    print("📝 已清空 pending_deletes.json 文件")

def main():
    """主函数"""
    print("🗑️  Bot消息删除工具")
    print("=" * 50)
    
    # 检查配置
    if not Config.SLACK_BOT_TOKEN:
        print("❌ 错误: 未设置SLACK_BOT_TOKEN")
        return
    
    if not Config.SLACK_CHANNEL_A or not Config.SLACK_CHANNEL_B:
        print("❌ 错误: 未设置Slack频道ID")
        return
    
    # 删除Bot消息
    delete_bot_messages()
    
    print("\n" + "=" * 50)
    
    # 删除pending_deletes.json中的消息
    delete_pending_deletes()
    
    print("\n🎉 所有删除任务完成！")

if __name__ == "__main__":
    main() 