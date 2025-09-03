#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本 - 秘塔AI搜索课件爬虫工具
用于测试爬虫功能的基本测试用例
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock, Mock

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from metaso_spider import MetasoSpider
from config import DevelopmentConfig


class TestMetasoSpider(unittest.TestCase):
    """秘塔爬虫测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.spider = MetasoSpider()
        self.test_url = "https://metaso.cn/test"
    
    def test_spider_initialization(self):
        """测试爬虫初始化"""
        self.assertIsNotNone(self.spider)
        self.assertIsInstance(self.spider.config, DevelopmentConfig)
    
    def test_url_validation(self):
        """测试URL验证"""
        # 测试有效URL
        valid_url = "https://metaso.cn/course/123"
        self.assertTrue(self.spider._is_valid_metaso_url(valid_url))
        
        # 测试无效URL
        invalid_url = "https://example.com/test"
        self.assertFalse(self.spider._is_valid_metaso_url(invalid_url))
    
    @patch('requests.Session.get')
    def test_get_page_content_success(self, mock_get):
        """测试页面内容获取成功"""
        # 模拟成功响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Test content</body></html>"
        mock_response.raise_for_status.return_value = None
        mock_response.apparent_encoding = 'utf-8'
        mock_get.return_value = mock_response
        
        content = self.spider.get_page_content(self.test_url)
        self.assertIsNotNone(content)
        self.assertIn("Test content", str(content))
    
    @patch('requests.Session.get')
    def test_get_page_content_error(self, mock_get):
        """测试页面获取错误处理"""
        # 模拟请求异常
        import requests
        mock_get.side_effect = requests.RequestException("Network error")
        
        content = self.spider.get_page_content(self.test_url)
        self.assertIsNone(content)
    
    def test_extract_course_info(self):
        """测试课程信息提取"""
        # 模拟HTML内容
        html_content = """
        <html>
            <head><title>测试课程</title></head>
            <body>
                <h1>大语言模型基础</h1>
                <div class="course-content">
                    <img src="/images/test1.jpg" alt="图片1">
                    <a href="/files/test.pdf">下载PDF</a>
                </div>
            </body>
        </html>
        """
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        course_info = self.spider.extract_course_content(soup)
        
        self.assertIsInstance(course_info, dict)
        self.assertIn('title', course_info)
        self.assertIn('preview_images', course_info)
        self.assertIn('download_links', course_info)


class TestConfiguration(unittest.TestCase):
    """配置测试类"""
    
    def test_development_config(self):
        """测试开发环境配置"""
        config = DevelopmentConfig()
        self.assertEqual(config.LOG_LEVEL, "DEBUG")
        self.assertEqual(config.REQUEST_DELAY, 0.5)
        
    def test_directory_paths(self):
        """测试目录路径配置"""
        config = DevelopmentConfig()
        self.assertTrue(os.path.isabs(config.DATA_DIR))
        self.assertTrue(os.path.isabs(config.LOGS_DIR))


def run_tests():
    """运行所有测试"""
    print("开始运行秘塔爬虫测试...")
    print("=" * 50)
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试用例
    test_suite.addTest(unittest.makeSuite(TestMetasoSpider))
    test_suite.addTest(unittest.makeSuite(TestConfiguration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("=" * 50)
    if result.wasSuccessful():
        print("✅ 所有测试通过！")
        return True
    else:
        print("❌ 测试失败！")
        print(f"失败: {len(result.failures)}, 错误: {len(result.errors)}")
        return False


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)