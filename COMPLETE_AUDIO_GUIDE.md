# Metaso完整音频下载指南

## 概述

本指南专门针对需要下载**完整音频文件**（如MP3、WAV等格式）的用户，而非音频片段。`complete_audio_downloader.py` 工具专门设计用于从Metaso网站下载完整的音频文件。

## 与其他工具的区别

| 工具 | 用途 | 下载内容 |
|------|------|----------|
| `complete_audio_downloader.py` | 下载完整音频文件 | 单个完整音频文件 |
| `metaso_video_downloader.py` | 下载视频文件 | 视频文件（MP4等） |

## 工具特点

### 🎯 专门针对完整音频
- 专门查找完整音频导出API
- 支持多种音频格式（MP3、WAV、OGG、M4A）
- 自动识别音频文件类型
- 智能文件命名

### 🔍 全面的API端点扫描
- 音频导出端点
- 音频生成端点
- 音频下载端点
- TTS相关端点
- 课件音频端点

### 🔐 自动认证
- 自动获取认证信息
- 智能处理权限验证
- 无需手动输入认证参数

## 快速开始

### 基础使用

```bash
cd video-spider-tool
python complete_audio_downloader.py
```

### 指定URL下载

```bash
python complete_audio_downloader.py https://metaso.cn/your-target-url
```

## 详细使用步骤

### 步骤1：准备环境

确保已安装必要的依赖：
```bash
pip install requests beautifulsoup4
```

### 步骤2：运行下载器

```bash
# 使用默认URL
python complete_audio_downloader.py

# 指定目标URL
python complete_audio_downloader.py https://metaso.cn/your-target-url
```

工具会自动：
- 获取认证信息
- 解析目标URL
- 扫描可用的音频API端点
- 下载完整音频文件

## 工作原理

### 1. URL解析
- 从Metaso URL中提取文件ID、章节ID等信息
- 解析音频相关参数（语言、语速、音色等）

### 2. API端点扫描
工具会尝试以下类型的API端点：

#### 音频导出端点
- `/api/file/{file_id}/audio/export`
- `/api/chapter/{chapter_id}/audio/export`

#### 音频生成端点
- `/api/file/{file_id}/generate/audio`
- `/api/chapter/{chapter_id}/generate/audio`

#### 音频下载端点
- `/api/file/{file_id}/audio/download`
- `/api/chapter/{chapter_id}/audio/download`

#### TTS相关端点
- `/api/tts/{file_id}/export`
- `/api/tts/{chapter_id}/download`

### 3. 响应处理
- **直接音频文件**：Content-Type为audio/*的响应
- **JSON响应**：包含音频URL的JSON数据
- **大文件响应**：可能的音频文件

### 4. 文件下载
- 自动识别音频格式
- 显示下载进度
- 智能文件命名

## 预期结果

成功运行后，你将获得：

```
downloads/
└── 【课件】第1章_大语言模型概述.mp3  # 完整音频文件
```

## 支持的音频格式

- **MP3** (.mp3) - 最常见的音频格式
- **WAV** (.wav) - 无损音频格式
- **OGG** (.ogg) - 开源音频格式
- **M4A** (.m4a) - Apple音频格式

## 故障排除

### 问题1：未找到音频文件

**可能原因：**
- 音频尚未生成完成
- 需要认证权限
- 该文件不支持音频导出

**解决方案：**
1. 确认在Metaso网站上可以播放音频
2. 使用认证信息重试
3. 检查文件是否支持TTS功能

### 问题2：权限不足

**解决方案：**
1. 获取有效的UID和SID
2. 确认账户有访问权限
3. 检查文件是否为公开文件

### 问题3：下载的文件很小

**可能原因：**
- 下载的是错误信息而非音频文件
- API返回了错误响应

**解决方案：**
1. 检查控制台输出的错误信息
2. 尝试不同的API端点
3. 验证认证信息

### 问题4：文件格式不正确

**解决方案：**
1. 工具会自动识别Content-Type
2. 手动检查下载文件的实际格式
3. 使用音频播放器验证文件

## 高级配置

### 自定义下载目录

```python
downloader = CompleteAudioDownloader(download_dir="my_audio_downloads")
```

### 自定义请求头

在 `__init__` 方法中修改headers字典来自定义请求头。

### 添加新的API端点

在 `try_audio_api_endpoints` 方法中的 `audio_endpoints` 列表中添加新的端点。

## 注意事项

### 法律合规
- 仅下载你有权访问的内容
- 遵守Metaso的使用条款
- 尊重版权和知识产权

### 技术限制
- 依赖于Metaso的API结构
- 可能受到反爬虫机制限制
- 需要稳定的网络连接

### 使用建议
- 避免频繁请求
- 使用认证信息提高成功率
- 定期更新工具以适应API变化

## 与其他工具的配合使用

### 1. 先尝试完整音频下载
```bash
python complete_audio_downloader.py
```

### 2. 如果失败，再尝试视频下载
```bash
python metaso_video_downloader.py
```

### 3. 最后考虑片段下载
```bash
python blob_audio_downloader.py
```

## 技术支持

如果遇到问题：

1. **检查控制台输出**：查看详细的错误信息
2. **验证URL格式**：确保Metaso URL格式正确
3. **测试网络连接**：确认可以访问Metaso网站
4. **更新依赖**：确保所有Python包都是最新版本

## 更新日志

### v1.0.0
- 初始版本
- 支持完整音频文件下载
- 支持多种音频格式
- 支持认证下载
- 全面的API端点扫描