# -*- coding:utf-8 -*-
import os, configparser
import threading
from Common.log import FrameLog
import pandas as pd
import numpy as np
import inspect
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import smtplib
import traceback
from Config import config as cfg


log = FrameLog().log()

NULL_LIST = [np.nan, np.NaN, " ", "", None, "nan", "NaN", "None", "null", []]


def is_null(tgt):
    """
    查看输入的是不是null
    :param tgt: 输入的string或者unicode
    :return: boolean
    """
    if tgt not in NULL_LIST and not pd.isnull(tgt):
        isnull_res = False
    else:
        isnull_res = True

    return isnull_res


# 多线程重载 run 方法
class MyThread(threading.Thread):

    def __init__(self, func, driver, test_class_list):
        super(MyThread, self).__init__()
        # threading.Thread.__init__(self)
        self.func = func
        self.driver = driver
        self.test_class_list = test_class_list

    def run(self):
        print("Starting " + self.name)
        print("Exiting " + self.name)
        self.func(self.driver, self.test_class_list)


# 获取项目路径
def project_path():
    return os.path.split(os.path.realpath(__file__))[0].split('C')[0]


# 获取当前的'类名/方法名/'(提供截屏路径使用)
def get_current_function_name(class_instance):
    return class_instance.__class__.__name__ + "/" + inspect.stack()[1][3] + "/"


# 获取'config.ini'文件中的（ 获取 [test_url] 下的 baidu_rul 的值
def get_config_ini(key, value):
    config = configparser.ConfigParser()
    config.read(project_path() + "Config/config.ini")
    return config.get(key, value)


# 递归创建目录
def mkdir(path):
    path = path.strip()  # 去除首位空格
    path = path.rstrip("//")  # 去除尾部 / 符号
    is_exists = os.path.exists(path)  # 判断路径是否存在(True存在，False不存在)
    # 判断结果
    if not is_exists:
        os.makedirs(path)
        log.info(path + ' 目录创建成功')
        return True
    else:
        log.info(path + ' 目录已存在')
        return False


def send_mail(subject, content, to_list, attach_file=None):
    """
    [ 发送邮件 ]
    :param subject: 邮件主题
    :param content: 邮件内容
    :param to_list: 邮件发送者列表
    :param attach_file: 附件
    :return:
    """
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = cfg.ERROR_MAIL_ACCOUNT
    msg['To'] = ";".join(to_list)
    msg.attach(MIMEText(content, _subtype='plain', _charset='utf-8'))
    if not is_null(attach_file):
        attach = MIMEText(open(attach_file, 'rb').read(), 'base64', 'utf-8')
        # 指定当前文件格式类型
        attach['Content-type'] = 'application/octet-stream'
        # 配置附件显示的文件名称,当点击下载附件时，默认使用的保存文件的名称
        attach['Content-Disposition'] = "attachment;filename=" + attach_file.split("/")[-1]
        # 把附件添加到msg中
        msg.attach(attach)
    try:
        server = smtplib.SMTP()
        server.connect(host=cfg.ERROR_MAIL_HOST, port=25)
        server.login(cfg.ERROR_MAIL_ACCOUNT, cfg.ERROR_MAIL_PASSWD)
        server.sendmail(cfg.ERROR_MAIL_ACCOUNT, to_list, msg.as_string())
        server.close()
        log.info("邮件发送成功！")
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
        log.error("邮件发送失败！")


if __name__ == "__main__":
    pass
    # attach_file = cfg.REPORTS_PATH + "report.html"
    # send_mail(subject="测试发送", content="测试内容。。。。", to_list=cfg.MAIL_LIST, attach_file=attach_file)

    # print("项目路径：" + project_path())
    # print("被测系统URL：" + get_config_ini("test_url", "ctrip_url"))
    # print()
    # print(os.path.split(os.path.realpath(__file__)))
    # print(os.path.split(os.path.realpath(__file__))[0])
    # print(os.path.split(os.path.realpath(__file__))[0].split('C'))
    # print(os.path.split(os.path.realpath(__file__))[0].split('C')[0])


