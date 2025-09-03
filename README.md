# 秘塔AI搜索课件爬虫工具

一个专门用于爬取秘塔AI搜索（metaso.cn）课件内容的Python工具。

## 功能特性

- 🎯 专门针对metaso.cn网站优化
- 📚 支持课件内容批量下载
- 🖼️ 自动下载课件中的图片和媒体文件
- 📝 详细的日志记录和错误处理
- ⚙️ 灵活的配置管理
- 🔄 支持断点续传和重试机制

## 项目结构

```
video-spider-tool/
├── src/                    # 源代码目录
│   ├── metaso_spider.py   # 秘塔AI搜索爬虫主程序
│   ├── video_spider.py    # 通用视频爬虫基类
│   ├── advanced_spider.py # 高级爬虫功能
│   └── config.py          # 配置管理
├── data/                  # 下载数据存储目录
├── logs/                  # 日志文件目录
├── requirements.txt       # Python依赖包
├── .gitignore            # Git忽略文件
└── README.md             # 项目说明文档
```

## 安装和使用

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd video-spider-tool

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 基本使用

```python
from src.metaso_spider import MetasoSpider

# 创建爬虫实例
spider = MetasoSpider()

# 爬取课件内容
url = "https://metaso.cn/course/example"
result = spider.crawl_course(url)

print(f"爬取完成，共下载 {len(result['files'])} 个文件")
```

### 3. 配置说明

在 `src/config.py` 中可以调整以下配置：

- **下载设置**：文件保存路径、并发数量、重试次数
- **请求参数**：超时时间、请求间隔、User-Agent
- **日志配置**：日志级别、输出格式、文件路径
- **爬虫规则**：支持的文件类型、URL过滤规则

## 主要模块

### MetasoSpider

专门针对metaso.cn网站的爬虫类，主要功能：

- `crawl_course(url)`: 爬取指定课程的所有内容
- `extract_course_info(soup)`: 提取课程基本信息
- `download_file(url, filename)`: 下载文件并显示进度
- `get_page_content(url)`: 获取网页内容

### 配置管理

支持开发和生产环境的不同配置：

```python
from src.config import DevelopmentConfig, ProductionConfig

# 开发环境
config = DevelopmentConfig()

# 生产环境
config = ProductionConfig()
```

## 日志系统

项目使用Python标准logging模块，支持：

- 控制台彩色输出
- 文件日志记录
- 不同级别的日志（DEBUG, INFO, WARNING, ERROR）
- 自动日志轮转

日志文件保存在 `logs/` 目录下。

## 错误处理

- 网络请求超时重试
- 文件下载失败重试
- 详细的错误信息记录
- 优雅的异常处理

## 注意事项

1. **合规使用**：请遵守网站的robots.txt和使用条款
2. **请求频率**：建议设置合理的请求间隔，避免对服务器造成压力
3. **数据使用**：下载的内容仅供个人学习使用，请勿用于商业用途
4. **版权声明**：请尊重原作者的版权，合理使用下载的内容

## 开发计划

- [ ] 添加GUI界面
- [ ] 支持更多文件格式
- [ ] 增加下载队列管理
- [ ] 添加数据库存储支持
- [ ] 实现分布式爬取

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交GitHub Issue
- 发送邮件至：[your-email@example.com]

---

**免责声明**：本工具仅供学习和研究使用，使用者需自行承担使用风险，并遵守相关法律法规。