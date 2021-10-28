"""
测试用例列表处理类，根据caseList.txt定义的测试用例列表添加到test_suite
"""
import os
import unittest

from src.common import webConfig


class AllTest:  # 定义一个类AllTest
    def __init__(self):  # 初始化一些参数和数据
        self.reportDir = webConfig.REPORT_PATH  # report/
        self.caseListFile = os.path.join(webConfig.BASE_PATH, "caseList.txt")  # 配置测试用例列表文件路径
        self.caseDir = os.path.join(webConfig.WebConfig.cases_path, "web")  # 测试文件路径
        self.caseList = []

    def set_case_list(self):
        """
        读取caseList.txt文件中的用例名称，并添加到caseList列表
        :return:
        """
        fb = open(self.caseListFile)
        for value in fb.readlines():
            data = str(value).replace("\n", "")  # 读取每行数据会将换行转换为\n，去掉每行数据中的\n
            if data != '' and not data.startswith("#"):  # data非空且不以#开头
                self.appendList(self.caseDir, data)
        fb.close()

    def appendList(self, case_dir, data):
        pre_dir = os.path.join(case_dir, data)
        if os.path.isdir(pre_dir):  # 判断是否为文件夹
            doc_list = os.listdir(pre_dir)  # 列出当前文件夹下所有文件(夹)
            for doc in doc_list:
                if doc.startswith('__init__') or doc.startswith('__pycache__'):  # 文件(夹)名为__init__文件，或者是__pycache__文件夹
                    continue  # 跳过
                self.appendList(pre_dir, doc)  # 递归判断
        else:
            self.caseList.append(data.split(".")[0])  # 截取.py前面的文件名加入到caseList中

    def set_case_suite(self):
        """
        返回一个unittest的测试套
        :return: test_suite
        """
        self.set_case_list()  # 通过set_case_list()拿到caselist元素组
        test_suite = unittest.TestSuite()
        for case in self.caseList:  # 从caselist元素组中循环取出case
            case_name = case.split("/")[-1]  # 通过split函数来将aaa/bbb分割字符串，-1取后面，0取前面
            case_name = case_name + '.py'
            # 批量加载用例，第一个参数为用例存放路径，第一个参数为路径文件名
            discover = unittest.defaultTestLoader.discover(self.caseDir, pattern=case_name)
            if discover.countTestCases() != 0:
                print(case)  # 打印测试用例名
                test_suite.addTest(discover)

        return test_suite  # 返回测试集


if __name__ == '__main__':
    print(AllTest().set_case_suite().countTestCases())
