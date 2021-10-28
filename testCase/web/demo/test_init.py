"""
初始化用例，用来验证init.yaml脚本是否能成功登陆
"""
import unittest

from src.web.common.YamlHandler import YamlHandler


class TestInit(unittest.TestCase):
    def setUp(self):
        self.handler = YamlHandler()
        self.imgs = self.handler.imgs
        self.success_img = self.handler.success_img

    def test(self):
        result = self.handler.run(yaml_name='init')
        self.assertTrue(result)

    def tearDown(self):
        self.handler.browser.quit()


if __name__ == '__main__':
    unittest.main()
