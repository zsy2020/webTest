"""
yaml处理类，根据yaml的格式执行browser定义的操作
"""
import time

from src.common import webConfig
from src.common.log import logger
from src.common.webConfig import WebConfig
from src.web.util.browser import Browser
from src.web.util.file_handler import YamlReader, find_file


class YamlHandler:
    def __init__(self):
        self.scenarios = None
        self.browser = None
        self.case = {}
        self.imgs = []
        self.success_img = []

    def getFirstCaseName(self):
        for key in self.scenarios.keys():
            return key

    def setCase(self, case_name=None):
        if case_name is None:
            case_name = self.getFirstCaseName()
        case = self.scenarios.get(case_name)
        case['case-name'] = case_name
        self.case = case

    def getCaseName(self):
        return self.case.get('case-name')

    def getRequests(self):
        return self.case.get('requests')

    def doAction(self, action):
        msg = ''
        time.sleep(0.5)
        if isinstance(action, dict):
            action_keys = action.keys()
            for key in action_keys:
                value = action.get(key)
                msg = self.browser.get(getFunc(key), getIndex(key), value)
        else:
            msg = self.browser.get(getFunc(action), getIndex(action))
        return msg

    def openDefaultBrowser(self):
        self.browser = Browser(webConfig.WebConfig.driver_type)
        self.browser.go(webConfig.WebConfig.url)
        return self.browser

    def run(self, yaml_name=webConfig.LOGIN_SUCCESS, case_name=None):
        yaml_path = find_file(WebConfig.yaml_path, yaml_name + '.yaml')
        yaml_data = YamlReader(yaml_path).data
        self.scenarios = yaml_data[0].get('scenarios')
        self.setCase(case_name)
        requests = self.getRequests()

        if self.browser is None:
            self.openDefaultBrowser()

        img = None
        msg = '【%s】场景开始执行' % self.getCaseName()
        print(msg)
        logger.info(msg)
        for request in requests:
            msg = 'label：【%s】' % request.get('label')
            print(msg)
            logger.info(msg)
            for action in request.get('actions'):
                logger.info('action:%s' % action)
                if action == 'getScreenshot()':
                    time.sleep(1)
                    self.success_img.append(self.browser.driver.get_screenshot_as_base64())
                    continue
                try:
                    msg = self.doAction(action)
                    if yaml_name != webConfig.LOGIN_SUCCESS:
                        print(msg)
                    logger.info(msg)
                except Exception as e:
                    print(str(e))
                    logger.error(str(e))
                    img = self.browser.driver.get_screenshot_as_base64()
                    self.imgs.append(img)
                    return False

        result = True if img is None else False
        return result


def getIndex(str_org):
    str_start = '('
    return str_org[str_org.index(str_start) + 1:-1]


def getFunc(str_org):
    str_start = '('
    return str_org[:str_org.index(str_start)]


if __name__ == '__main__':
    YamlHandler().run()
