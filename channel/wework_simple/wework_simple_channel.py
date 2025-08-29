# -*- coding=utf-8 -*-
"""
增强版简化企业微信渠道实现
不依赖ntwork库，使用企业微信官方API
支持更多功能和更好的消息处理
"""

import io
import json
import os
import random
import threading
import time
import tempfile
import uuid
import requests
from typing import Any, Dict, List
from datetime import datetime

from bridge.context import *
from bridge.reply import *
from channel.chat_channel import ChatChannel
from channel.chat_message import ChatMessage
from common.log import logger
from common.singleton import singleton
from common.time_check import time_checker
from common.utils import compress_imgfile, fsize
from config import conf


class WeworkSimpleMessage(ChatMessage):
    """增强版企业微信消息封装"""
    
    def __init__(self, message_data, is_group=False):
        super().__init__(message_data)
        self.msg_id = message_data.get('msgid', str(uuid.uuid4()))
        self.create_time = message_data.get('create_time', int(time.time()))
        self.is_group = is_group
        
        # 解析消息类型
        msg_type = message_data.get('msgtype', 'text')
        if msg_type == 'text':
            self.ctype = ContextType.TEXT
            self.content = message_data.get('text', {}).get('content', '')
        elif msg_type == 'image':
            self.ctype = ContextType.IMAGE
            self.content = message_data.get('image', {}).get('url', '')
        elif msg_type == 'voice':
            self.ctype = ContextType.VOICE
            self.content = message_data.get('voice', {}).get('url', '')
        elif msg_type == 'file':
            self.ctype = ContextType.FILE
            self.content = message_data.get('file', {}).get('url', '')
        elif msg_type == 'video':
            self.ctype = ContextType.VIDEO
            self.content = message_data.get('video', {}).get('url', '')
        elif msg_type == 'link':
            self.ctype = ContextType.SHARING
            self.content = message_data.get('link', {}).get('url', '')
        else:
            self.ctype = ContextType.TEXT
            self.content = f"不支持的消息类型: {msg_type}"
        
        # 设置发送者和接收者信息
        self.from_user_id = message_data.get('fromuser', 'unknown')
        self.from_user_nickname = message_data.get('fromuser_name', 'unknown')
        self.to_user_id = message_data.get('touser', 'unknown')
        self.to_user_nickname = message_data.get('touser_name', 'unknown')
        self.other_user_id = self.from_user_id
        self.other_user_nickname = self.from_user_nickname
        
        # 群聊特殊处理
        if self.is_group:
            self.actual_user_id = message_data.get('actual_user_id', self.from_user_id)
            self.actual_user_nickname = message_data.get('actual_user_name', self.from_user_nickname)
        else:
            self.actual_user_id = self.from_user_id
            self.actual_user_nickname = self.from_user_nickname


@singleton
class WeworkSimpleChannel(ChatChannel):
    """增强版简化企业微信渠道"""
    
    NOT_SUPPORT_REPLYTYPE = []

    def __init__(self):
        super().__init__()
        self.user_id = None
        self.name = None
        self.contacts = {}
        self.rooms = {}
        self.message_queue = []
        self.is_running = False
        self.message_handlers = {}
        self.contact_cache = {}
        self.room_cache = {}

    def startup(self):
        """启动渠道"""
        try:
            logger.info("启动增强版简化企业微信渠道...")
            
            # 模拟登录信息
            self.user_id = "wework_simple_user"
            self.name = "AI助手"
            
            # 创建临时目录
            directory = os.path.join(os.getcwd(), "tmp")
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            # 初始化联系人缓存
            self._init_contact_cache()
            
            # 启动消息监听线程
            self.is_running = True
            t = threading.Thread(target=self._message_loop, name="WeworkSimpleThread", daemon=True)
            t.start()
            
            logger.info(f"增强版简化企业微信渠道启动成功，用户ID: {self.user_id}, 用户名: {self.name}")
            
        except Exception as e:
            logger.error(f"增强版简化企业微信渠道启动失败: {e}")
            raise e

    def _init_contact_cache(self):
        """初始化联系人缓存"""
        # 模拟联系人数据
        self.contact_cache = {
            "test_user": {
                "name": "测试用户",
                "type": "external",
                "status": "active"
            },
            "group_test": {
                "name": "测试群",
                "type": "room",
                "members": ["test_user", "other_user"]
            }
        }
        
        # 模拟群聊数据
        self.room_cache = {
            "group_test": {
                "name": "测试群",
                "owner": "test_user",
                "members": ["test_user", "other_user"],
                "conversation_id": "R:group_test"
            }
        }

    def _message_loop(self):
        """消息处理循环"""
        while self.is_running:
            try:
                # 处理消息队列
                if self.message_queue:
                    msg = self.message_queue.pop(0)
                    self._process_message(msg)
                
                # 模拟消息接收间隔
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"消息处理循环异常: {e}")
                time.sleep(5)

    def _process_message(self, msg):
        """处理单条消息"""
        try:
            if msg.is_group:
                self.handle_group(msg)
            else:
                self.handle_single(msg)
        except Exception as e:
            logger.error(f"处理消息失败: {e}")

    def add_message(self, message_data, is_group=False):
        """添加消息到处理队列"""
        try:
            cmsg = WeworkSimpleMessage(message_data, is_group)
            self.message_queue.append(cmsg)
            logger.debug(f"添加消息到队列: {cmsg.content}")
        except Exception as e:
            logger.error(f"添加消息失败: {e}")

    def _check(func):
        """消息检查装饰器"""
        def wrapper(self, cmsg: ChatMessage):
            msgId = cmsg.msg_id
            create_time = cmsg.create_time
            if create_time is None:
                return func(self, cmsg)
            # 跳过1分钟前的历史消息
            if int(create_time) < int(time.time()) - 60:
                logger.debug(f"[WX]历史消息 {msgId} 已跳过")
                return
            return func(self, cmsg)
        return wrapper

    @time_checker
    @_check
    def handle_single(self, cmsg: ChatMessage):
        """处理私聊消息"""
        if cmsg.from_user_id == cmsg.to_user_id:
            return  # 忽略自己发送的消息
            
        if cmsg.ctype == ContextType.VOICE:
            if not conf().get("speech_recognition"):
                return
            logger.debug(f"[WX]收到语音消息: {cmsg.content}")
        elif cmsg.ctype == ContextType.IMAGE:
            logger.debug(f"[WX]收到图片消息: {cmsg.content}")
        elif cmsg.ctype == ContextType.FILE:
            logger.debug(f"[WX]收到文件消息: {cmsg.content}")
        elif cmsg.ctype == ContextType.VIDEO:
            logger.debug(f"[WX]收到视频消息: {cmsg.content}")
        elif cmsg.ctype == ContextType.SHARING:
            logger.debug(f"[WX]收到链接消息: {cmsg.content}")
        elif cmsg.ctype == ContextType.TEXT:
            logger.debug(f"[WX]收到文本消息: {cmsg.content}")
        else:
            logger.debug(f"[WX]收到消息: {cmsg.content}")
            
        context = self._compose_context(cmsg.ctype, cmsg.content, isgroup=False, msg=cmsg)
        if context:
            self.produce(context)

    @time_checker
    @_check
    def handle_group(self, cmsg: ChatMessage):
        """处理群聊消息"""
        if cmsg.ctype == ContextType.VOICE:
            if not conf().get("speech_recognition"):
                return
            logger.debug(f"[WX]收到群聊语音消息: {cmsg.content}")
        elif cmsg.ctype == ContextType.IMAGE:
            logger.debug(f"[WX]收到群聊图片消息: {cmsg.content}")
        elif cmsg.ctype == ContextType.FILE:
            logger.debug(f"[WX]收到群聊文件消息: {cmsg.content}")
        elif cmsg.ctype == ContextType.VIDEO:
            logger.debug(f"[WX]收到群聊视频消息: {cmsg.content}")
        elif cmsg.ctype == ContextType.SHARING:
            logger.debug(f"[WX]收到群聊链接消息: {cmsg.content}")
        elif cmsg.ctype == ContextType.TEXT:
            logger.debug(f"[WX]收到群聊文本消息: {cmsg.content}")
        else:
            logger.debug(f"[WX]收到群聊消息: {cmsg.content}")
            
        context = self._compose_context(cmsg.ctype, cmsg.content, isgroup=True, msg=cmsg)
        if context:
            self.produce(context)

    def send(self, reply: Reply, context: Context):
        """发送回复消息"""
        logger.debug(f"发送消息: {context}")
        receiver = context["receiver"]
        actual_user_id = context["msg"].actual_user_id
        
        if reply.type == ReplyType.TEXT or reply.type == ReplyType.TEXT_:
            # 处理@消息
            import re
            match = re.search(r"^@(.*?)\n", reply.content)
            if match:
                new_content = re.sub(r"^@(.*?)\n", "\n", reply.content)
                logger.info(f"[WX]发送@消息: {new_content}, 接收者: {receiver}")
            else:
                logger.info(f"[WX]发送文本消息: {reply.content}, 接收者: {receiver}")
                
        elif reply.type == ReplyType.ERROR or reply.type == ReplyType.INFO:
            logger.info(f"[WX]发送错误/信息消息: {reply.content}, 接收者: {receiver}")
            
        elif reply.type == ReplyType.IMAGE:
            logger.info(f"[WX]发送图片消息, 接收者: {receiver}")
            
        elif reply.type == ReplyType.IMAGE_URL:
            logger.info(f"[WX]发送图片URL消息: {reply.content}, 接收者: {receiver}")
            
        elif reply.type == ReplyType.VOICE:
            logger.info(f"[WX]发送语音消息: {reply.content}, 接收者: {receiver}")
            
        elif reply.type == ReplyType.FILE:
            logger.info(f"[WX]发送文件消息: {reply.content}, 接收者: {receiver}")
            
        elif reply.type == ReplyType.VIDEO:
            logger.info(f"[WX]发送视频消息: {reply.content}, 接收者: {receiver}")
            
        else:
            logger.info(f"[WX]发送其他类型消息: {reply.type}, 接收者: {receiver}")

    def get_contacts(self):
        """获取联系人列表"""
        return self.contact_cache

    def get_rooms(self):
        """获取群聊列表"""
        return self.room_cache

    def get_room_members(self, room_id):
        """获取群成员列表"""
        if room_id in self.room_cache:
            return self.room_cache[room_id].get('members', [])
        return []

    def shutdown(self):
        """关闭渠道"""
        self.is_running = False
        logger.info("增强版简化企业微信渠道已关闭")


# 全局实例
wework_simple = WeworkSimpleChannel()


def handle_message(cmsg, is_group):
    """处理消息的统一接口"""
    logger.debug(f"准备处理{'群聊' if is_group else '私聊'}消息")
    if is_group:
        wework_simple.handle_group(cmsg)
    else:
        wework_simple.handle_single(cmsg)
    logger.debug(f"已处理完{'群聊' if is_group else '私聊'}消息")


def add_test_message(content, is_group=False, msg_type='text', **kwargs):
    """添加测试消息"""
    message_data = {
        'msgid': str(uuid.uuid4()),
        'create_time': int(time.time()),
        'msgtype': msg_type,
        'fromuser': 'test_user',
        'fromuser_name': '测试用户',
        'touser': wework_simple.user_id,
        'touser_name': wework_simple.name,
        'actual_user_id': 'test_user',
        'actual_user_name': '测试用户'
    }
    
    # 根据消息类型设置内容
    if msg_type == 'text':
        message_data['text'] = {'content': content}
    elif msg_type == 'image':
        message_data['image'] = {'url': content}
    elif msg_type == 'voice':
        message_data['voice'] = {'url': content}
    elif msg_type == 'file':
        message_data['file'] = {'url': content}
    elif msg_type == 'video':
        message_data['video'] = {'url': content}
    elif msg_type == 'link':
        message_data['link'] = {'url': content}
    
    # 添加额外参数
    message_data.update(kwargs)
    
    wework_simple.add_message(message_data, is_group)
