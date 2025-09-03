#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metaso认证信息获取指南
根据搜索结果，需要从浏览器获取uid和sid来进行API认证
"""

import requests
import json
from urllib.parse import urljoin
import os

class MetasoAuthenticatedDownloader:
    def __init__(self, uid=None, sid=None):
        self.session = requests.Session()
        
        # 如果提供了认证信息，设置Authorization头
        if uid and sid:
            token = f"{uid}-{sid}"
            self.session.headers.update({
                'Authorization': f'Bearer {token}',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Referer': 'https://metaso.cn/'
            })
        else:
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Referer': 'https://metaso.cn/'
            })
        
        self.file_id = "8651522172447916032"
        self.chapter_id = "8651523279591608320"
        self.base_url = "https://metaso.cn"
        
    def print_auth_guide(self):
        """打印认证信息获取指南"""
        print("="*80)
        print("🔐 Metaso认证信息获取指南")
        print("="*80)
        print("\n📋 步骤说明:")
        print("1. 打开浏览器，访问 https://metaso.cn/")
        print("2. 登录你的Metaso账号")
        print("3. 按F12打开开发者工具")
        print("4. 切换到 Application 标签页")
        print("5. 在左侧找到 Cookies > https://metaso.cn")
        print("6. 找到 'uid' 和 'sid' 两个cookie值")
        print("7. 复制这两个值，格式如下:")
        print("   uid: 65e91a6b2bac5b600dd8526a")
        print("   sid: 5e7acc465b114236a8d9de26c9f41846")
        print("\n💡 获取到认证信息后，重新运行此脚本并提供uid和sid参数")
        print("\n🚀 使用方法:")
        print("   python get_metaso_auth.py --uid=你的uid --sid=你的sid")
        print("\n" + "="*80)
        
    def test_auth(self):
        """测试认证是否有效"""
        test_url = f"{self.base_url}/api/file/{self.file_id}"
        
        try:
            response = self.session.get(test_url, timeout=10)
            print(f"\n🔍 测试认证状态: {test_url}")
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'errCode' in data and data['errCode'] == 401:
                        print("   ❌ 认证失败: 401 Unauthorized")
                        return False
                    else:
                        print("   ✅ 认证成功!")
                        return True
                except:
                    print("   ✅ 认证可能成功 (非JSON响应)")
                    return True
            else:
                print(f"   ❌ 请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ 请求异常: {str(e)}")
            return False
            
    def try_download_video(self):
        """尝试下载视频"""
        if not self.test_auth():
            print("\n❌ 认证失败，无法下载视频")
            return False
            
        print("\n🎬 开始尝试下载视频...")
        
        # 尝试不同的视频API端点
        video_endpoints = [
            f"/api/chapter/{self.chapter_id}/video",
            f"/api/export/{self.file_id}/video", 
            f"/api/generate/{self.file_id}/video",
            f"/api/file/{self.file_id}/video",
            f"/api/courseware/{self.file_id}/video"
        ]
        
        for endpoint in video_endpoints:
            url = urljoin(self.base_url, endpoint)
            print(f"\n🔍 尝试端点: {endpoint}")
            
            try:
                response = self.session.get(url, timeout=30)
                print(f"   状态码: {response.status_code}")
                
                if response.status_code == 200:
                    content_type = response.headers.get('Content-Type', '')
                    
                    if 'video/' in content_type:
                        print(f"   ✅ 发现视频文件! Content-Type: {content_type}")
                        return self.download_video_file(response, endpoint)
                    
                    elif 'json' in content_type:
                        try:
                            data = response.json()
                            print(f"   JSON响应: {json.dumps(data, ensure_ascii=False, indent=2)[:300]}...")
                            
                            # 检查是否有错误
                            if 'errCode' in data:
                                if data['errCode'] == 401:
                                    print("   ❌ 认证失败")
                                elif data['errCode'] == 500:
                                    print("   ❌ 服务器错误")
                                else:
                                    print(f"   ❌ 错误码: {data['errCode']}")
                            else:
                                # 查找可能的视频链接
                                video_url = self.extract_video_url(data)
                                if video_url:
                                    print(f"   🎬 发现视频链接: {video_url}")
                                    return self.download_from_url(video_url)
                                    
                        except json.JSONDecodeError:
                            print("   ❌ JSON解析失败")
                            
                else:
                    print(f"   ❌ 请求失败: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ 请求异常: {str(e)}")
                
        print("\n❌ 所有端点都无法获取视频")
        return False
        
    def extract_video_url(self, data):
        """从JSON数据中提取视频URL"""
        def search_video_url(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key.lower() in ['url', 'video_url', 'download_url', 'stream_url', 'media_url', 'src', 'href']:
                        if isinstance(value, str) and ('http' in value or value.startswith('/')):
                            return value
                    result = search_video_url(value)
                    if result:
                        return result
            elif isinstance(obj, list):
                for item in obj:
                    result = search_video_url(item)
                    if result:
                        return result
            return None
            
        return search_video_url(data)
        
    def download_from_url(self, video_url):
        """从URL下载视频"""
        if not video_url.startswith('http'):
            video_url = urljoin(self.base_url, video_url)
            
        print(f"   🚀 开始下载: {video_url}")
        
        try:
            response = self.session.get(video_url, stream=True, timeout=30)
            if response.status_code == 200:
                return self.download_video_file(response, video_url)
            else:
                print(f"   ❌ 下载失败: {response.status_code}")
        except Exception as e:
            print(f"   ❌ 下载异常: {str(e)}")
            
        return False
        
    def download_video_file(self, response, source):
        """下载视频文件"""
        try:
            # 创建下载目录
            download_dir = "downloads"
            os.makedirs(download_dir, exist_ok=True)
            
            # 生成文件名
            filename = f"metaso_video_{self.file_id}.mp4"
            filepath = os.path.join(download_dir, filename)
            
            # 下载文件
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        
            file_size = os.path.getsize(filepath)
            print(f"   ✅ 下载完成: {filepath} ({file_size} bytes)")
            return True
            
        except Exception as e:
            print(f"   ❌ 保存文件失败: {str(e)}")
            return False

def main():
    import sys
    
    # 解析命令行参数
    uid = None
    sid = None
    
    for arg in sys.argv[1:]:
        if arg.startswith('--uid='):
            uid = arg.split('=', 1)[1]
        elif arg.startswith('--sid='):
            sid = arg.split('=', 1)[1]
            
    downloader = MetasoAuthenticatedDownloader(uid, sid)
    
    if not uid or not sid:
        downloader.print_auth_guide()
        print("\n⚠️ 请提供uid和sid参数后重新运行")
        return
        
    print("="*80)
    print("🎬 Metaso认证视频下载器")
    print(f"📋 文件ID: {downloader.file_id}")
    print(f"📋 章节ID: {downloader.chapter_id}")
    print(f"🔐 UID: {uid[:10]}...")
    print(f"🔐 SID: {sid[:10]}...")
    print("="*80)
    
    success = downloader.try_download_video()
    
    if success:
        print("\n🎉 视频下载成功！")
    else:
        print("\n❌ 视频下载失败")
        print("\n💡 可能的原因:")
        print("   1. 认证信息已过期，请重新获取")
        print("   2. 视频尚未生成完成")
        print("   3. 需要特殊权限或会员")
        print("   4. API接口已变更")

if __name__ == "__main__":
    main()