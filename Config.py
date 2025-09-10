import json
import os
import platform
import sys
from dotenv import load_dotenv
from typing import List, Optional


class Config:
    def __init__(self, data: dict):
        # 加载环境变量
        load_dotenv()
        # 优先使用环境变量，如果不存在则使用配置文件
        self.token = os.getenv('TOKEN') or data.get('token', '')
        self.api_url = os.getenv('API_URL') or data.get('api_url', '')
        self.bot = os.getenv('IS_BOT', '').lower() == 'true' if os.getenv('IS_BOT') else data.get('is_bot', False)
        self.cqhttp_url = data['coolq_url'].rstrip('/')
        self.cqhttp_token = data['coolq_token']
        self.proxy = self._get_proxy(data.get('proxy'))
        print(f"代理配置结果: {self.proxy}")
        self.toast = data['toast']
        self.message_monitor = Config.MessageMonitor(data['message_monitor'])
        self.user_dynamic_monitor = Config.UserDynamicMonitor(data['user_dynamic_monitor'])
        self.push = Config.Push(data['push'])
        self.push_content = Config.PushContent(data['push_text'])

    def _get_proxy(self, proxy_data) -> str:
        """处理代理配置"""
        if not proxy_data:
            return ''
        
        # 打印调试信息
        print(f"处理代理配置: {proxy_data}")
        
        # 如果是字符串直接返回
        if isinstance(proxy_data, str):
            return proxy_data
        
        # 如果是字典，根据环境选择
        if isinstance(proxy_data, dict):
            is_docker = os.getenv('IS_DOCKER', 'false').lower() == 'true'
            env_type = 'docker' if is_docker else 'local'
            print(f"当前环境: {env_type}")
            
            # 尝试从环境变量获取代理设置
            if is_docker:
                env_proxy = os.getenv('HTTP_PROXY') or os.getenv('HTTPS_PROXY')
                if env_proxy:
                    print(f"使用环境变量代理: {env_proxy}")
                    return env_proxy
            
            # 从配置文件获取
            proxy_url = proxy_data.get(env_type, '')
            print(f"从配置文件获取代理: {proxy_url}")
            
            # 确保返回的是字符串
            if isinstance(proxy_url, dict):
                return ''
            return proxy_url
        
        return ''

    class MessageMonitor:
        def __init__(self, data: dict):
            self.users = data['user_id']
            # 优先使用环境变量中的channel配置
            env_channels = os.getenv('CHANNEL')
            if env_channels:
                self.channel_ids = [int(channel.strip()) for channel in env_channels.split(',') if channel.strip()]
            else:
                self.channel_ids = data.get('channel', [])
            self.channel_names = dict()
            for guilds in data['channel_name']:
                channels = self.channel_names.get(guilds[0])
                if channels is None:
                    channels = set()
                    self.channel_names[guilds[0]] = channels
                for i in range(1, len(guilds)):
                    channels.add(guilds[i])

    class UserDynamicMonitor:
        def __init__(self, data: dict):
            self.users = data['user_id']
            self.servers = set(data['server'])

    class Push:
        def __init__(self, data: dict):
            self.groups = data['QQ_group']
            self.users = data['QQ_user']

    class PushContent:
        def __init__(self, data: dict):
            self.categories = data["category"]
            self.message_format = data["message_format"]
            self.user_dynamic_format = data["user_dynamic_format"]
            self.replace = data["replace"]


def read_config() -> Config:
    config_path = 'config.json'
    try:
        with open(config_path, 'r', encoding='utf8') as f:
            data = json.load(f)
            return Config(data)
    except FileNotFoundError:
        print('配置文件不存在')
        sys.exit(1)
    except Exception:
        print('配置文件读取出错，请检查配置文件各参数是否正确')
        if platform.system() == 'Windows':
            os.system('pause')
        sys.exit(1)


config = read_config()
message_monitor = config.message_monitor
user_dynamic_monitor = config.user_dynamic_monitor
push = config.push
push_content = config.push_content
