# -*- coding: utf-8 -*-
# Desc: 从文件中加载配置
# former: MainFest/utils.py
from datetime import datetime
import toml
from hashlib import new as hashlib_new
from os.path import exists

def FindHash(file_path:str,sha:str = 'sha256') -> str:
    """
    计算文件的哈希值
    :param file_path: 文件路径
    :param sha: 哈希算法名称
    :return: 哈希值字符串
    """
    if exists(file_path):
        h = hashlib_new('sha256')
        with open(file_path,'rb') as f:
            while b := f.read(8192):
                h.update(b)
        return '{}:{}'.format(sha,h.hexdigest())
    else:
        print(file_path, '没找到文件')

def TimeStamp() -> str:
    """
    返回当前时间的时间戳
    :return: 当前时间的字符串表示
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


CONFIG_PATH = "config/config.toml"

class ConfigLoader:
    """
    配置加载器类，用于加载和访问配置文件中的配置项
    """
    def __init__(self, config_path) -> None:
        """
        初始化配置加载器
        :param config_path: 配置文件路径
        """
        self.config_path = config_path

    def load_config(self) -> dict:
        """
        加载配置文件
        :return: 配置文件内容的字典表示
        """
        with open(self.config_path, 'r', encoding='utf-8') as file:
            return toml.load(file)

    def __getattr__(self, name) -> str:
        """
        动态访问配置项，每次访问属性时都会重新加载配置文件
        :param name: 配置项名称
        :return: 配置项的值
        """
        config = self.load_config()
        if name in config:
            return config[name]
        raise AttributeError(f"'ConfigLoader' object has no attribute '{name}'")

CONFIG = ConfigLoader(CONFIG_PATH)
"""
基础配置对象，用于访问配置文件中的配置项
"""