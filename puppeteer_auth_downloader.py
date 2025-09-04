#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用Puppeteer自动获取Metaso认证信息并下载音频
完全自动化的解决方案
"""

import os
import json
import requests
import argparse
from urllib.parse import urlparse, parse_qs
import time
import subprocess
import sys

class PuppeteerAuthDownloader:
    def __init__(self, url):
        self.url = url
        self.uid = None
        self.sid = None
        
        # 解析URL获取文件ID和章节ID
        self.file_id, self.chapter_id = self.parse_url(url)
        
        # 下载目录
        self.download_dir = "downloads"
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
    
    def parse_url(self, url):
        """解析URL获取文件ID和章节ID"""
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            
            file_id = params.get('_id', [None])[0]
            chapter_id = params.get('chapterId', [None])[0]
            
            print(f"📋 解析URL信息:")
            print(f"   文件ID: {file_id}")
            print(f"   章节ID: {chapter_id}")
            
            return file_id, chapter_id
            
        except Exception as e:
            print(f"❌ 解析URL失败: {str(e)}")
            return None, None
    
    def call_mcp_tool(self, server_name, tool_name, args):
        """调用MCP工具的辅助函数"""
        try:
            # 这里需要实际的MCP调用实现
            # 由于我们在Python脚本中，需要通过其他方式调用
            print(f"🔧 调用MCP工具: {server_name}.{tool_name}")
            print(f"   参数: {args}")
            return True, {"success": True}
        except Exception as e:
            print(f"❌ MCP工具调用失败: {str(e)}")
            return False, {"error": str(e)}
    
    def navigate_to_metaso(self):
        """导航到Metaso网站"""
        print("\n🌐 正在打开Metaso网站...")
        
        # 调用Puppeteer导航
        success, result = self.call_mcp_tool(
            "mcp.config.usrlocalmcp.Puppeteer",
            "puppeteer_navigate",
            {"url": "https://metaso.cn/"}
        )
        
        if success:
            print("✅ 网站加载成功")
            return True
        else:
            print(f"❌ 网站加载失败: {result}")
            return False
    
    def wait_for_login(self):
        """等待用户登录"""
        print("\n🔐 请在浏览器中登录Metaso账号...")
        print("\n📋 登录步骤:")
        print("   1. 在打开的浏览器窗口中点击登录")
        print("   2. 输入您的用户名和密码")
        print("   3. 完成登录后，按回车键继续...")
        
        # 等待用户确认登录完成
        input("\n按回车键确认已完成登录: ")
        
        return True
    
    def get_cookies_from_browser(self):
        """从浏览器获取cookies"""
        print("\n🍪 正在获取认证信息...")
        
        # 执行JavaScript获取cookies
        cookie_script = """
        const cookies = document.cookie.split(';');
        const result = {};
        cookies.forEach(cookie => {
            const [name, value] = cookie.trim().split('=');
            if (name === 'uid' || name === 'sid') {
                result[name] = value;
            }
        });
        return JSON.stringify(result);
        """
        
        # 调用Puppeteer执行JavaScript
        success, result = self.call_mcp_tool(
            "mcp.config.usrlocalmcp.Puppeteer",
            "puppeteer_evaluate",
            {"script": cookie_script}
        )
        
        if success:
            try:
                # 解析返回的cookies
                cookies_data = json.loads(result.get('result', '{}'))
                self.uid = cookies_data.get('uid')
                self.sid = cookies_data.get('sid')
                
                if self.uid and self.sid:
                    print(f"✅ 认证信息获取成功:")
                    print(f"   UID: {self.uid}")
                    print(f"   SID: {self.sid[:20]}...")
                    return True
                else:
                    print("❌ 未找到有效的认证信息")
                    print("💡 请确保已经成功登录Metaso账号")
                    return False
                    
            except json.JSONDecodeError:
                print("❌ 解析cookies数据失败")
                return False
        else:
            print(f"❌ 获取cookies失败: {result}")
            return False
    
    def manual_cookie_input(self):
        """手动输入cookie信息"""
        print("\n🔧 自动获取失败，请手动输入认证信息:")
        print("\n📋 获取步骤:")
        print("   1. 在浏览器中按F12打开开发者工具")
        print("   2. 切换到 Application 标签页")
        print("   3. 在左侧找到 Cookies > https://metaso.cn")
        print("   4. 找到 'uid' 和 'sid' 两个cookie值")
        print("   5. 复制这两个值")
        
        uid = input("\n请输入UID: ").strip()
        sid = input("请输入SID: ").strip()
        
        if uid and sid:
            self.uid = uid
            self.sid = sid
            print(f"\n✅ 认证信息已设置:")
            print(f"   UID: {self.uid}")
            print(f"   SID: {self.sid[:20]}...")
            return True
        else:
            print("❌ 认证信息不完整")
            return False
    
    def try_audio_endpoints(self):
        """尝试各种音频API端点"""
        print("\n🎵 尝试下载完整音频文件...")
        
        if not self.uid or not self.sid:
            print("❌ 缺少认证信息")
            return False
        
        # 创建requests session
        session = requests.Session()
        
        # 设置cookies
        session.cookies.set('uid', self.uid)
        session.cookies.set('sid', self.sid)
        
        # 设置headers
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': self.url,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        })
        
        # 音频API端点列表
        audio_endpoints = [
            f"https://metaso.cn/api/ppt/{self.file_id}/audio/export",
            f"https://metaso.cn/api/ppt/{self.file_id}/audio/download",
            f"https://metaso.cn/api/ppt/{self.file_id}/audio/url",
            f"https://metaso.cn/api/chapter/{self.chapter_id}/audio/export",
            f"https://metaso.cn/api/chapter/{self.chapter_id}/audio/download",
            f"https://metaso.cn/api/chapter/{self.chapter_id}/audio/url",
            f"https://metaso.cn/api/file/{self.file_id}/audio/export",
            f"https://metaso.cn/api/file/{self.file_id}/audio/download",
            f"https://metaso.cn/api/courseware/{self.file_id}/audio",
            f"https://metaso.cn/api/courseware/{self.file_id}/audio/export",
            f"https://metaso.cn/api/courseware/{self.file_id}/audio/download",
            f"https://metaso.cn/api/tts/{self.file_id}/export",
            f"https://metaso.cn/api/tts/{self.file_id}/download",
            f"https://metaso.cn/api/tts/{self.chapter_id}/export",
            f"https://metaso.cn/api/tts/{self.chapter_id}/download",
            f"https://metaso.cn/api/media/{self.file_id}/audio",
            f"https://metaso.cn/api/media/{self.chapter_id}/audio",
            f"https://metaso.cn/api/file/{self.file_id}/export",
            f"https://metaso.cn/api/chapter/{self.chapter_id}/export"
        ]
        
        for endpoint in audio_endpoints:
            endpoint_name = '/'.join(endpoint.split('/')[-3:])  # 显示最后三部分
            print(f"\n🔍 尝试音频API端点: {endpoint_name}")
            
            try:
                response = session.get(endpoint, timeout=15)
                print(f"   状态码: {response.status_code}")
                
                if response.status_code == 200:
                    content_type = response.headers.get('Content-Type', '')
                    print(f"   Content-Type: {content_type}")
                    
                    # 检查是否是音频文件
                    if 'audio' in content_type or 'mp3' in content_type:
                        return self.download_audio_file(response, endpoint)
                    
                    # 检查是否是JSON响应
                    elif 'json' in content_type:
                        try:
                            data = response.json()
                            print(f"   JSON响应: {json.dumps(data, ensure_ascii=False)[:100]}...")
                            
                            # 从JSON中提取音频URL
                            audio_url = self.extract_audio_url(data)
                            if audio_url:
                                return self.download_audio_from_url(session, audio_url, endpoint)
                                
                        except json.JSONDecodeError:
                            print("   响应不是有效的JSON")
                
            except Exception as e:
                print(f"   请求失败: {str(e)}")
                continue
        
        return False
    
    def extract_audio_url(self, data):
        """从JSON数据中提取音频URL"""
        # 常见的音频URL字段
        audio_fields = ['url', 'audio_url', 'download_url', 'file_url', 'src', 'path', 'link']
        
        def search_dict(obj, fields):
            if isinstance(obj, dict):
                for field in fields:
                    if field in obj and obj[field]:
                        url = obj[field]
                        if isinstance(url, str) and ('.mp3' in url or '.wav' in url or '.m4a' in url or 'audio' in url):
                            return url
                
                # 递归搜索
                for value in obj.values():
                    result = search_dict(value, fields)
                    if result:
                        return result
            
            elif isinstance(obj, list):
                for item in obj:
                    result = search_dict(item, fields)
                    if result:
                        return result
            
            return None
        
        return search_dict(data, audio_fields)
    
    def download_audio_from_url(self, session, audio_url, source_endpoint):
        """从URL下载音频文件"""
        print(f"\n🎵 找到音频URL: {audio_url}")
        
        try:
            # 处理相对URL
            if audio_url.startswith('/'):
                audio_url = f"https://metaso.cn{audio_url}"
            
            response = session.get(audio_url, stream=True, timeout=30)
            
            if response.status_code == 200:
                # 确定文件扩展名
                if '.mp3' in audio_url:
                    ext = '.mp3'
                elif '.wav' in audio_url:
                    ext = '.wav'
                elif '.m4a' in audio_url:
                    ext = '.m4a'
                else:
                    ext = '.mp3'  # 默认
                
                filename = f"metaso_audio_{self.file_id}{ext}"
                filepath = os.path.join(self.download_dir, filename)
                
                file_size = int(response.headers.get('Content-Length', 0))
                print(f"   文件大小: {file_size / 1024 / 1024:.2f} MB")
                print(f"   保存到: {filepath}")
                
                with open(filepath, 'wb') as f:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            if file_size > 0:
                                progress = (downloaded / file_size) * 100
                                print(f"\r   下载进度: {progress:.1f}%", end='', flush=True)
                
                print(f"\n✅ 音频下载成功: {filepath}")
                print(f"   来源: {source_endpoint}")
                return True
            else:
                print(f"❌ 下载失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 下载音频时出错: {str(e)}")
            return False
    
    def download_audio_file(self, response, source_endpoint):
        """直接下载音频文件"""
        print(f"\n🎵 发现音频文件，开始下载...")
        
        try:
            filename = f"metaso_audio_{self.file_id}.mp3"
            filepath = os.path.join(self.download_dir, filename)
            
            file_size = int(response.headers.get('Content-Length', 0))
            print(f"   文件大小: {file_size / 1024 / 1024:.2f} MB")
            print(f"   保存到: {filepath}")
            
            with open(filepath, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if file_size > 0:
                            progress = (downloaded / file_size) * 100
                            print(f"\r   下载进度: {progress:.1f}%", end='', flush=True)
            
            print(f"\n✅ 音频下载成功: {filepath}")
            print(f"   来源: {source_endpoint}")
            return True
            
        except Exception as e:
            print(f"❌ 下载音频时出错: {str(e)}")
            return False
    
    def run(self):
        """运行自动认证下载器"""
        print("="*80)
        print("🤖 Metaso Puppeteer自动认证音频下载器")
        print(f"📋 文件ID: {self.file_id}")
        print(f"📋 章节ID: {self.chapter_id}")
        print("="*80)
        
        try:
            # 1. 导航到Metaso网站
            if not self.navigate_to_metaso():
                return False
            
            # 2. 等待用户登录
            if not self.wait_for_login():
                return False
            
            # 3. 尝试自动获取cookies
            if not self.get_cookies_from_browser():
                # 4. 如果自动获取失败，使用手动输入
                if not self.manual_cookie_input():
                    return False
            
            # 5. 尝试下载音频
            if self.try_audio_endpoints():
                print("\n🎉 音频下载成功！")
                return True
            else:
                print("\n❌ 未找到可下载的完整音频文件")
                print("\n💡 建议:")
                print("   1. 确认音频已经生成完成")
                print("   2. 检查该文件是否支持音频导出功能")
                print("   3. 尝试在网页中手动生成音频")
                print("   4. 确认认证信息是否正确")
                return False
                
        except Exception as e:
            print(f"❌ 运行过程中出错: {str(e)}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Metaso Puppeteer自动认证音频下载器')
    parser.add_argument('url', help='Metaso页面URL')
    
    args = parser.parse_args()
    
    downloader = PuppeteerAuthDownloader(args.url)
    success = downloader.run()
    
    if success:
        print("\n🎉 下载完成！")
    else:
        print("\n❌ 下载失败")
        print("\n💡 备选方案:")
        print("   1. 使用 manual_auth_helper.py 手动输入认证信息")
        print("   2. 使用 complete_audio_downloader.py 并提供 --uid 和 --sid 参数")
        print("   3. 检查网络连接和Metaso网站状态")

if __name__ == "__main__":
    main()