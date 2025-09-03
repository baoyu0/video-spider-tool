#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件
包含爬虫的各种配置参数
"""

import os
from typing import Dict, List


class Config:
    """配置类"""
    
    # 基础配置
    BASE_URL = "https://metaso.cn"
    
    # 目录配置
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(PROJECT_ROOT, "data")
    LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
    
    # 日志配置
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = os.path.join(LOGS_DIR, "metaso_spider.log")
    
    # 请求配置
    REQUEST_TIMEOUT = 30
    DOWNLOAD_TIMEOUT = 60
    REQUEST_DELAY = 1  # 请求间隔（秒）
    MAX_RETRIES = 3
    
    # 用户代理
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    
    # 请求头
    DEFAULT_HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none'
    }
    
    # 文件类型配置
    SUPPORTED_FILE_TYPES = {
        'pptx': 'PowerPoint演示文稿',
        'ppt': 'PowerPoint演示文稿',
        'pdf': 'PDF文档',
        'doc': 'Word文档',
        'docx': 'Word文档',
        'xls': 'Excel表格',
        'xlsx': 'Excel表格',
        'txt': '文本文件',
        'md': 'Markdown文档'
    }
    
    # 图片类型
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
    
    # 下载配置
    CHUNK_SIZE = 8192  # 下载块大小
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 最大文件大小 100MB
    
    # 秘塔AI搜索特定配置
    METASO_CONFIG = {
        'api_base': '/api/file',
        'preview_path': '/preview',
        'download_path': '/download',
        'bookshelf_path': '/bookshelf'
    }
    
    # 爬取规则
    CRAWL_RULES = {
        'respect_robots_txt': True,
        'download_images': True,
        'download_original_file': True,
        'save_metadata': True,
        'create_info_file': True
    }
    
    @classmethod
    def get_user_agent(cls) -> str:
        """随机获取一个用户代理"""
        import random
        return random.choice(cls.USER_AGENTS)
    
    @classmethod
    def ensure_directories(cls) -> None:
        """确保必要的目录存在"""
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.LOGS_DIR, exist_ok=True)
    
    @classmethod
    def get_file_type_description(cls, file_type: str) -> str:
        """获取文件类型描述"""
        return cls.SUPPORTED_FILE_TYPES.get(file_type.lower(), '未知文件类型')


# 开发环境配置
class DevelopmentConfig(Config):
    """开发环境配置"""
    LOG_LEVEL = "DEBUG"
    REQUEST_DELAY = 0.5


# 生产环境配置
class ProductionConfig(Config):
    """生产环境配置"""
    LOG_LEVEL = "INFO"
    REQUEST_DELAY = 2
    MAX_RETRIES = 5


# 根据环境变量选择配置
ENVIRONMENT = os.getenv('SPIDER_ENV', 'development')

if ENVIRONMENT == 'production':
    config = ProductionConfig()
else:
    config = DevelopmentConfig()