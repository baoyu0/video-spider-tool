#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级视频爬虫工具
支持多种视频网站和流媒体平台
"""

import os
import re
import json
import time
import logging
import requests
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Tuple
import concurrent.futures
from threading import Lock


class AdvancedVideoSpider:
    """高级视频爬虫类"""
    
    def __init__(self, download_dir: str = "../data", max_workers: int = 3, log_level: str = "INFO"):
        """
        初始化高级爬虫
        
        Args:
            download_dir: 下载目录
            max_workers: 最大并发数
            log_level: 日志级别
        """
        self.download_dir = download_dir
        self.max_workers = max_workers
        self.session = requests.Session()
        self.download_lock = Lock()
        
        # 设置请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # 设置日志
        self.logger = self._setup_logger(log_level)
        
        # 创建下载目录
        os.makedirs(download_dir, exist_ok=True)
        
        # 视频网站特定的提取器
        self.extractors = {
            'youtube.com': self._extract_youtube,
            'youtu.be': self._extract_youtube,
            'bilibili.com': self._extract_bilibili,
            'vimeo.com': self._extract_vimeo,
            'dailymotion.com': self._extract_dailymotion,
            'generic': self._extract_generic
        }
        
        # 支持的视频格式
        self.video_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.m4v', '.3gp']
        
    def _setup_logger(self, log_level: str) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger('AdvancedVideoSpider')
        logger.setLevel(getattr(logging, log_level.upper()))
        
        # 避免重复添加处理器
        if not logger.handlers:
            # 创建文件处理器
            os.makedirs('../logs', exist_ok=True)
            file_handler = logging.FileHandler('../logs/advanced_spider.log', encoding='utf-8')
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
    
    def _get_domain(self, url: str) -> str:
        """获取URL的域名"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    
    def _extract_youtube(self, soup: BeautifulSoup, url: str) -> List[Dict[str, str]]:
        """提取YouTube视频信息"""
        videos = []
        
        # 查找YouTube视频ID
        video_id_pattern = r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})'
        match = re.search(video_id_pattern, url)
        
        if match:
            video_id = match.group(1)
            # 注意：实际的YouTube下载需要使用youtube-dl或yt-dlp
            videos.append({
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'title': soup.find('title').get_text() if soup.find('title') else f"YouTube视频_{video_id}",
                'type': 'youtube',
                'video_id': video_id
            })
            
            self.logger.info(f"检测到YouTube视频: {video_id}")
            self.logger.warning("YouTube视频下载需要使用专门的工具如yt-dlp")
        
        return videos
    
    def _extract_bilibili(self, soup: BeautifulSoup, url: str) -> List[Dict[str, str]]:
        """提取B站视频信息"""
        videos = []
        
        # 查找B站视频信息
        bv_pattern = r'bilibili\.com/video/(BV[a-zA-Z0-9]+)'
        av_pattern = r'bilibili\.com/video/av(\d+)'
        
        bv_match = re.search(bv_pattern, url)
        av_match = re.search(av_pattern, url)
        
        if bv_match or av_match:
            video_id = bv_match.group(1) if bv_match else f"av{av_match.group(1)}"
            title = soup.find('title').get_text() if soup.find('title') else f"B站视频_{video_id}"
            
            videos.append({
                'url': url,
                'title': title,
                'type': 'bilibili',
                'video_id': video_id
            })
            
            self.logger.info(f"检测到B站视频: {video_id}")
            self.logger.warning("B站视频下载需要特殊处理")
        
        return videos
    
    def _extract_vimeo(self, soup: BeautifulSoup, url: str) -> List[Dict[str, str]]:
        """提取Vimeo视频信息"""
        videos = []
        
        # 查找Vimeo视频ID
        vimeo_pattern = r'vimeo\.com/(\d+)'
        match = re.search(vimeo_pattern, url)
        
        if match:
            video_id = match.group(1)
            title = soup.find('title').get_text() if soup.find('title') else f"Vimeo视频_{video_id}"
            
            videos.append({
                'url': url,
                'title': title,
                'type': 'vimeo',
                'video_id': video_id
            })
            
            self.logger.info(f"检测到Vimeo视频: {video_id}")
        
        return videos
    
    def _extract_dailymotion(self, soup: BeautifulSoup, url: str) -> List[Dict[str, str]]:
        """提取Dailymotion视频信息"""
        videos = []
        
        # 查找Dailymotion视频ID
        dm_pattern = r'dailymotion\.com/video/([a-zA-Z0-9]+)'
        match = re.search(dm_pattern, url)
        
        if match:
            video_id = match.group(1)
            title = soup.find('title').get_text() if soup.find('title') else f"Dailymotion视频_{video_id}"
            
            videos.append({
                'url': url,
                'title': title,
                'type': 'dailymotion',
                'video_id': video_id
            })
            
            self.logger.info(f"检测到Dailymotion视频: {video_id}")
        
        return videos
    
    def _extract_generic(self, soup: BeautifulSoup, url: str) -> List[Dict[str, str]]:
        """通用视频提取器"""
        videos = []
        
        # 查找video标签
        video_tags = soup.find_all('video')
        for video in video_tags:
            src = video.get('src')
            if src:
                full_url = urljoin(url, src)
                videos.append({
                    'url': full_url,
                    'title': video.get('title') or video.get('alt', ''),
                    'type': 'video_tag'
                })
            
            # 查找source标签
            sources = video.find_all('source')
            for source in sources:
                src = source.get('src')
                if src:
                    full_url = urljoin(url, src)
                    videos.append({
                        'url': full_url,
                        'title': video.get('title') or source.get('title', ''),
                        'type': 'source_tag'
                    })
        
        # 查找iframe中的视频
        iframes = soup.find_all('iframe')
        for iframe in iframes:
            src = iframe.get('src')
            if src and any(domain in src for domain in ['youtube.com', 'vimeo.com', 'bilibili.com']):
                full_url = urljoin(url, src)
                videos.append({
                    'url': full_url,
                    'title': iframe.get('title', ''),
                    'type': 'iframe_embed'
                })
        
        # 查找链接中的视频文件
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            if any(href.lower().endswith(ext) for ext in self.video_extensions):
                full_url = urljoin(url, href)
                videos.append({
                    'url': full_url,
                    'title': link.get_text(strip=True),
                    'type': 'direct_link'
                })
        
        # 使用正则表达式查找可能的视频URL
        text_content = str(soup)
        patterns = [
            r'https?://[^\s"\'>]+\.(?:mp4|avi|mov|wmv|flv|webm|mkv|m4v)(?:\?[^\s"\'>]*)?',
            r'"(https?://[^"]+\.(?:mp4|avi|mov|wmv|flv|webm|mkv|m4v))"',
            r"'(https?://[^']+\.(?:mp4|avi|mov|wmv|flv|webm|mkv|m4v))'"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            for match in matches:
                video_url = match if isinstance(match, str) else match[0]
                videos.append({
                    'url': video_url,
                    'title': '',
                    'type': 'regex_match'
                })
        
        return videos
    
    def get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """获取网页内容"""
        try:
            self.logger.info(f"正在获取页面内容: {url}")
            
            # 添加重试机制
            for attempt in range(3):
                try:
                    response = self.session.get(url, timeout=30)
                    response.raise_for_status()
                    break
                except requests.RequestException as e:
                    if attempt == 2:
                        raise e
                    self.logger.warning(f"第{attempt + 1}次尝试失败，重试中...")
                    time.sleep(2)
            
            # 检测编码
            if response.encoding == 'ISO-8859-1':
                response.encoding = response.apparent_encoding
            
            soup = BeautifulSoup(response.text, 'html.parser')
            self.logger.info(f"成功获取页面内容: {url}")
            return soup
            
        except requests.RequestException as e:
            self.logger.error(f"获取页面内容失败 {url}: {e}")
            return None
    
    def extract_videos(self, url: str) -> List[Dict[str, str]]:
        """提取视频信息"""
        soup = self.get_page_content(url)
        if not soup:
            return []
        
        domain = self._get_domain(url)
        
        # 选择合适的提取器
        extractor = self.extractors.get(domain, self.extractors['generic'])
        videos = extractor(soup, url)
        
        # 去重
        seen_urls = set()
        unique_videos = []
        for video in videos:
            if video['url'] not in seen_urls:
                seen_urls.add(video['url'])
                unique_videos.append(video)
        
        self.logger.info(f"从 {url} 提取到 {len(unique_videos)} 个视频")
        return unique_videos
    
    def download_video(self, video_info: Dict[str, str]) -> Tuple[bool, str]:
        """下载视频文件"""
        url = video_info['url']
        title = video_info.get('title', '')
        video_type = video_info.get('type', 'unknown')
        
        # 对于特殊类型的视频，给出提示
        if video_type in ['youtube', 'bilibili', 'vimeo', 'dailymotion']:
            message = f"检测到{video_type}视频，建议使用专门的下载工具"
            self.logger.warning(message)
            return False, message
        
        try:
            self.logger.info(f"开始下载视频: {url}")
            
            # 获取文件信息
            head_response = self.session.head(url, timeout=10)
            content_type = head_response.headers.get('content-type', '')
            
            if not content_type.startswith('video/') and not any(ext in url.lower() for ext in self.video_extensions):
                message = f"URL可能不是视频文件: {url}"
                self.logger.warning(message)
                return False, message
            
            # 获取文件名
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            
            if not filename or '.' not in filename:
                # 根据content-type确定扩展名
                ext_map = {
                    'video/mp4': '.mp4',
                    'video/avi': '.avi',
                    'video/quicktime': '.mov',
                    'video/x-msvideo': '.avi',
                    'video/webm': '.webm'
                }
                ext = ext_map.get(content_type, '.mp4')
                
                if title:
                    filename = f"{title}{ext}"
                else:
                    filename = f"video_{int(time.time())}{ext}"
            
            # 清理文件名
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            filename = filename[:200]  # 限制文件名长度
            
            with self.download_lock:
                filepath = os.path.join(self.download_dir, filename)
                
                # 检查文件是否已存在
                if os.path.exists(filepath):
                    message = f"文件已存在，跳过下载: {filename}"
                    self.logger.info(message)
                    return True, message
            
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
                            print(f"\r下载 {filename}: {progress:.1f}%", end='', flush=True)
            
            print()  # 换行
            message = f"视频下载完成: {filename}"
            self.logger.info(message)
            return True, message
            
        except Exception as e:
            message = f"下载视频失败 {url}: {e}"
            self.logger.error(message)
            return False, message
    
    def crawl_videos_parallel(self, urls: List[str]) -> Dict[str, List[Dict[str, str]]]:
        """并行爬取多个URL的视频"""
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交提取任务
            future_to_url = {executor.submit(self.extract_videos, url): url for url in urls}
            
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    videos = future.result()
                    results[url] = videos
                except Exception as e:
                    self.logger.error(f"处理URL失败 {url}: {e}")
                    results[url] = []
        
        return results
    
    def download_videos_parallel(self, videos: List[Dict[str, str]]) -> List[Tuple[bool, str, Dict[str, str]]]:
        """并行下载视频"""
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交下载任务
            future_to_video = {executor.submit(self.download_video, video): video for video in videos}
            
            for future in concurrent.futures.as_completed(future_to_video):
                video = future_to_video[future]
                try:
                    success, message = future.result()
                    results.append((success, message, video))
                except Exception as e:
                    error_msg = f"下载任务异常: {e}"
                    self.logger.error(error_msg)
                    results.append((False, error_msg, video))
        
        return results


if __name__ == "__main__":
    # 示例使用
    spider = AdvancedVideoSpider(max_workers=2)
    
    # 测试URL列表
    test_urls = [
        "https://example.com/videos",
        "https://sample-videos.com/"
    ]
    
    try:
        print("开始爬取视频...")
        
        # 提取所有视频
        all_videos = []
        for url in test_urls:
            videos = spider.extract_videos(url)
            all_videos.extend(videos)
            print(f"从 {url} 找到 {len(videos)} 个视频")
        
        if all_videos:
            print(f"\n总共找到 {len(all_videos)} 个视频，开始下载...")
            
            # 并行下载
            download_results = spider.download_videos_parallel(all_videos)
            
            # 统计结果
            successful = sum(1 for success, _, _ in download_results if success)
            print(f"\n下载完成！成功: {successful}, 失败: {len(download_results) - successful}")
            
            # 显示详细结果
            for success, message, video in download_results:
                status = "✓" if success else "✗"
                print(f"{status} {message}")
        else:
            print("未找到任何视频")
            
    except KeyboardInterrupt:
        print("\n用户中断操作")
    except Exception as e:
        print(f"\n发生错误: {e}")