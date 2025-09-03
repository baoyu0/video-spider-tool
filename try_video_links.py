#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
尝试从API分析中发现的视频链接下载视频
"""

import requests
import os
from pathlib import Path

def download_video_from_link(url, uid, sid, filename):
    """从指定链接下载视频"""
    session = requests.Session()
    
    # 设置认证头
    token = f"{uid}-{sid}"
    headers = {
        'Authorization': f'Bearer {token}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://metaso.cn/',
        'Origin': 'https://metaso.cn'
    }
    
    session.headers.update(headers)
    
    print(f"🔍 尝试下载: {url}")
    
    try:
        response = session.get(url, timeout=30, stream=True)
        print(f"   状态码: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'unknown')}")
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            
            # 检查是否是视频文件
            if 'video/' in content_type or 'application/octet-stream' in content_type:
                print(f"   ✅ 发现视频文件! Content-Type: {content_type}")
                
                # 创建下载目录
                download_dir = Path("downloads")
                download_dir.mkdir(exist_ok=True)
                
                file_path = download_dir / filename
                
                # 下载文件
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                file_size = os.path.getsize(file_path)
                print(f"   ✅ 下载完成: {file_path} ({file_size} bytes)")
                return True
            
            elif 'json' in content_type:
                # 如果是JSON响应，打印内容
                try:
                    json_data = response.json()
                    print(f"   📄 JSON响应: {json_data}")
                    
                    # 检查是否包含视频URL
                    if 'data' in json_data and isinstance(json_data['data'], dict):
                        if 'videoUrl' in json_data['data']:
                            video_url = json_data['data']['videoUrl']
                            print(f"   🎬 发现视频URL: {video_url}")
                            return download_video_from_link(video_url, uid, sid, filename)
                        elif 'url' in json_data['data']:
                            video_url = json_data['data']['url']
                            print(f"   🎬 发现URL: {video_url}")
                            return download_video_from_link(video_url, uid, sid, filename)
                    
                except Exception as e:
                    print(f"   ❌ JSON解析错误: {e}")
            
            else:
                print(f"   ⚠️ 未知内容类型: {content_type}")
                # 尝试保存前1024字节查看内容
                content_preview = response.content[:1024]
                print(f"   内容预览: {content_preview}")
        
        else:
            print(f"   ❌ 请求失败: {response.status_code}")
            if response.text:
                print(f"   错误信息: {response.text[:200]}")
    
    except Exception as e:
        print(f"   ❌ 请求异常: {str(e)}")
    
    return False

def main():
    # 用户认证信息
    uid = "654ce6f986a91de24c79b52f"
    sid = "7db6149bc7944aff8fc5632fb5e91e75"
    
    # 从API分析中发现的视频链接
    video_links = [
        "https://metaso.cn/api/ppt/8651522172447916032/video",
        "https://metaso.cn/api/chapter/8651523279591608320/video",
        "https://metaso.cn/api/export/8651522172447916032/video",
        "https://metaso.cn/api/generate/8651522172447916032/video",
        "https://metaso.cn/api/file/8651522172447916032/video",
        "https://metaso.cn/api/courseware/8651522172447916032/video"
    ]
    
    print("="*80)
    print("🎬 尝试从发现的视频链接下载视频")
    print(f"🔐 认证信息: UID={uid[:10]}..., SID={sid[:10]}...")
    print("="*80)
    
    for i, link in enumerate(video_links, 1):
        print(f"\n📹 尝试链接 {i}/{len(video_links)}:")
        filename = f"metaso_video_{i}.mp4"
        
        success = download_video_from_link(link, uid, sid, filename)
        if success:
            print(f"\n🎉 视频下载成功！")
            break
        else:
            print(f"   ❌ 此链接下载失败")
    
    else:
        print(f"\n❌ 所有链接都下载失败")
        print(f"\n💡 可能的原因:")
        print(f"   1. 视频尚未生成完成")
        print(f"   2. 需要特殊的请求方法（POST而不是GET）")
        print(f"   3. 认证信息不正确或已过期")
        print(f"   4. API接口需要额外参数")

if __name__ == "__main__":
    main()