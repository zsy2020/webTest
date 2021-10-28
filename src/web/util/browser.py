import os
import sys
import time
from io import BytesIO

import cv2
from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from src.common import webConfig, configInfo
from src.web.util import file_handler

# 自动匹配浏览器配置
CHROME_DRIVER_PATH = webConfig.WebConfig.driver_path + '/chromedriver'
FIREFOX_DRIVER_PATH = webConfig.WebConfig.driver_path + '/geckodriver'
IE_DRIVER_PATH = webConfig.WebConfig.driver_path + '/IEDriverServer'

TYPES = {'firefox', 'chrome', 'ie'}
EXECUTABLE_PATH = {'firefox': FIREFOX_DRIVER_PATH, 'chrome': CHROME_DRIVER_PATH, 'ie': IE_DRIVER_PATH}

# 上传文件脚本路径
UPLOAD_SCRIPT = webConfig.FILE_PATH + '/uploadScript.exe'


def openDefaultBrowser():
    browser = Browser(webConfig.WebConfig.driver_type)
    return browser


class UnSupportBrowserTypeError(Exception):
    pass


class Browser(object):

    def __init__(self, browser_type='chrome'):
        self._type = browser_type.lower()
        self.driver = self.customizeDownload()

        # 设置显式等待时间
        self.driverWait = WebDriverWait(self.driver, webConfig.WebConfig.timeout)
        # 设置隐式等待时间
        self.driver.implicitly_wait(webConfig.WebConfig.timeout)

    def customizeDownload(self):
        """自定义下载路径为download，支持谷歌，火狐，不支持ie"""
        if self._type in TYPES:
            if self._type == 'firefox':
                profile = webdriver.FirefoxProfile()
                profile.set_preference('browser.download.dir', webConfig.DOWNLOAD_PATH)  # 指定下载路径
                profile.set_preference('browser.download.folderList', 2)  # 2:自定义下载路径； 0:下载到桌面； 1:下载到默认路径
                profile.set_preference('browser.download.manager.showWhenStarting', False)  # 在开始下载时是否显示下载管理器
                profile.set_preference('browser.helperApps.neverAsk.saveToDisk',
                                       'application/zip,application/gzip,application/vnd.ms-excel')  # 对所给出文件类型不再弹出框进行询问
                return webdriver.Firefox(executable_path=EXECUTABLE_PATH[self._type])
            elif self._type == 'chrome':
                prefs = {'profile.default_content_settings.popups': 0,  # 禁止弹出窗口
                         'download.default_directory': webConfig.DOWNLOAD_PATH}  # 设置下载位置
                chrome_options = webdriver.ChromeOptions()
                if not webConfig.WebConfig.driver_path.__contains__('windows'):
                    chrome_options.add_argument('--headless')
                    chrome_options.add_argument('--no-sandbox')
                    chrome_options.add_argument('--disable-gpu')
                    chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_experimental_option('prefs', prefs)
                return webdriver.Chrome(executable_path=EXECUTABLE_PATH[self._type], chrome_options=chrome_options)
            else:
                return webdriver.Ie(executable_path=EXECUTABLE_PATH[self._type])
        else:
            raise UnSupportBrowserTypeError('仅支持%s!' % ', '.join(TYPES))

    def get(self, function, *args, **kwargs):
        """方法映射，如传进来function=go，就执行go方法"""
        func = getattr(Browser, function)
        return func(self, *args, **kwargs)

    def go(self, url, maximize_window=True):
        """打开url链接"""
        if not url:
            url = webConfig.WebConfig.url
        self.driver.get(url)
        if maximize_window:
            self.driver.maximize_window()
        return 'do %s url: %s' % (sys._getframe().f_code.co_name, url)

    def findEle(self, value, by=By.XPATH):
        """隐式获取元素"""
        return self.driver.find_element(by, value)

    def findEleUntil(self, value, by=By.XPATH):
        """显式获取元素"""
        return self.driverWait.until(EC.element_to_be_clickable((by, value)),
                                     'Unable to locate element until timeout {"method":"%s","selector":"%s"}' % (
                                         by, value))

    def uploadByName(self, file_dir, file_name):
        """上传文件"""
        pre_dir = os.path.join(webConfig.BASE_PATH, file_dir)
        if file_name == '':
            file_path = file_handler.last_file(pre_dir)
        else:
            file_path = os.path.join(pre_dir, file_name)
        cmd = '{} "{}" "{}"'.format(UPLOAD_SCRIPT, self._type, file_path)
        result = os.system(cmd)  # 使用系统方法导入.exe文件
        if result == 0:
            return 'do upload success file:%s' % file_path
        else:
            raise 'do upload failed file:%s' % file_path

    def writeExcel(self, file_name, data):
        """写入excel"""
        if file_name == '':
            file_path = file_handler.last_file(webConfig.DOWNLOAD_PATH)
        else:
            file_path = os.path.join(webConfig.DOWNLOAD_PATH, file_name)
        file_handler.ExcelHandler(path=file_path).data = data
        return 'write excel success file:{},data:{}'.format(file_path, data)

    def readExcel(self, file_name, data):
        """读取excel"""
        if file_name == '':
            file_path = file_handler.last_file(webConfig.DOWNLOAD_PATH)
        else:
            file_path = os.path.join(webConfig.DOWNLOAD_PATH, file_name)
        actual = file_handler.ExcelHandler(path=file_path, title_line=True).data
        if actual == data:
            return 'read excel success file:{},expect:{},actual:{}'.format(file_path, data, actual)
        else:
            raise Exception('read excel failed file:{},expect:{},actual:{}'.format(file_path, data, actual))

    def clickByXPath(self, xpath, value=None):
        """xpath定位元素，value值为None，执行点击操作，不为None，执行断言"""
        ele = self.findEleUntil(xpath)
        if value is None:
            ele.click()
            return 'do click ByXPath %s' % xpath
        else:
            actual = ele.text
            if actual == value:
                return 'do assert success ByXPath %s: expect=%s, actual=%s' % (xpath, value, actual)
            else:
                raise Exception('do assert failed ByXPath %s: expect=%s, actual=%s' % (xpath, value, actual))

    def assertContainsByCSS(self, css, value):
        ele = self.findEleUntil(css, By.CSS_SELECTOR)
        actual = ele.text
        if actual.__contains__(value):
            return 'do assertContains success ByCSS %s: expect=%s, actual=%s' % (css, value, actual)
        else:
            raise Exception('do assertContains failed ByCSS %s: expect=%s, actual=%s' % (css, value, actual))

    def clickByCSS(self, css, value=None):
        """css定位元素，value值为None，执行点击操作，不为None，执行断言"""
        ele = self.findEleUntil(css, By.CSS_SELECTOR)
        if value is None:
            ele.click()
            return 'do click ByCSS %s' % css
        else:
            time.sleep(1)
            actual = ele.text
            if actual == value:
                return 'do assert success ByCSS %s: expect=%s, actual=%s' % (css, value, actual)
            else:
                raise Exception('do assert failed ByCSS %s: expect=%s, actual=%s' % (css, value, actual))

    def loginAssertByCSS(self, css, value):
        """登录成功校验, css定位的元素文本中是否包含value值"""
        try:
            ele = self.findEleUntil(css, By.CSS_SELECTOR)
        except Exception as e:
            raise Exception('login assert failed %s' % str(e))
        time.sleep(1)
        actual = ele.text
        if actual.__contains__(value):
            return 'login assert success ByCSS %s: expect=%s, actual=%s' % (css, value, actual)
        else:
            raise Exception('login assert failed ByCSS %s: expect=%s, actual=%s' % (css, value, actual))

    def clickByLinkText(self, linkText, value=None):
        """LinkText定位元素，value值为None，执行点击操作，不为None，执行断言"""
        ele = self.findEle(linkText, By.LINK_TEXT)
        if value is None:
            ele.click()
            return 'do click ByLinkText %s' % linkText
        else:
            time.sleep(1)
            actual = ele.text
            if actual == value:
                return 'do assert success ByLinkText %s: expect=%s, actual=%s' % (linkText, value, actual)
            else:
                raise Exception('do assert failed ByLinkText %s: expect=%s, actual=%s' % (linkText, value, actual))

    def typeByXPath(self, xpath, value):
        """输入操作，xpath定位元素"""
        element = self.findEleUntil(xpath)
        self.clear(element)
        if value == 'super_name':
            value = configInfo.SystemConfig.super_name
        if value == 'super_pwd':
            value = configInfo.SystemConfig.super_pwd
        if value == 'username':
            value = configInfo.SystemConfig.username
        if value == 'password':
            value = configInfo.SystemConfig.password
        element.send_keys(value)
        return 'do type ByXPath %s: %s' % (xpath, value)

    def typeByCSS(self, css, value):
        """输入操作，css定位元素"""
        element = self.findEleUntil(css, By.CSS_SELECTOR)
        self.clear(element)
        if value == 'super_name':
            value = configInfo.SystemConfig.super_name
        if value == 'super_pwd':
            value = configInfo.SystemConfig.super_pwd
        if value == 'username':
            value = configInfo.SystemConfig.username
        if value == 'password':
            value = configInfo.SystemConfig.password
        element.send_keys(value)
        return 'do type ByCSS %s: %s' % (css, value)

    def wait(self, time_second):
        """执行强制等待"""
        print('wait time:%s second' % time_second)
        time.sleep(int(time_second))
        return 'wait end'

    def sliderVerify(self, imgCss='div#__Verification > div:nth-child(1)', blockCss='div#xy_img',
                     sliderCss='div.handler.handler_bg', refreshCss='div.refesh_bg'):
        """
        执行滑块验证
        :param imgCss 验证图片的css定位
        :param blockCss 缺口图片的css定位
        :param sliderCss 拖动滑块的css定位
        :param refreshCss 刷新按钮的css定位
        """
        num = 0
        while num < 10:  # 设置重试次数为10
            num += 1
            # 获取验证图片
            self.get_geetest_image(imgCss)
            # 点击呼出缺口图片
            slider = self.findEleUntil(sliderCss, By.CSS_SELECTOR)
            slider.click()
            # 获取缺口图片
            self.get_geetest_image(blockCss, 'block.png')
            # 获取缺口位置坐标
            loc = self.match_image()
            # 拖动滑块
            self.slide_to_gap(sliderCss, loc[0])
            try:
                self.driverWait.until(EC.invisibility_of_element(slider))  # 查看验证图片是否存在
                return 'do sliderVerify 滑块验证成功，执行了%d次' % num  # 不存在即认证成功
            except Exception as e:
                print(e)
            self.findEleUntil(refreshCss, By.CSS_SELECTOR).click()  # 存在，滑块验证失败，刷新重新验证
        return 'do sliderVerify 滑块验证失败，执行了%d次' % num

    def match_image(self):
        """
        图片比对
        :return: max_loc 返回匹配的最大坐标
        """
        block = os.path.join(webConfig.FILE_PATH, 'block.png')
        img = os.path.join(webConfig.FILE_PATH, 'img.png')
        target = cv2.imread(img, 0)
        temple = cv2.imread(block, 0)
        result = cv2.matchTemplate(target, temple, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        # print('min:' + str(min_loc))
        print('max:' + str(max_loc))
        return max_loc

    def slide_to_gap(self, sliderCss, distance):
        """
        拖动滑块到缺口处
        :param sliderCss: 滑块css定位
        :param distance: x方向坐标
        :return:
        """
        slider = self.findEleUntil(sliderCss, By.CSS_SELECTOR)
        ActionChains(self.driver).click_and_hold(slider).perform()
        ActionChains(self.driver).move_by_offset(xoffset=distance, yoffset=0).perform()
        time.sleep(0.5)
        ActionChains(self.driver).release().perform()

    def get_geetest_image(self, imgCss, name='img.png'):
        """
        获取图片并保存,
        :return: 图片对象
        """
        top, bottom, left, right = self.get_position(imgCss)
        screenshot = self.get_screenshot()
        # 从网页截屏图片中裁剪处理验证图片
        captcha = screenshot.crop((left, top, right, bottom))
        file_name = os.path.join(webConfig.FILE_PATH, name)
        captcha.save(file_name)
        return captcha

    def get_position(self, css):
        """
        css定位获取元素位置
        :param css css选择器
        :return: (top, bottom, left, right)
        """
        img = self.findEleUntil(css, By.CSS_SELECTOR)
        location = img.location
        size = img.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
            'width']
        return top, bottom, left, right

    def get_screenshot(self):
        """ 获取网页截图, return: 截图对象 """
        # 浏览器截屏
        screenshot = self.driver.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def refresh(self, tab=None):
        """刷新网页"""
        self.driver.refresh()

    def turnNewPageByCSS(self, css, attr):
        """打开新标签页并且跳转到value"""
        element = self.findEleUntil(css, By.CSS_SELECTOR)
        value = element.get_attribute(attr)
        js = "window.open('{}')".format(value)
        self.driver.execute_script(js)
        self.switchWindow(1)

    def back(self, step):
        """
        网页后退
        :param step 后退次数
        """
        for i in range(0, int(step)):
            self.driver.back()
        return 'back %s step' % step

    def close(self, tab=None):
        """关闭当前窗口"""
        self.driver.close()

    def switchWindow(self, tab):
        """切换标签页"""
        handles = self.driver.window_handles
        self.driver.switch_to.window(handles[int(tab)])

    def quit(self, tab=None):
        """退出浏览器"""
        self.driver.quit()

    def clear(self, element):
        """
        清空输入框的内容,模拟键盘操作：ctrl + a , delete
        :param element 元素对象
        """
        if element.get_attribute('value') != '':
            element.send_keys(Keys.CONTROL, 'a')
            element.send_keys(Keys.DELETE)


if __name__ == '__main__':
    b = Browser()
    msg = b.get("go", "https://www.baidu.com")
    print(msg)
