#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版wework渠道演示脚本
展示如何使用简化版wework渠道进行AI对话
"""

import sys
import os
import time
import threading
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from channel.wework_simple.wework_simple_channel import (
    WeworkSimpleChannel, 
    add_test_message
)

def demo_private_chat():
    """演示私聊功能"""
    print("=" * 60)
    print("演示：私聊功能")
    print("=" * 60)
    
    # 创建渠道实例
    channel = WeworkSimpleChannel()
    channel.startup()
    
    # 模拟私聊消息
    private_messages = [
        "你好，请介绍一下自己",
        "今天天气怎么样？",
        "请帮我写一首关于春天的诗",
        "什么是人工智能？"
    ]
    
    for i, message in enumerate(private_messages, 1):
        print(f"\n{i}. 用户发送私聊消息: {message}")
        
        # 添加消息到队列
        add_test_message(message, is_group=False)
        
        # 等待AI处理
        time.sleep(2)
        
        # 处理队列中的消息
        for msg in channel.message_queue:
            print(f"   AI处理消息: {msg.content}")
            channel.handle_single(msg)
        
        # 清理队列
        channel.message_queue.clear()
        time.sleep(1)
    
    channel.shutdown()
    print("\n私聊演示完成！")

def demo_group_chat():
    """演示群聊功能"""
    print("\n" + "=" * 60)
    print("演示：群聊功能")
    print("=" * 60)
    
    # 创建渠道实例
    channel = WeworkSimpleChannel()
    channel.startup()
    
    # 模拟群聊消息
    group_messages = [
        "@bot 你好，这是群聊消息",
        "@bot 请介绍一下这个群的功能",
        "@bot 帮我总结一下今天的会议内容",
        "bot 这个机器人真不错"
    ]
    
    for i, message in enumerate(group_messages, 1):
        print(f"\n{i}. 用户发送群聊消息: {message}")
        
        # 添加消息到队列
        add_test_message(message, is_group=True)
        
        # 等待AI处理
        time.sleep(2)
        
        # 处理队列中的消息
        for msg in channel.message_queue:
            print(f"   AI处理群聊消息: {msg.content}")
            channel.handle_group(msg)
        
        # 清理队列
        channel.message_queue.clear()
        time.sleep(1)
    
    channel.shutdown()
    print("\n群聊演示完成！")

def demo_message_types():
    """演示不同消息类型"""
    print("\n" + "=" * 60)
    print("演示：不同消息类型")
    print("=" * 60)
    
    # 创建渠道实例
    channel = WeworkSimpleChannel()
    channel.startup()
    
    # 模拟不同类型的消息
    message_types = [
        {
            'type': 'text',
            'content': '这是一条文本消息',
            'description': '文本消息'
        },
        {
            'type': 'image',
            'content': 'https://example.com/image.jpg',
            'description': '图片消息'
        },
        {
            'type': 'voice',
            'content': 'https://example.com/voice.mp3',
            'description': '语音消息'
        }
    ]
    
    for i, msg_data in enumerate(message_types, 1):
        print(f"\n{i}. 用户发送{msg_data['description']}: {msg_data['content']}")
        
        # 创建消息数据
        message_data = {
            'msgid': f'msg_{i}',
            'create_time': int(time.time()),
            'msgtype': msg_data['type'],
            'fromuser': 'test_user',
            'fromuser_name': '测试用户',
            'touser': channel.user_id,
            'touser_name': channel.name,
            'actual_user_id': 'test_user',
            'actual_user_name': '测试用户'
        }
        
        # 根据消息类型设置内容
        if msg_data['type'] == 'text':
            message_data['text'] = {'content': msg_data['content']}
        elif msg_data['type'] == 'image':
            message_data['image'] = {'url': msg_data['content']}
        elif msg_data['type'] == 'voice':
            message_data['voice'] = {'url': msg_data['content']}
        
        # 添加消息到队列
        channel.add_message(message_data, is_group=False)
        
        # 等待AI处理
        time.sleep(2)
        
        # 处理队列中的消息
        for msg in channel.message_queue:
            print(f"   AI处理{msg_data['description']}: {msg.content}")
            channel.handle_single(msg)
        
        # 清理队列
        channel.message_queue.clear()
        time.sleep(1)
    
    channel.shutdown()
    print("\n消息类型演示完成！")

def demo_configuration():
    """演示配置功能"""
    print("\n" + "=" * 60)
    print("演示：配置功能")
    print("=" * 60)
    
    # 读取配置文件
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("当前配置:")
        print(f"  渠道类型: {config.get('channel_type', 'unknown')}")
        print(f"  AI模型: {config.get('model', 'unknown')}")
        print(f"  私聊前缀: {config.get('single_chat_prefix', [])}")
        print(f"  群聊前缀: {config.get('group_chat_prefix', [])}")
        print(f"  语音识别: {config.get('speech_recognition', False)}")
        print(f"  对话最大token: {config.get('conversation_max_tokens', 0)}")
        print(f"  角色描述: {config.get('character_desc', '')[:50]}...")
        
    except Exception as e:
        print(f"读取配置文件失败: {e}")
    
    print("\n配置演示完成！")

def main():
    """主函数"""
    print("简化版wework渠道演示")
    print("=" * 60)
    print("这个演示展示了如何使用简化版wework渠道进行AI对话")
    print("特点：")
    print("  ✅ 不依赖ntwork库")
    print("  ✅ 支持私聊和群聊")
    print("  ✅ 支持多种消息类型")
    print("  ✅ 易于扩展和定制")
    print("  ✅ 与AI大模型完美集成")
    print("=" * 60)
    
    try:
        # 演示私聊功能
        demo_private_chat()
        
        # 演示群聊功能
        demo_group_chat()
        
        # 演示不同消息类型
        demo_message_types()
        
        # 演示配置功能
        demo_configuration()
        
        print("\n" + "=" * 60)
        print("所有演示完成！")
        print("=" * 60)
        print("使用说明：")
        print("1. 修改 config.json 中的 channel_type 为 'wework'")
        print("2. 运行 python3 app.py 启动项目")
        print("3. 使用 add_test_message() 函数添加测试消息")
        print("4. 消息会自动发送给AI处理并返回回复")
        print("=" * 60)
        
    except Exception as e:
        print(f"演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
