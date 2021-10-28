"""
测试基类，实现了用例开始前执行登录的操作，结束后退出浏览器的操作。测试用例继承该类就默认登录成功后执行该用例
"""
import unittest

from src.common.webConfig import DOWNLOAD_PATH
from src.web.common.YamlHandler import YamlHandler
from src.web.util.file_handler import del_file


class BaseTest(unittest.TestCase):
    handler = None
    imgs = []
    success_img = []

    @classmethod
    def setUpClass(cls):
        print(">>>>>>>>>>>>>>setUpClass>>>>>>>>>>")
        del_file(DOWNLOAD_PATH)
        cls.handler = YamlHandler()
        cls.imgs = cls.handler.imgs
        cls.success_img = cls.handler.success_img
        login_result = cls.handler.run()
        assert login_result

    @classmethod
    def tearDownClass(cls):
        print(">>>>>>>>>>>>>>tearDownClass>>>>>>>>>>")
        cls.handler.browser.quit()
