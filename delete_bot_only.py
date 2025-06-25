#!/usr/bin/env python3
"""
只删除Bot发送的消息
直接尝试删除，不依赖读取频道历史
"""

import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config import Config

def delete_bot_messages_direct():
    """直接尝试删除Bot消息"""
    client = WebClient(token=Config.SLACK_BOT_TOKEN)
    channel_id = "C06AUSCKYKF"
    
    print("🗑️  删除Bot发送的消息")
    print("=" * 50)
    
    # 获取Bot信息
    try:
        auth_response = client.auth_test()
        bot_user_id = auth_response['user_id']
        print(f"🤖 Bot用户ID: {bot_user_id}")
    except SlackApiError as e:
        print(f"❌ 获取Bot信息失败: {e.response['error']}")
        return
    
    # 尝试一些可能的时间戳格式
    # 基于当前时间生成一些可能的时间戳
    current_time = time.time()
    
    # 生成最近几天的可能时间戳
    test_timestamps = []
    for days_ago in range(7):  # 最近7天
        for hour in range(24):  # 每天24小时
            timestamp = current_time - (days_ago * 24 * 3600) - (hour * 3600)
            test_timestamps.append(f"{timestamp:.6f}")
    
    print(f"🔍 尝试删除 {len(test_timestamps)} 个可能的时间戳...")
    
    deleted_count = 0
    not_found_count = 0
    failed_count = 0
    
    for i, ts in enumerate(test_timestamps, 1):
        if i % 100 == 0:
            print(f"   进度: {i}/{len(test_timestamps)}")
        
        try:
            client.chat_delete(channel=channel_id, ts=ts)
            deleted_count += 1
            print(f"   ✅ 成功删除消息: {ts}")
        except SlackApiError as e:
            if e.response['error'] == 'message_not_found':
                not_found_count += 1
            elif e.response['error'] == 'cant_delete_message':
                # 可能是权限问题或消息太旧
                not_found_count += 1
            else:
                failed_count += 1
                if failed_count <= 5:  # 只显示前5个错误
                    print(f"   ❌ 删除失败 {ts}: {e.response['error']}")
        
        # 添加延迟避免API限制
        time.sleep(0.05)
    
    print(f"\n📊 删除结果:")
    print(f"   ✅ 成功删除: {deleted_count} 条")
    print(f"   📭 消息不存在: {not_found_count} 条")
    print(f"   ❌ 删除失败: {failed_count} 条")

def try_delete_recent_messages():
    """尝试删除最近的消息"""
    client = WebClient(token=Config.SLACK_BOT_TOKEN)
    channel_id = "C06AUSCKYKF"
    
    print("\n🕐 尝试删除最近的消息...")
    
    # 获取当前时间
    current_time = time.time()
    
    # 尝试最近24小时内的消息
    for hours_ago in range(24):
        timestamp = current_time - (hours_ago * 3600)
        ts = f"{timestamp:.6f}"
        
        try:
            client.chat_delete(channel=channel_id, ts=ts)
            print(f"   ✅ 删除成功: {hours_ago} 小时前")
        except SlackApiError as e:
            if e.response['error'] != 'message_not_found':
                print(f"   ❌ {hours_ago} 小时前: {e.response['error']}")
        
        time.sleep(0.1)

def main():
    """主函数"""
    print("🗑️  Bot消息删除工具")
    print("=" * 50)
    
    # 检查配置
    if not Config.SLACK_BOT_TOKEN:
        print("❌ 错误: 未设置SLACK_BOT_TOKEN")
        return
    
    # 方法1: 直接尝试删除
    delete_bot_messages_direct()
    
    # 方法2: 尝试删除最近消息
    try_delete_recent_messages()
    
    print("\n🎉 删除尝试完成！")

if __name__ == "__main__":
    main() 