"""
定义配置文件中不同配置的方法供调用，
"""
import configparser
import os

path = os.path.split(os.path.realpath(__file__))[0]
config_path = os.path.join(path, 'config.ini')
config = configparser.ConfigParser()  # 调用外部的读取配置文件的方法
config.read(config_path, encoding='utf-8')


def get_email(name):
    value = config.get('EMAIL', name)
    return value


def get_system(name):
    value = config.get('SYSTEM', name)
    return value


def get_web(name):
    value = config.get('WEB', name)
    return value


def get_log(name):
    value = config.get('LOG', name)
    return value


def get_path():
    return path


if __name__ == '__main__':  # 测试一下，我们读取配置文件的方法是否可用
    print('测试路径是否OK,路径为：', get_path())
    print('EMAIL中的开关on_off值为：', get_email('on_off'))
    print('SYSTEM中的username值为：', get_system('username'))
    print('WEB中的driver_type值为：', get_web('driver_type'))
    print('LOG中的file_name值为：', get_log('file_name'))
