#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频爬虫工具
用于爬取和下载网页中的视频资源
"""

import os
import re
import time
import logging
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from typing import List, Dict, Optional


class VideoSpider:
    """视频爬虫类"""
    
    def __init__(self, download_dir: str = "../data", log_level: str = "INFO"):
        """
        初始化爬虫
        
        Args:
            download_dir: 下载目录
            log_level: 日志级别
        """
        self.download_dir = download_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 设置日志
        self.logger = self._setup_logger(log_level)
        
        # 创建下载目录
        os.makedirs(download_dir, exist_ok=True)
        
        # 支持的视频格式
        self.video_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv']
        
    def _setup_logger(self, log_level: str) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger('VideoSpider')
        logger.setLevel(getattr(logging, log_level.upper()))
        
        # 创建文件处理器
        file_handler = logging.FileHandler('../logs/spider.log', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 创建格式器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """
        获取网页内容
        
        Args:
            url: 目标URL
            
        Returns:
            BeautifulSoup对象或None
        """
        try:
            self.logger.info(f"正在获取页面内容: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # 检测编码
            response.encoding = response.apparent_encoding
            
            soup = BeautifulSoup(response.text, 'html.parser')
            self.logger.info(f"成功获取页面内容: {url}")
            return soup
            
        except requests.RequestException as e:
            self.logger.error(f"获取页面内容失败 {url}: {e}")
            return None
    
    def extract_video_urls(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """
        从页面中提取视频URL
        
        Args:
            soup: BeautifulSoup对象
            base_url: 基础URL
            
        Returns:
            视频信息列表
        """
        video_urls = []
        
        # 查找video标签
        video_tags = soup.find_all('video')
        for video in video_tags:
            src = video.get('src')
            if src:
                full_url = urljoin(base_url, src)
                video_urls.append({
                    'url': full_url,
                    'title': video.get('title', ''),
                    'type': 'video_tag'
                })
            
            # 查找source标签
            sources = video.find_all('source')
            for source in sources:
                src = source.get('src')
                if src:
                    full_url = urljoin(base_url, src)
                    video_urls.append({
                        'url': full_url,
                        'title': video.get('title', ''),
                        'type': 'source_tag'
                    })
        
        # 查找链接中的视频文件
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            if any(href.lower().endswith(ext) for ext in self.video_extensions):
                full_url = urljoin(base_url, href)
                video_urls.append({
                    'url': full_url,
                    'title': link.get_text(strip=True),
                    'type': 'link'
                })
        
        # 使用正则表达式查找可能的视频URL
        text_content = str(soup)
        video_pattern = r'https?://[^\s"\'>]+\.(?:mp4|avi|mov|wmv|flv|webm|mkv)(?:\?[^\s"\'>]*)?'
        matches = re.findall(video_pattern, text_content, re.IGNORECASE)
        
        for match in matches:
            video_urls.append({
                'url': match,
                'title': '',
                'type': 'regex_match'
            })
        
        # 去重
        seen_urls = set()
        unique_videos = []
        for video in video_urls:
            if video['url'] not in seen_urls:
                seen_urls.add(video['url'])
                unique_videos.append(video)
        
        self.logger.info(f"找到 {len(unique_videos)} 个视频URL")
        return unique_videos
    
    def download_video(self, video_info: Dict[str, str]) -> bool:
        """
        下载视频文件
        
        Args:
            video_info: 视频信息字典
            
        Returns:
            下载是否成功
        """
        url = video_info['url']
        title = video_info.get('title', '')
        
        try:
            self.logger.info(f"开始下载视频: {url}")
            
            # 获取文件名
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            
            if not filename or '.' not in filename:
                # 如果无法从URL获取文件名，使用标题或时间戳
                if title:
                    filename = f"{title}.mp4"
                else:
                    filename = f"video_{int(time.time())}.mp4"
            
            # 清理文件名
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            filepath = os.path.join(self.download_dir, filename)
            
            # 检查文件是否已存在
            if os.path.exists(filepath):
                self.logger.info(f"文件已存在，跳过下载: {filename}")
                return True
            
            # 下载文件
            response = self.session.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # 显示下载进度
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            print(f"\r下载进度: {progress:.1f}%", end='', flush=True)
            
            print()  # 换行
            self.logger.info(f"视频下载完成: {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"下载视频失败 {url}: {e}")
            return False
    
    def crawl_videos(self, url: str) -> List[Dict[str, str]]:
        """
        爬取指定URL的视频
        
        Args:
            url: 目标URL
            
        Returns:
            成功下载的视频信息列表
        """
        self.logger.info(f"开始爬取视频: {url}")
        
        # 获取页面内容
        soup = self.get_page_content(url)
        if not soup:
            return []
        
        # 提取视频URL
        video_urls = self.extract_video_urls(soup, url)
        if not video_urls:
            self.logger.warning("未找到任何视频URL")
            return []
        
        # 下载视频
        downloaded_videos = []
        for video_info in video_urls:
            if self.download_video(video_info):
                downloaded_videos.append(video_info)
            
            # 添加延迟避免过于频繁的请求
            time.sleep(1)
        
        self.logger.info(f"爬取完成，成功下载 {len(downloaded_videos)} 个视频")
        return downloaded_videos


if __name__ == "__main__":
    # 示例使用
    spider = VideoSpider()
    
    # 测试URL（请替换为实际的视频页面URL）
    test_url = "https://example.com/videos"
    
    try:
        downloaded_videos = spider.crawl_videos(test_url)
        print(f"\n成功下载 {len(downloaded_videos)} 个视频:")
        for video in downloaded_videos:
            print(f"- {video['title'] or video['url']}")
    except KeyboardInterrupt:
        print("\n用户中断下载")
    except Exception as e:
        print(f"\n发生错误: {e}")