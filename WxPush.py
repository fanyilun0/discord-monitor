#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys
import os
import aiohttp
from Config import config

headers = {'Content-Type': 'application/json;charset=utf-8'}

async def send_weixin_message(text):
    json_text = {
        "msgtype": "text",
        "text": {
            "content": text,
        }
    }
    try:
        # 打印调试信息
        print(f"正在发送消息到: {config.api_url}")
        is_docker = os.getenv('IS_DOCKER', 'false').lower() == 'true'
        print(f"当前环境: {'Docker' if is_docker else '本地'}")
        
        # 在Docker环境中使用正确的代理
        proxies = {}
        if config.proxy:
            proxies = {
                "http": config.proxy,
                "https": config.proxy
            }
            print(f"使用代理: {proxies}")
        
        # 发送请求并记录详细信息
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(config.api_url, json=json_text, headers=headers, proxy=config.proxy if config.proxy else None, timeout=10) as response:
                print(f"请求状态: {response.status}")
                response_text = await response.text()
                
                if response.status != 200:
                    print(f"消息发送失败: {response.status} - {response_text}")
                    from Log import add_log
                    add_log(2, 'WxPush', f"消息发送失败: {response.status} - {response_text}")
                else:
                    print("消息发送成功")
                    from Log import add_log
                    add_log(0, 'WxPush', "消息发送成功")
                return response_text
    except Exception as e:
        error_msg = f"发送消息异常: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        from Log import add_log
        add_log(2, 'WxPush', error_msg)
        return None


def send_weixin_message_sync(text):
    """同步版本的微信消息发送函数，用于非异步环境"""
    import requests
    json_text = {
        "msgtype": "text",
        "text": {
            "content": text,
        }
    }
    try:
        # 打印调试信息
        print(f"正在发送消息到: {config.api_url}")
        is_docker = os.getenv('IS_DOCKER', 'false').lower() == 'true'
        print(f"当前环境: {'Docker' if is_docker else '本地'}")
        
        # 在Docker环境中使用正确的代理
        proxies = {}
        if config.proxy:
            proxies = {
                "http": config.proxy,
                "https": config.proxy
            }
            print(f"使用代理: {proxies}")
        
        # 发送请求并记录详细信息
        response = requests.post(config.api_url, json=json_text, headers=headers, proxies=proxies, timeout=10)
        print(f"请求状态: {response.status_code}")
        
        if response.status_code != 200:
            print(f"消息发送失败: {response.status_code} - {response.text}")
            from Log import add_log
            add_log(2, 'WxPush', f"消息发送失败: {response.status_code} - {response.text}")
        else:
            print("消息发送成功")
            from Log import add_log
            add_log(0, 'WxPush', "消息发送成功")
        return response.content
    except Exception as e:
        error_msg = f"发送消息异常: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        from Log import add_log
        add_log(2, 'WxPush', error_msg)
        return None
