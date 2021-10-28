"""
定义配置类，读取配置文件中的配置信息包括[HTTP][USER][EMAIL][LOG]
"""
from read_config import get_system, get_email, get_log


class SystemConfig:
    super_name = get_system('super_name')
    super_pwd = get_system('super_pwd')
    username = get_system('username')
    password = get_system('password')
    pass_rate = float(get_system('pass_rate'))
    system_name = get_system('system_name')


class EmailConfig:
    on_off = get_email('on_off')
    title = get_email('title')
    message = get_email('message')
    password = get_email('password')
    receiver = get_email('receiver')
    server = get_email('server')
    sender = get_email('sender')


class LogConfig:
    file_name = get_log('file_name')
    backup = int(get_log('backup'))
    console_level = get_log('console_level')
    file_level = get_log('file_level')
