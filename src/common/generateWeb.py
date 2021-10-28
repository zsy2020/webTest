import os

from src.common import webConfig


class MyTools:
    @staticmethod
    def MakeClass(className, filepath, yaml_name):
        """
            自动生成测试用例类
        :param className: 类名字符串
        :param filepath: 生成用例路径
        :param yaml_name: yaml脚本名称 如:login
        :return:
        """
        lines = [
            "import unittest",
            "from src.web.common.BaseYamlTest import BaseTest",
            "\n\nclass {0}(BaseTest)".format(className) + ":",
            "\tdef test(self):"
        ]
        lines += ["\t\tresult = self.handler.run(yaml_name='{}')".format(yaml_name)]
        lines += ["\t\tself.assertTrue(result)"]
        lines += ["\n\nif __name__ == '__main__':"]
        lines += ["\tunittest.main()"]

        print(lines)
        lines = [i + "\n" for i in lines]
        with open(filepath, "a+", encoding="utf-8") as fp:
            fp.writelines(lines)
            print("类{0}生成成功".format(className))
            pass
        pass


def autoGen(className, caseDir, yamlPath):
    """
    支持批量自动生成测试用例
    """
    if not os.path.exists(yamlPath):
        print('yamlPath:%s is not exist' % yamlPath)
        return
    if not os.path.exists(caseDir):
        os.makedirs(caseDir)
        open("{}\\__init__.py".format(caseDir), 'w').close()
    if os.path.isdir(yamlPath):
        yaml_list = os.listdir(yamlPath)
        for doc in yaml_list:
            doc_path = os.path.join(yamlPath, doc)
            autoGen(className, caseDir, doc_path)
    else:
        yaml_path_split = yamlPath.split('\\')[-1]
        name = yaml_path_split.split('.')[0]
        name = name.replace('-', '_')
        case_path = os.path.join(caseDir, 'test_%s.py' % name)
        MyTools.MakeClass(className, case_path, name)


if __name__ == '__main__':
    path = webConfig.BASE_PATH
    case_dir = os.path.join(path, 'testCase', 'web', 'test')
    yaml_path = os.path.join(path, webConfig.WebConfig.yaml_path)
    autoGen("TestCase", case_dir, yaml_path)
