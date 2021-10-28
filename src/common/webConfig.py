"""
定义web配置。config.ini文件中[WEB]的配置。
"""
import os

import read_config

# 通过当前文件的绝对路径，其父级目录一定是框架的base目录，然后确定各层的绝对路径。如果你的结构不同，可自行修改。
BASE_PATH = read_config.get_path()
DOWNLOAD_PATH = os.path.join(BASE_PATH, 'download')
FILE_PATH = os.path.join(BASE_PATH, 'file')
LOG_PATH = os.path.join(BASE_PATH, 'log')
REPORT_PATH = os.path.join(BASE_PATH, 'report')
SUFFIX = '.xml'
LOGIN_SUCCESS = 'init'


class WebConfig:
    """
    运行测试配置
    """
    # 测试系统名称
    system_name = read_config.get_system('system_name')

    # 测试地址
    url = read_config.get_web('url')

    # 配置浏览器驱动类型(chrome/firefox/ie)
    driver_type = read_config.get_web('driver_type')

    # 超时时间
    timeout = float(read_config.get_web('timeout'))

    # yaml脚本目录
    yaml_path = os.path.join(BASE_PATH, 'script')

    # 操作系统类型（浏览器驱动）
    driver_path = os.path.join(BASE_PATH, 'drivers', read_config.get_web('sys_type'))

    # 通过率
    pass_rate = float(read_config.get_system('pass_rate'))

    # 运行测试用例的目录
    cases_path = os.path.join(BASE_PATH, 'testCase')


if __name__ == '__main__':
    print(WebConfig.timeout)
