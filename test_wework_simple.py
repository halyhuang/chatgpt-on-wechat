#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试简化版wework渠道
"""

import sys
import os
import time
import threading

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from channel.wework_simple.wework_simple_channel import (
    WeworkSimpleChannel, 
    add_test_message, 
    handle_message
)

def test_wework_simple():
    """测试简化版wework渠道"""
    print("开始测试简化版wework渠道...")
    
    try:
        # 创建渠道实例
        channel = WeworkSimpleChannel()
        
        # 启动渠道
        channel.startup()
        
        print("渠道启动成功！")
        print(f"用户ID: {channel.user_id}")
        print(f"用户名: {channel.name}")
        
        # 等待一下让渠道完全启动
        time.sleep(2)
        
        # 测试添加私聊消息
        print("\n测试私聊消息...")
        add_test_message("你好，这是测试消息", is_group=False)
        
        # 测试添加群聊消息
        print("测试群聊消息...")
        add_test_message("@bot 你好，这是群聊测试消息", is_group=True)
        
        # 等待消息处理
        time.sleep(3)
        
        # 检查消息队列
        print(f"\n消息队列长度: {len(channel.message_queue)}")
        
        # 处理队列中的消息
        for msg in channel.message_queue:
            print(f"处理消息: {msg.content}")
            handle_message(msg, msg.is_group)
        
        # 清理队列
        channel.message_queue.clear()
        
        print("\n测试完成！")
        
        # 关闭渠道
        channel.shutdown()
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_with_ai():
    """测试与AI的集成"""
    print("\n开始测试与AI的集成...")
    
    try:
        # 导入必要的模块
        from bridge.context import Context
        from bridge.reply import Reply, ReplyType
        
        # 创建渠道实例
        channel = WeworkSimpleChannel()
        channel.startup()
        
        # 创建测试消息
        message_data = {
            'msgid': 'test_msg_001',
            'create_time': int(time.time()),
            'msgtype': 'text',
            'text': {'content': '你好，请介绍一下自己'},
            'fromuser': 'test_user',
            'fromuser_name': '测试用户',
            'touser': channel.user_id,
            'touser_name': channel.name,
            'actual_user_id': 'test_user',
            'actual_user_name': '测试用户'
        }
        
        # 添加消息
        channel.add_message(message_data, is_group=False)
        
        # 处理消息
        for msg in channel.message_queue:
            print(f"处理AI消息: {msg.content}")
            # 这里会触发AI处理
            channel.handle_single(msg)
        
        # 清理
        channel.message_queue.clear()
        channel.shutdown()
        
        print("AI集成测试完成！")
        
    except Exception as e:
        print(f"AI集成测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 50)
    print("简化版wework渠道测试")
    print("=" * 50)
    
    # 基础功能测试
    test_wework_simple()
    
    # AI集成测试
    test_with_ai()
    
    print("\n所有测试完成！")
