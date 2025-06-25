#!/usr/bin/env python3
"""
专门删除C06AUSCKYKF频道消息
尝试多种方法删除消息
"""

import time
import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config import Config

def try_delete_with_pagination():
    """尝试使用分页方式获取和删除消息"""
    client = WebClient(token=Config.SLACK_BOT_TOKEN)
    channel_id = "C06AUSCKYKF"
    
    print("🗑️  尝试删除C06AUSCKYKF频道消息")
    print("=" * 50)
    
    # 获取Bot信息
    try:
        auth_response = client.auth_test()
        bot_user_id = auth_response['user_id']
        print(f"🤖 Bot用户ID: {bot_user_id}")
    except SlackApiError as e:
        print(f"❌ 获取Bot信息失败: {e.response['error']}")
        return
    
    total_deleted = 0
    page = 1
    
    try:
        # 尝试获取频道信息
        channel_info = client.conversations_info(channel=channel_id)
        print(f"📺 频道名称: {channel_info['channel']['name']}")
    except SlackApiError as e:
        print(f"⚠️  无法获取频道信息: {e.response['error']}")
    
    while True:
        print(f"\n📄 获取第 {page} 页消息...")
        
        try:
            # 获取频道历史消息
            response = client.conversations_history(
                channel=channel_id,
                limit=100
            )
            messages = response['messages']
            
            if not messages:
                print("📭 没有更多消息")
                break
            
            print(f"📝 找到 {len(messages)} 条消息")
            
            # 过滤出Bot发送的消息
            bot_messages = [msg for msg in messages if msg.get('user') == bot_user_id]
            
            if not bot_messages:
                print("📭 没有Bot发送的消息")
                break
            
            print(f"🤖 找到 {len(bot_messages)} 条Bot消息")
            
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
                
                time.sleep(0.1)
            
            print(f"✅ 第 {page} 页删除完成: 成功 {deleted_count} 条，失败 {failed_count} 条")
            
            # 检查是否还有更多消息
            if not response.get('has_more', False):
                print("📄 已到达最后一页")
                break
            
            page += 1
            
        except SlackApiError as e:
            print(f"❌ 获取第 {page} 页消息失败: {e.response['error']}")
            break
    
    print(f"\n🎉 总删除完成: {total_deleted} 条Bot消息")

def try_delete_by_search():
    """尝试通过搜索找到并删除消息"""
    client = WebClient(token=Config.SLACK_BOT_TOKEN)
    
    print("\n🔍 尝试通过搜索找到消息...")
    
    try:
        # 搜索Bot发送的消息
        response = client.search_messages(
            query=f"from:@me in:#C06AUSCKYKF",
            count=100
        )
        
        messages = response.get('messages', {}).get('matches', [])
        
        if not messages:
            print("📭 搜索没有找到消息")
            return
        
        print(f"🔍 搜索找到 {len(messages)} 条消息")
        
        deleted_count = 0
        failed_count = 0
        
        for i, message in enumerate(messages, 1):
            ts = message['ts']
            text = message.get('text', '')[:30] + '...' if len(message.get('text', '')) > 30 else message.get('text', '')
            
            print(f"   [{i}/{len(messages)}] 删除: {text}")
            
            try:
                client.chat_delete(channel="C06AUSCKYKF", ts=ts)
                deleted_count += 1
            except SlackApiError as e:
                if e.response['error'] == 'message_not_found':
                    print(f"     ⚠️  消息已不存在")
                    deleted_count += 1
                else:
                    print(f"     ❌ 删除失败: {e.response['error']}")
                    failed_count += 1
            
            time.sleep(0.1)
        
        print(f"✅ 搜索删除完成: 成功 {deleted_count} 条，失败 {failed_count} 条")
        
    except SlackApiError as e:
        print(f"❌ 搜索失败: {e.response['error']}")

def main():
    """主函数"""
    print("🗑️  C06AUSCKYKF频道消息删除工具")
    print("=" * 50)
    
    # 检查配置
    if not Config.SLACK_BOT_TOKEN:
        print("❌ 错误: 未设置SLACK_BOT_TOKEN")
        return
    
    # 方法1: 分页删除
    try_delete_with_pagination()
    
    # 方法2: 搜索删除
    try_delete_by_search()
    
    print("\n🎉 所有删除方法尝试完成！")

if __name__ == "__main__":
    main() 