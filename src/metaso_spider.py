#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
秘塔AI搜索课件爬虫工具
专门用于爬取秘塔AI搜索平台的课件内容
"""

import os
import re
import time
import json
import logging
import requests
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
from typing import List, Dict, Optional


class MetasoSpider:
    """秘塔AI搜索课件爬虫类"""
    
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
        
        # 秘塔AI搜索的基础URL
        self.base_url = "https://metaso.cn"
        
        # 导入配置
        from config import DevelopmentConfig
        self.config = DevelopmentConfig()
        
    def _setup_logger(self, log_level: str) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger('MetasoSpider')
        logger.setLevel(getattr(logging, log_level.upper()))
        
        # 避免重复添加处理器
        if logger.handlers:
            return logger
        
        # 创建logs目录
        os.makedirs('../logs', exist_ok=True)
        
        # 创建文件处理器
        file_handler = logging.FileHandler('../logs/metaso_spider.log', encoding='utf-8')
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
    
    def parse_metaso_url(self, url: str) -> Dict[str, str]:
        """
        解析秘塔AI搜索的URL，提取文件信息
        
        Args:
            url: 秘塔AI搜索的URL
            
        Returns:
            包含文件信息的字典
        """
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        file_info = {
            'file_id': query_params.get('_id', [''])[0],
            'title': query_params.get('title', [''])[0],
            'download_url': query_params.get('downloadUrl', [''])[0],
            'preview_url': query_params.get('previewUrl', [''])[0],
            'file_type': query_params.get('type', [''])[0]
        }
        
        self.logger.info(f"解析URL得到文件信息: {file_info}")
        return file_info
    
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
            response.encoding = response.apparent_encoding or 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            self.logger.info(f"成功获取页面内容")
            return soup
            
        except requests.RequestException as e:
            self.logger.error(f"获取页面内容失败: {e}")
            return None
    
    def extract_course_content(self, soup: BeautifulSoup) -> Dict[str, any]:
        """
        从页面中提取课件内容信息
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            课件内容信息
        """
        content_info = {
            'title': '',
            'pages': [],
            'total_pages': 0,
            'current_page': 1,
            'download_links': [],
            'preview_images': []
        }
        
        try:
            # 提取标题
            title_element = soup.find('title')
            if title_element:
                content_info['title'] = title_element.get_text(strip=True)
            
            # 查找页面信息
            page_info = soup.find_all(text=re.compile(r'共\d+页|第\d+页'))
            for info in page_info:
                if '共' in info and '页' in info:
                    match = re.search(r'共(\d+)页', info)
                    if match:
                        content_info['total_pages'] = int(match.group(1))
                
                if '第' in info and '页' in info:
                    match = re.search(r'第(\d+)页', info)
                    if match:
                        content_info['current_page'] = int(match.group(1))
            
            # 查找下载链接
            download_links = soup.find_all('a', href=True)
            for link in download_links:
                href = link['href']
                if 'download' in href or '下载' in link.get_text():
                    full_url = urljoin(self.base_url, href)
                    content_info['download_links'].append({
                        'url': full_url,
                        'text': link.get_text(strip=True)
                    })
            
            # 查找预览图片
            images = soup.find_all('img', src=True)
            for img in images:
                src = img['src']
                if any(keyword in src.lower() for keyword in ['preview', 'page', 'slide']):
                    full_url = urljoin(self.base_url, src)
                    content_info['preview_images'].append({
                        'url': full_url,
                        'alt': img.get('alt', ''),
                        'title': img.get('title', '')
                    })
            
            # 查找iframe中的内容
            iframes = soup.find_all('iframe', src=True)
            for iframe in iframes:
                iframe_src = iframe['src']
                if 'preview' in iframe_src:
                    content_info['preview_iframe'] = urljoin(self.base_url, iframe_src)
            
            self.logger.info(f"提取到课件信息: 标题={content_info['title']}, 总页数={content_info['total_pages']}")
            
        except Exception as e:
            self.logger.error(f"提取课件内容失败: {e}")
        
        return content_info
    
    def download_file(self, url: str, filename: str = None) -> bool:
        """
        下载文件
        
        Args:
            url: 下载URL
            filename: 保存的文件名
            
        Returns:
            下载是否成功
        """
        try:
            self.logger.info(f"开始下载文件: {url}")
            
            # 获取文件名
            if not filename:
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
                
                if not filename or '.' not in filename:
                    # 从Content-Disposition头获取文件名
                    head_response = self.session.head(url, timeout=10)
                    content_disposition = head_response.headers.get('Content-Disposition', '')
                    if 'filename=' in content_disposition:
                        filename = content_disposition.split('filename=')[1].strip('"\'')
                    else:
                        filename = f"download_{int(time.time())}.file"
            
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
            self.logger.info(f"文件下载完成: {filename} ({downloaded_size} bytes)")
            return True
            
        except Exception as e:
            self.logger.error(f"下载文件失败 {url}: {e}")
            return False
    
    def crawl_metaso_course(self, url: str) -> Dict[str, any]:
        """
        爬取秘塔AI搜索的课件
        
        Args:
            url: 秘塔AI搜索的课件URL
            
        Returns:
            爬取结果信息
        """
        self.logger.info(f"开始爬取秘塔AI课件: {url}")
        
        result = {
            'success': False,
            'file_info': {},
            'content_info': {},
            'downloaded_files': [],
            'error': None
        }
        
        try:
            # 解析URL获取文件信息
            file_info = self.parse_metaso_url(url)
            result['file_info'] = file_info
            
            # 获取页面内容
            soup = self.get_page_content(url)
            if not soup:
                result['error'] = "无法获取页面内容"
                return result
            
            # 提取课件内容信息
            content_info = self.extract_course_content(soup)
            result['content_info'] = content_info
            
            # 尝试下载原文件
            if file_info.get('download_url'):
                download_url = urljoin(self.base_url, file_info['download_url'])
                filename = file_info.get('title', 'course_file')
                if file_info.get('file_type'):
                    filename += f".{file_info['file_type']}"
                
                if self.download_file(download_url, filename):
                    result['downloaded_files'].append({
                        'type': 'original_file',
                        'filename': filename,
                        'url': download_url
                    })
            
            # 下载其他发现的文件
            for download_link in content_info.get('download_links', []):
                if self.download_file(download_link['url']):
                    result['downloaded_files'].append({
                        'type': 'additional_file',
                        'filename': os.path.basename(urlparse(download_link['url']).path),
                        'url': download_link['url']
                    })
            
            # 下载预览图片
            for i, image in enumerate(content_info.get('preview_images', [])):
                image_filename = f"preview_page_{i+1}.jpg"
                if self.download_file(image['url'], image_filename):
                    result['downloaded_files'].append({
                        'type': 'preview_image',
                        'filename': image_filename,
                        'url': image['url']
                    })
            
            # 保存课件信息到JSON文件
            info_filename = f"{file_info.get('title', 'course')}_info.json"
            info_filepath = os.path.join(self.download_dir, info_filename)
            
            with open(info_filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    'file_info': file_info,
                    'content_info': content_info,
                    'crawl_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'source_url': url
                }, f, ensure_ascii=False, indent=2)
            
            result['downloaded_files'].append({
                'type': 'info_file',
                'filename': info_filename,
                'url': 'local'
            })
            
            result['success'] = True
            self.logger.info(f"课件爬取完成，共下载 {len(result['downloaded_files'])} 个文件")
            
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"爬取课件失败: {e}")
        
        return result


if __name__ == "__main__":
    # 示例使用
    spider = MetasoSpider()
    
    # 测试URL - 大语言模型概述课件
    test_url = "https://metaso.cn/bookshelf?displayUrl=%2Fapi%2Ffile%2F8651522172447916032%2Fpreview&url=%2Fapi%2Ffile%2F8651522172447916032%2Fpreview&page=1&totalPage=0&file_path=&_id=8651522172447916032&title=%E3%80%90%E8%AF%BE%E4%BB%B6%E3%80%91%E7%AC%AC1%E7%AB%A0_%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8B%E6%A6%82%E8%BF%B0.pptx&snippet=undefined&sessionId=null&tag=%E6%9C%AC%E5%9C%B0%E6%96%87%E4%BB%B6%E4%B8%8A%E4%BC%A0%E5%88%B0%E4%B9%A6%E6%9E%B6%E4%B8%93%E7%94%A8%E4%B8%93%E9%A2%98654ce6f986a91de24c79b52f&author=&publishDate=undefined&showFront=false&downloadUrl=%2Fapi%2Ffile%2F8651522172447916032%2Fdownload&previewUrl=%2Fapi%2Ffile%2F8651522172447916032%2Fpreview&internalFile=true&topicId=undefined&type=pptx&readMode=false"
    
    try:
        result = spider.crawl_metaso_course(test_url)
        
        if result['success']:
            print(f"\n✅ 爬取成功！")
            print(f"课件标题: {result['content_info'].get('title', '未知')}")
            print(f"文件类型: {result['file_info'].get('file_type', '未知')}")
            print(f"共下载 {len(result['downloaded_files'])} 个文件:")
            
            for file_info in result['downloaded_files']:
                print(f"  - {file_info['type']}: {file_info['filename']}")
        else:
            print(f"\n❌ 爬取失败: {result.get('error', '未知错误')}")
    
    def _is_valid_metaso_url(self, url: str) -> bool:
        """验证是否为有效的秘塔AI搜索URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc == 'metaso.cn' or parsed.netloc.endswith('.metaso.cn')
        except Exception:
            return False
            
    except KeyboardInterrupt:
        print("\n用户中断爬取")
    except Exception as e:
        print(f"\n发生错误: {e}")